# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Generate tensorflow graphs for testing tfcompile."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.core.protobuf import saver_pb2
from tensorflow.python.client import session
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import variables
from tensorflow.python.platform import app
from tensorflow.python.platform import flags as flags_lib
from tensorflow.python.training import saver as saver_lib

flags = flags_lib
FLAGS = flags.FLAGS
flags.DEFINE_string('out_dir', '',
                    'Output directory for graphs, checkpoints and savers.')


def tfadd():
  x = constant_op.constant([1], name='x_const')
  y = constant_op.constant([2], name='y_const')
  math_ops.add(x, y, name='x_y_sum')


def tfadd_with_ckpt():
  x = array_ops.placeholder(dtypes.int32, name='x_hold')
  y = variables.Variable(constant_op.constant([0]), name='y_saved')
  math_ops.add(x, y, name='x_y_sum')

  init_op = variables.initialize_all_variables()
  saver = saver_lib.Saver(write_version=saver_pb2.SaverDef.V1)
  with session.Session() as sess:
    sess.run(init_op)
    sess.run(y.assign(y + 42))
    # Without the checkpoint, the variable won't be set to 42.
    ckpt = '%s/test_graph_tfadd_with_ckpt.ckpt' % FLAGS.out_dir
    saver.save(sess, ckpt)


def tfadd_with_ckpt_saver():
  x = array_ops.placeholder(dtypes.int32, name='x_hold')
  y = variables.Variable(constant_op.constant([0]), name='y_saved')
  math_ops.add(x, y, name='x_y_sum')

  init_op = variables.initialize_all_variables()
  saver = saver_lib.Saver(name='abcprefix', write_version=saver_pb2.SaverDef.V1)
  with session.Session() as sess:
    sess.run(init_op)
    sess.run(y.assign(y + 42))
    # Without the checkpoint, the variable won't be set to 42.
    ckpt_file = '%s/test_graph_tfadd_with_ckpt_saver.ckpt' % FLAGS.out_dir
    saver.save(sess, ckpt_file)
    # Without the SaverDef, the restore op won't be named correctly.
    saver_file = '%s/test_graph_tfadd_with_ckpt_saver.saver' % FLAGS.out_dir
    with open(saver_file, 'w') as f:
      f.write(saver.as_saver_def().SerializeToString())


def tfgather():
  params = array_ops.placeholder(dtypes.float32, name='params')
  indices = array_ops.placeholder(dtypes.int32, name='indices')
  array_ops.gather(params, indices, name='gather_output')


def tfmatmul():
  x = array_ops.placeholder(dtypes.float32, name='x_hold')
  y = array_ops.placeholder(dtypes.float32, name='y_hold')
  math_ops.matmul(x, y, name='x_y_prod')


def tfmatmulandadd():
  # This tests multiple outputs.
  x = array_ops.placeholder(dtypes.float32, name='x_hold')
  y = array_ops.placeholder(dtypes.float32, name='y_hold')
  math_ops.matmul(x, y, name='x_y_prod')
  math_ops.add(x, y, name='x_y_sum')


def write_graph(build_graph):
  """Build a graph using build_graph and write it out."""
  g = ops.Graph()
  with g.as_default():
    build_graph()
    filename = '%s/test_graph_%s.pb' % (FLAGS.out_dir, build_graph.__name__)
    with open(filename, 'w') as f:
      f.write(g.as_graph_def().SerializeToString())


def main(_):
  write_graph(tfadd)
  write_graph(tfadd_with_ckpt)
  write_graph(tfadd_with_ckpt_saver)
  write_graph(tfgather)
  write_graph(tfmatmul)
  write_graph(tfmatmulandadd)


if __name__ == '__main__':
  app.run()
