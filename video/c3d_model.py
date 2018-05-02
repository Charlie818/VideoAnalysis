# Copyright 2015 Google Inc. All Rights Reserved.
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

"""Builds the C3D network.

Implements the inference pattern for model building.
inference_c3d(): Builds the model as far as is required for running the network
forward to make predictions.
"""

import tensorflow as tf


class C3DModel(object):
    """"""
    # The UCF-101 dataset has 101 classes
    NUM_CLASSES = 101

    # Images are cropped to (CROP_SIZE, CROP_SIZE)
    CROP_SIZE = 112
    CHANNELS = 3

    # Number of frames per video clip
    NUM_FRAMES_PER_CLIP = 16

    DROPOUT_VALUES = 0.5
    BATCH_SIZE = 16

    def __init__(self, batch_size=16, num_classes=101,test=False):
        """Constructor for C3D"""
        if test:self.DROPOUT_VALUES=1
        self.BATCH_SIZE = batch_size
        self.NUM_CLASSES = num_classes
        with tf.variable_scope('var_name') as var_scope:
            self.weights = {
                'wc1': self._variable_with_weight_decay('wc1', [3, 3, 3, 3, 64], 0.04, 0.00),
                'wc2': self._variable_with_weight_decay('wc2', [3, 3, 3, 64, 128], 0.04, 0.00),
                'wc3a': self._variable_with_weight_decay('wc3a', [3, 3, 3, 128, 256], 0.04, 0.00),
                'wc3b': self._variable_with_weight_decay('wc3b', [3, 3, 3, 256, 256], 0.04, 0.00),
                'wc4a': self._variable_with_weight_decay('wc4a', [3, 3, 3, 256, 512], 0.04, 0.00),
                'wc4b': self._variable_with_weight_decay('wc4b', [3, 3, 3, 512, 512], 0.04, 0.00),
                'wc5a': self._variable_with_weight_decay('wc5a', [3, 3, 3, 512, 512], 0.04, 0.00),
                'wc5b': self._variable_with_weight_decay('wc5b', [3, 3, 3, 512, 512], 0.04, 0.00),
                'wd1': self._variable_with_weight_decay('wd1', [8192, 4096], 0.04, 0.001),
                'wd2': self._variable_with_weight_decay('wd2', [4096, 4096], 0.04, 0.002),
                'out': self._variable_with_weight_decay('wout', [4096, self.NUM_CLASSES], 0.04, 0.005)
            }
            self.biases = {
                'bc1': self._variable_with_weight_decay('bc1', [64], 0.04, 0.0),
                'bc2': self._variable_with_weight_decay('bc2', [128], 0.04, 0.0),
                'bc3a': self._variable_with_weight_decay('bc3a', [256], 0.04, 0.0),
                'bc3b': self._variable_with_weight_decay('bc3b', [256], 0.04, 0.0),
                'bc4a': self._variable_with_weight_decay('bc4a', [512], 0.04, 0.0),
                'bc4b': self._variable_with_weight_decay('bc4b', [512], 0.04, 0.0),
                'bc5a': self._variable_with_weight_decay('bc5a', [512], 0.04, 0.0),
                'bc5b': self._variable_with_weight_decay('bc5b', [512], 0.04, 0.0),
                'bd1': self._variable_with_weight_decay('bd1', [4096], 0.04, 0.0),
                'bd2': self._variable_with_weight_decay('bd2', [4096], 0.04, 0.0),
                'out': self._variable_with_weight_decay('bout', [self.NUM_CLASSES], 0.04, 0.0),
            }

    def placeholder_inputs(self):
        """Generate placeholder variables to represent the input tensors.
        These placeholders are used as inputs by the rest of the model building
        code and will be fed from the downloaded data in the .run() loop, below.
        Args:
          batch_size: The batch size will be baked into both placeholders.
        Returns:
          images_placeholder: Images placeholder.
          labels_placeholder: Labels placeholder.
        """
        # Note that the shapes of the placeholders match the shapes of the full
        # image and label tensors, except the first dimension is now batch_size
        # rather than the full size of the train or test data sets.
        images_placeholder = tf.placeholder(tf.float32, shape=(self.BATCH_SIZE,
                                                               self.NUM_FRAMES_PER_CLIP,
                                                               self.CROP_SIZE,
                                                               self.CROP_SIZE,
                                                               self.CHANNELS))
        labels_placeholder = tf.placeholder(tf.int64, shape=(self.BATCH_SIZE))
        return images_placeholder, labels_placeholder

    def _variable_on_cpu(self, name, shape, initializer):
        # with tf.device('/cpu:%d' % cpu_id):
        with tf.device('/cpu:0'):
            var = tf.get_variable(name, shape, initializer=initializer)
        return var

    def _variable_with_weight_decay(self, name, shape, stddev, wd):
        var = self._variable_on_cpu(name, shape, tf.truncated_normal_initializer(stddev=stddev))
        if wd is not None:
            weight_decay = tf.nn.l2_loss(var) * wd
            tf.add_to_collection('losses', weight_decay)
        return var

    def conv3d(self, name, l_input, w, b):
        return tf.nn.bias_add(
            tf.nn.conv3d(l_input, w, strides=[1, 1, 1, 1, 1], padding='SAME'),
            b
        )

    def max_pool(self, name, l_input, k):
        return tf.nn.max_pool3d(l_input, ksize=[1, k, 2, 2, 1], strides=[1, k, 2, 2, 1], padding='SAME', name=name)

    def inference_c3d(self, _X):
        end_points = {}
        # Convolution Layer
        conv1 = self.conv3d('conv1', _X, self.weights['wc1'], self.biases['bc1'])
        conv1 = tf.nn.relu(conv1, 'relu1')
        pool1 = self.max_pool('pool1', conv1, k=1)

        # Convolution Layer
        conv2 = self.conv3d('conv2', pool1, self.weights['wc2'], self.biases['bc2'])
        conv2 = tf.nn.relu(conv2, 'relu2')
        pool2 = self.max_pool('pool2', conv2, k=2)

        # Convolution Layer
        conv3 = self.conv3d('conv3a', pool2, self.weights['wc3a'], self.biases['bc3a'])
        conv3 = tf.nn.relu(conv3, 'relu3a')
        conv3 = self.conv3d('conv3b', conv3, self.weights['wc3b'], self.biases['bc3b'])
        conv3 = tf.nn.relu(conv3, 'relu3b')
        pool3 = self.max_pool('pool3', conv3, k=2)

        # Convolution Layer
        conv4 = self.conv3d('conv4a', pool3, self.weights['wc4a'], self.biases['bc4a'])
        conv4 = tf.nn.relu(conv4, 'relu4a')
        conv4 = self.conv3d('conv4b', conv4, self.weights['wc4b'], self.biases['bc4b'])
        conv4 = tf.nn.relu(conv4, 'relu4b')
        pool4 = self.max_pool('pool4', conv4, k=2)

        # Convolution Layer
        conv5 = self.conv3d('conv5a', pool4, self.weights['wc5a'], self.biases['bc5a'])
        conv5 = tf.nn.relu(conv5, 'relu5a')
        conv5 = self.conv3d('conv5b', conv5, self.weights['wc5b'], self.biases['bc5b'])
        conv5 = tf.nn.relu(conv5, 'relu5b')
        pool5 = self.max_pool('pool5', conv5, k=2)

        # Fully connected layer
        # pool5 = tf.transpose(pool5, perm=[0, 1, 4, 2, 3])
        dense1 = tf.reshape(pool5, [self.BATCH_SIZE, self.weights['wd1'].get_shape().as_list()[
            0]])  # Reshape conv3 output to fit dense layer input
        dense1 = tf.matmul(dense1, self.weights['wd1']) + self.biases['bd1']

        dense1 = tf.nn.relu(dense1, name='fc1')  # Relu activation
        dense1 = tf.nn.dropout(dense1, self.DROPOUT_VALUES)
        end_points['fc_6']=dense1

        dense2 = tf.nn.relu(tf.matmul(dense1, self.weights['wd2']) + self.biases['bd2'], name='fc2')  # Relu activation
        dense2 = tf.nn.dropout(dense2, self.DROPOUT_VALUES)
        end_points['fc_7'] = dense2
        # Output: class prediction
        out = tf.matmul(dense2, self.weights['out']) + self.biases['out']

        return out, end_points

def main():
    c3d = C3DModel(batch_size=1)
    images_placeholder, labels_placeholder = c3d.placeholder_inputs()
    print(c3d.inference_c3d(images_placeholder))


if __name__ == '__main__':
    main()
