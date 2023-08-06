import json
import h5py
import time
import logging
import numpy as np

from tqdm import tqdm

from dxl.learn.core import Barrier, make_distribute_session
from dxl.learn.core import Master, Barrier, ThisHost, ThisSession, Tensor

from .master import MasterGraph
from .worker import WorkerGraphToR
from ...services.utils import print_tensor, debug_tensor
from ...preprocess.preprocess import preprocess as preprocess_tor
from ...preprocess.preprocess import cut_lors
# from ..task.configure import IterativeTaskConfig

# from ...task.data import ImageInfo, LorsInfo, OsemInfo, TorInfo
from .reconstruction_task import ReconstructionTaskBase
from dxl.data.io import load_array

import logging
logging.basicConfig(
    format='[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)
logger = logging.getLogger('srf')
# sample_reconstruction_config = {
#     'grid': [150, 150, 150],
#     'center': [0., 0., 0.],
#     'size': [150., 150., 150.],
#     'map_file': './debug/map.npy',
#     'x_lor_files': './debug/xlors.npy',
#     'y_lor_files': './debug/ylors.npy',
#     'z_lor_files': './debug/zlors.npy',
#     'x_lor_shapes': [100, 6],
#     'y_lor_shapes': [200, 6],
#     'z_lor_shapes': [300, 6],
#     'lor_ranges': None,
#     'lor_steps': None,
# }


# tor_config = {
#     'grid': [150, 150, 150],
#     'center': [0., 0., 0.],
#     'size': [150., 150., 150.],
#     'map_file': './debug/map.npy',
#     'lor_file': './debug/lors.npy',
#     'num_iteration': 10,
#     'num_subsets': 10,
#     'lor_ranges': None,
#     'lor_steps': None,
# }


class ToRReconstructionTask(ReconstructionTaskBase):
    worker_graph_cls = WorkerGraphToR

    class KEYS(ReconstructionTaskBase.KEYS):
        class TENSOR(ReconstructionTaskBase.KEYS.TENSOR):
            LORS = WorkerGraphToR.KEYS.TENSOR.LORS
            EFFICIENCY_MAP = WorkerGraphToR.KEYS.TENSOR.EFFICIENCY_MAP

        class CONFIG(ReconstructionTaskBase.KEYS.CONFIG):
            GAUSSIAN_FACTOR = 'gaussian_factor'
            C_FACTOR = 'c_factor'

    @classmethod
    def default_config(self):
        result = super().default_config()
        result.update({
            self.KEYS.CONFIG.GAUSSIAN_FACTOR: 2.35482005,
            self.KEYS.CONFIG.C_FACTOR: 0.15
        })
        return result

    @classmethod
    def parse_task(cls, task_spec):
        result = super().parse_task(task_spec)

        # TODO: move to where these configs were used.
        limit = result['tof']['tof_res'] * result['tor']['c_factor'] / \
            result['tor']['gaussian_factor'] * 3
        result['tof']['tof_sigma2'] = limit * limit * 9
        result['tof']['tof_bin'] = result['tof']['tof_bin'] * \
            result['tor']['c_factor']
        # ts = task_spec
        # ii = ts.image.to_dict()
        return result
        self.image_info = ImageInfo(ii['grid'],
                                    ii['center'],
                                    ii['size'],
                                    ii['name'],
                                    ii['map_file'])
        self.kernel_width = ts.tor.kernel_width

        oi = ts.osem.to_dict()
        self.osem_info = OsemInfo(oi['nb_iterations'],
                                  oi['nb_subsets'],
                                  oi['save_interval'])

        self.lors_file = ts.lors.path_file
        tofi = ts.tof.to_dict()
        self.tof_info = TorInfo(tofi['tof_res'],
                                tofi['tof_bin'])
        XYZ = ['x', 'y', 'z']
        self.lors_info = LorsInfo(
            {a: self.lors_file for a in XYZ},
            {a: ts.lors.shape[a] for a in XYZ},
            {a: ts.lors.step[a] for a in XYZ},
            None
        )
        # self.lor_info = LorInfo(
        #     {a: ti['{}_lor_files'.format(a)]
        #      for a in ['x', 'y', 'z']},
        #     {a: ti['{}_lor_shapes'.format(a)]
        #      for a in ['x', 'y', 'z']}, ti['lor_ranges'], ti['lor_steps'])
        limit = ts.tof.tof_res * ts.tor.c_factor / ts.tor.gaussian_factor * 3
        self.tof_sigma2 = limit * limit / 9
        self.tof_bin = self.tof_info.tof_bin * self.c_factor

    def load_local_data(self, key):
        if key == self.KEYS.TENSOR.LORS:
            c = self.config('lors')
            result = {}
            for a in WorkerGraphToR.AXIS:
                tid = self.config('task_index')
                nb_lors = c['shapes'][a][0]
                spec = {
                    'path_file': c['path_file'],
                    'path_dataset': "{}/{}".format(c['path_dataset'], a),
                    'slices': "[{}:{},:]".format(tid * nb_lors, (tid + 1) * nb_lors)
                }
                result[a] = load_array(spec).astype(np.float32)
            return result
        return super().load_local_data(key)
    # def create_master_graph(self):
    #     x = np.ones(self.image_info.grid, dtype=np.float32)
    #     mg = MasterGraph(x, self.nb_workers(), self.ginfo_master())
    #     self.add_master_graph(mg)
    #     logger.info("Global graph created.")
    #     return mg

    def _make_worker_graphs(self):
        KS, KT = self.KEYS.SUBGRAPH, self.KEYS.TENSOR

        if not ThisHost.is_master():
            self.subgraphs[self.KEYS.SUBGRAPH.WORKER] = [
                None for i in range(self.nb_workers)]
            mg = self.subgraph(KS.MASTER)
            KT = self.KEYS.TENSOR
            MKT = mg.KEYS.TENSOR
            inputs = {
                KT.EFFICIENCY_MAP: self.load_local_data(KT.EFFICIENCY_MAP),
                KT.LORS: self.load_local_data(KT.LORS)
            }
    #                 self.master_graph,
    #                 self.kernel_width,
    #                 self.image_info,
    #                 self.tof_bin,
    #                 self.tof_sigma2,
    #                 self.lors_info,
    #                 i,
    #                 self.ginfo_worker(i),
            wg = WorkerGraphToR(mg.tensor(MKT.X), mg.tensor(MKT.BUFFER)[self.task_index], mg.tensor(MKT.SUBSET),
                                inputs=inputs, task_index=self.task_index, name=self.name / 'worker_{}'.format(self.task_index))
            self.subgraphs[KS.WORKER][self.task_index] = wg
            logger.info("Worker graph {} created.".format(self.task_index))
        else:
            logger.info("Skip make worker graph in master process.")
    # def _make_worker_graphs(self):
    #     for i in range(self.nb_workers()):
    #         logger.info("Creating local graph for worker {}...".format(i))
    #         self.add_worker_graph(
    #
    #             ))
    #     logger.info("All local graph created.")
    #     return self.worker_graphs

    # def bind_local_data(self):
    #     """
    #     bind the static effmap data
    #     """
    #     map_file = self.work_directory + self.image_info.map_file
    #     task_index = ThisHost.host().task_index
    #     if ThisHost.is_master():
    #         logger.info("On Master node, skip bind local data.")
    #         return
    #     else:
    #         logger.info(
    #             "On Worker node, local data for worker {}.".format(task_index))
    #         emap = self.load_effmap(map_file)
    #         self.worker_graphs[task_index].init_efficiency_map(emap)
    #     self.bind_local_lors()

    # def bind_local_lors(self, task_index=None):
    #     if task_index is None:
    #         task_index = ThisHost.host().task_index
    #     if ThisHost.is_master():
    #         logger.info("On Master node, skip bind local data.")
    #         return
    #     else:
    #         logger.info(
    #             "On Worker node, local data for worker {}.".format(task_index))

    #         worker_lors = self.load_local_lors(task_index)
    #         # emap = self.load_effmap(map_file)
    #         # self.worker_graphs[task_index].assign_efficiency_map(emap)
    #         self.worker_graphs[task_index].assign_lors(worker_lors,
    #                                                    self.osem_info.nb_subsets)

    def make_steps(self):
        KS = self.KEYS.STEPS
        self._make_init_step(KS.INIT)
        self._make_recon_step(KS.RECON)
        self._make_merge_step(KS.MERGE)
        # assign_step = self._make_assign_step()
        # self.steps = {
        #     KS.INIT: init_step,
        #     KS.RECON: recon_step,
        #     KS.MERGE: merge_step,
        #     # KS.ASSIGN: assign_step
        # }

    def _make_init_step(self, name='init'):
        init_barrier = Barrier(name, self.hosts, [self.master_host],
                               [[g.tensor(g.KEYS.TENSOR.INIT)]
                                for g in self.worker_graphs])
        master_op = init_barrier.barrier(self.master_host)
        worker_ops = [init_barrier.barrier(h) for h in self.hosts]
        self.add_step(name, master_op, worker_ops)
        return name

    # def _make_assign_step(self, name='assign'):
    #     assigns = [[g.tensor(g.KEYS.TENSOR.ASSIGN_LORS)]
    #                for g in self.worker_graphs]
    #     assign_lors_barrier = Barrier(
    #         name, self.hosts, [self.master_host], assigns)
    #     master_op = assign_lors_barrier.barrier(self.master_host)
    #     worker_ops = [assign_lors_barrier.barriers(h) for h in self.hosts]
    #     self.add_step(name, master_op, worker_ops)
    #     return name

    def _make_recon_step(self, name='recon'):
        recons = [[g.tensor(g.KEYS.TENSOR.UPDATE)] for g in self.worker_graphs]
        calculate_barrier = Barrier(
            name, self.hosts, [self.master_host], task_lists=recons)
        master_op = calculate_barrier.barrier(self.master_host)
        worker_ops = [calculate_barrier.barrier(h) for h in self.hosts]
        self.add_step(name, master_op, worker_ops)
        return name

    def _make_merge_step(self, name='merge'):
        """
        """
        merge_op = self.master_graph.tensor(
            self.master_graph.KEYS.TENSOR.UPDATE)
        merge_barrier = Barrier(
            name, [self.master_host], self.hosts, [[merge_op]])
        master_op = merge_barrier.barrier(self.master_host)
        worker_ops = [merge_barrier.barrier(h) for h in self.hosts]
        self.add_step(name, master_op, worker_ops)
        return name

    # def _assign_lors(self, subset_index):
    #     if ThisHost.is_master():
    #         pass
    #     else:
    #         task_index = ThisHost.host().task
    #         this_worker = self.worker_graphs[task_index]
    #         ThisSession.run(this_worker.tensor(
    #             this_worker.KEYS.TENSOR.ASSIGN_LORS)[subset_index].data)

    # def run(self):
    #     KS = self.KEYS.STEPS
    #     self.run_step_of_this_host(KS.INIT)
    #     logger.info('STEP: {} done.'.format(KS.INIT))

    #     nb_iterations = self.osem_info.nb_iterations
    #     nb_subsets = self.osem_info.nb_subsets
    #     image_name = self.image_info.name
    #     for i in tqdm(range(nb_iterations), ascii=True):
    #         for j in tqdm(range(nb_subsets), ascii=True):
    #             print("start assign lors !!!!!!!")
    #             self._assign_lors(j)
    #             logger.info('STEP: {} {} done.'.format('assign', j))

    #             self.run_step_of_this_host(KS.RECON)
    #             logger.info('STEP: {} done.'.format(KS.RECON))

    #             self.run_step_of_this_host(KS.MERGE)
    #             logger.info('STEP: {} done.'.format(KS.MERGE))

    #             self.run_and_print_if_not_master(
    #                 self.worker_graphs[ThisHost.host().task].tensor(
    #                     self.worker_graphs[0].KEYS.TENSOR.RESULT)
    #             )
    #             self.run_and_print_if_is_master(
    #                 self.master_graph.tensor('x')
    #             )
    #             # self.run_and_print_if_not_master(
    #             #     self.worker_graphs[ThisHost.host().task].tensor(self.worker_graphs[0].KEYS.TENSOR.EFFICIENCY_MAP)
    #             # )

    #             self.run_and_save_if_is_master(
    #                 self.master_graph.tensor('x'),
    #                 image_name + '_{}_{}.npy'.format(i, j))

    #     logger.info('Recon {} steps {} subsets done.'.format(
    #         nb_iterations, nb_subsets))

    # def run_and_save_if_is_master(self, x, path):
    #     if ThisHost.is_master():
    #         if isinstance(x, Tensor):
    #             x = x.data
    #         result = ThisSession.run(x)
    #         np.save(path, result)

    # def run_and_print_if_not_master(self, x):
    #     if not ThisHost.is_master():
    #         if isinstance(x, Tensor):
    #             x = x.data
    #         result = ThisSession.run(x)
    #         print(result)

    # def run_and_print_if_is_master(self, x):
    #     if ThisHost.is_master():
    #         if isinstance(x, Tensor):
    #             x = x.data
    #         result = ThisSession.run(x)
    #         print(result)

    # def load_data(self, file_name, lor_range=None):
    #     if file_name.endswith('.npy'):
    #         data = np.load(file_name, 'r')
    #         if lor_range is not None:
    #             data = data[lor_range[0]:lor_range[1], :]
    #     elif file_name.endswith('.h5'):
    #         with h5py.File(file_name, 'r') as fin:
    #             if lor_range is not None:
    #                 data = np.array(fin['data'][lor_range[0]:lor_range[1], :])
    #             else:
    #                 data = np.array(fin['data'])
    #     return data

    # def load_local_lors_data(self, path_file, axis, lor_range):
    #     with h5py.File(path_file, 'r') as fin:
    #         lors3 = fin['lors']
    #         lor = lors3[axis]
    #         return np.array(lor[lor_range[0]: lor_range[1], ...])

    # # Load datas
    # def load_local_lors(self, task_index: int):
    #     lors = {}
    #     NS = self.osem_info.nb_subsets
    #     LI = self.lors_info
    #     axis = {'x', 'y', 'z'}
    #     print("Lors_info:!!!!!!!!!!", LI)
    #     print("Lors_info:!!!!!!!!!!", LI.lors_files('x'))
    #     # load the range of lors to the corresponding workers.
    #     worker_step = {a: LI.lors_steps(a) * NS for a in axis}
    #     print(worker_step)
    #     # print("!!!!!!!!!!!!!", task_index)
    #     lors_ranges = {a: [task_index * worker_step[a],
    #                        (task_index + 1) * worker_step[a]] for a in axis}

    #     for a in ['x', 'y', 'z']:
    #         msg = "Loading {} LORs from file: {}, with range: {}..."
    #         logger.info(msg.format(
    #             a, LI.lors_files(a), lors_ranges[a]))
    #         # lors[a] = self.load_data(
    #         #     LI.lors_files(a), lors_ranges[a])
    #         lors[a] = self.load_local_lors_data(
    #             LI.lors_files(a), a, lors_ranges[a])
    #     logger.info('Loading local data done.')
    #     return lors

    # def load_effmap(self, map_file: str):
    #     logger.info("Loading efficiency map from file: {}...".format(map_file))
    #     emap = self.load_data(map_file)
    #     return emap
