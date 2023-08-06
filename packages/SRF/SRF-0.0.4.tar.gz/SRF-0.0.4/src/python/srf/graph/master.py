from typing import Iterable

import numpy as np
import tensorflow as tf

from dxl.learn.core import Graph
from dxl.learn.core.tensor import variable
from dxl.learn.core.utils import logger, map_data
from dxl.learn.model.on_collections import Summation
# from .utils import constant_tensor, variable_tensor


class MasterGraph(Graph):
  class KEYS(Graph.KEYS):
    class TENSOR(Graph.KEYS.TENSOR):
      X = 'x'
      BUFFER = 'x_buffer'
      UPDATE = 'x_update'

    class SUBGRAPH(Graph.KEYS.SUBGRAPH):
      SUMMATION = 'summation'

  def __init__(self, x, nb_workers, graph_info=None, name='master_graph'):
    super().__init__(graph_info=graph_info, name = name)
    self._construct_x(x, nb_workers)
    self._construct_summation()
    self._debug_info()

  def _construct_x(self, x, nb_workers):
    x = variable(self.graph_info.update(name='x'), initializer=x)
    buffer = [
        variable(
            self.graph_info.update(name='buffer_{}'.format(i)),
            shape=x.shape,
            dtype=x.dtype) for i in range(nb_workers)
    ]
    self.tensors[self.KEYS.TENSOR.X] = x
    self.tensors[self.KEYS.TENSOR.BUFFER] = buffer

  def _construct_summation(self):
    sm = self.subgraphs[self.KEYS.SUBGRAPH.SUMMATION] = Summation(
        'summation', self.graph_info.update(name=None))
    x_s = sm(self.tensor(self.KEYS.TENSOR.BUFFER))
    x_u = self.tensor(self.KEYS.TENSOR.X).assign(x_s)
    self.tensors[self.KEYS.TENSOR.UPDATE] = x_u
    return x_u

  def _debug_info(self):
    logger.debug('Master graph constructed.')
    logger.debug('X: {}'.format(self.tensor(self.KEYS.TENSOR.X).data))
    logger.debug('BUFFER: {}'.format(
        list(map(lambda t: t.data, self.tensor(self.KEYS.TENSOR.BUFFER)))))
    logger.debug('UPDATE: {}'.format(
        self.tensor(self.KEYS.TENSOR.UPDATE).data))
