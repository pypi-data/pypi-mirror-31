import mxnet as mx
import copy
import numpy as np
import six
from functools import wraps
from contextlib import contextmanager

from .backend_base import BackendBase, DeviceDecorator

name_id = 0
def get_name(prefix="name"):
    global name_id
    name = "%s-%s" % (prefix, name_id)
    name_id += 1
    return name

class MXNetSession(object):

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def _run(self, vals, feed_dict):
        if isinstance(vals, list):
            return [self._run(v, feed_dict=feed_dict) for v in vals]
        if isinstance(vals, mx.ndarray.NDArray):
            return vals.asnumpy()
        return vals.bind(mx.cpu(), args=feed_dict).forward(is_train=True)[0].asnumpy()

    def coerce_val(self, val):
        if isinstance(val, float) or isinstance(val, int):
            return [val]
        return val

    def run(self, vals, feed_dict=[]):
        feed_dict = {a.name:mx.symbol.array(self.coerce_val(b)) for a,b in feed_dict}
        return self._run(vals, feed_dict)


@six.add_metaclass(DeviceDecorator)
class MXNetBackend(BackendBase):

    def __init__(self, **kwargs):
        super(MXNetBackend, self).__init__(**kwargs)
        self.core = mx

    # General purpose methods

    @classmethod
    def use_device(cls, method):
        @wraps(method)
        def func(self, *args, **kwargs):
            with mx.Context(self.get_current_device()):
                result = method(self, *args, **kwargs)
            return result
        return func

    def cpu(self, id=0):
        return mx.cpu(id)

    def gpu(self, id=0):
        return mx.gpu(id)

    def _placeholder(self, dtype=None, shape=None, name=None):
        name = get_name('placeholder')
        with self._device(self.get_current_device()):
            return mx.symbol.Variable(name, dtype=dtype, shape=shape)

    def _variable(self, initial_value=None, trainable=True, name=None):
        with self._device(self.get_current_device()):
            return mx.symbol.array(initial_value)

    def _device(self, name):
        return mx.Context(name)

    def create_session(self, **kwargs):
        sess = MXNetSession()
        return sess

    @contextmanager
    def session(self, **kwargs):
        with MXNetSession() as sess:
            self._sessions.append(sess)
            self._initialize(sess)
            yield sess
            self._sessions.pop()

    def interactive_session(self, **kwargs):
        return self.create_session(**kwargs)

    def get_current_session(self):
        if len(self._sessions) == 0:
            raise Exception('No current session')
        return self._sessions[-1]

    def _initialize(self, sess):
        pass

    # Unified interface


    def cast(self, x, dtype):
        return x.astype(dtype)

    def dtype(self, x):
        return x.dtype

    def shape(self, x):
        return x.infer_shape_partial()[1][0]

    def rank(self, x):
        return len(self.shape(x))

    def abs(self, x):
        return x.abs()

    def set_value(self, x, value):
        x[:] = value

    def zeros(self, shape, dtype=None, name=None):
        dtype = dtype or self.floatx()
        return mx.symbol.zeros(shape, dtype=dtype, name=name)

    def zeros_like(self, x, dtype=None, name=None):
        return mx.symbol.zeros_like(x, dtype=dtype, name=name)

    def ones(self, shape, dtype=None, name=None):
        dtype = dtype or self.floatx()
        return mx.symbol.ones(shape, dtype=dtype, name=name)

    def ones_like(self, x, dtype=None, name=None):
        return mx.symbol.ones_like(x, dtype=dtype, name=name)

    def random_normal(self, shape, mean=0.0, stddev=1.0, dtype=None, seed=None):
        dtype = dtype or self.floatx()
        return mx.symbol.random_normal(shape=shape, loc=mean, scale=stddev, dtype=dtype)

    def random_truncated_normal(self, shape, mean=0.0, stddev=1.0, dtype=None, seed=None):
        raise NotImplementedError

    def random_uniform(self, shape, minval=0, maxval=None, dtype=None, seed=None):
        dtype = dtype or self.floatx()
        if maxval is None: maxval = 1
        return mx.symbol.random_uniform(shape=shape, low=minval, high=maxval, dtype=dtype)

    def random_binomial(self, shape, p=0.5, dtype=None):
        raise NotImplementedError

    def random_gamma(self, shape, alpha, beta=None):
        beta = beta or 1
        return mx.symbol.random_gamma(shape=shape, alpha=alpha, beta=beta)

    def tanh(self, x, name=None):
        return mx.symbol.tanh(x, name=name)

    def sigmoid(self, x, name=None):
        return mx.symbol.sigmoid(x, name=name)

    def relu(self, x, alpha=0., name=None):
        return mx.symbol.relu(x, name=name)

    def softmax(self, x, T=1.0):
        return mx.symbol.softmax(x)

    def dropout(self, x, p, seed=None):
        return (self.random_uniform(self.shape(x)) > p) * x

    def conv2d(self, x, kernel, strides=(1, 1), border_mode='same',
               image_shape=None, filter_shape=None):
        '''
        Run on cuDNN if available.
        border_mode: string, "same" or "valid".
        dim_ordering: whether to use Theano or TensorFlow dimension ordering
        in inputs/kernels/ouputs.
        '''
        if border_mode == 'same':
            padding = 'SAME'
        elif border_mode == 'valid':
            padding = 'VALID'
        else:
            raise Exception('Invalid border mode: ' + str(border_mode))

        strides = (1,) + strides + (1,)

        if self.floatx() == 'float64':
            x = tf.cast(x, 'float32')
            kernel = tf.cast(kernel, 'float32')

        x = tf.nn.conv2d(x, kernel, strides, padding=padding)

        if self.floatx() == 'float64':
            x = tf.cast(x, 'float64')
        return x

    def pool2d(self, x, pool_size, strides=(1, 1),
               border_mode='valid', pool_mode='max'):
        '''
        pool_size: tuple of 2 integers.
        strides: tuple of 2 integers.
        border_mode: one of "valid", "same".
        dim_ordering: one of "th", "tf".
        '''
        if border_mode == 'same':
            padding = 'SAME'
        elif border_mode == 'valid':
            padding = 'VALID'
        else:
            raise Exception('Invalid border mode: ' + str(border_mode))

        strides = (1,) + strides + (1,)
        pool_size = (1,) + pool_size + (1,)

        if self.floatx() == 'float64':
            x = tf.cast(x, 'float32')

        if pool_mode == 'max':
            x = tf.nn.max_pool(x, pool_size, strides, padding=padding)
        elif pool_mode == 'avg':
            x = tf.nn.avg_pool(x, pool_size, strides, padding=padding)
        else:
            raise Exception('Invalid pooling mode: ' + str(pool_mode))

        if self.floatx() == 'float64':
            x = tf.cast(x, 'float64')
        return x

    def flatten(self, x, leading=1):
        leading_dim = self.shape(x)[:leading]
        new_shape = tf.concat([leading_dim, [-1]], 0)
        return tf.reshape(x, new_shape)

    def split(self, x, num_splits, axis=None):
        axis = axis % len(x.get_shape())
        return tf.split(x, num_splits, axis=axis)

    def reshape(self, x, shape):
        return tf.reshape(x, shape)

    def sum(self, x, axis=None, keepdims=False):
        if x.dtype.base_dtype == tf.bool:
            x = tf.cast(x, self.floatx())
        return tf.reduce_sum(x, axis=axis, keep_dims=keepdims)

    def prod(self, x, axis=None, keepdims=False):
        return tf.reduce_prod(x, axis=axis, keep_dims=keepdims)

    def mean(self, x, axis=None, keepdims=False):
        if axis is not None and axis < 0:
            axis = axis % len(x.get_shape())
        if x.dtype.base_dtype == tf.bool:
            x = tf.cast(x, self.floatx())
        return tf.reduce_mean(x, axis=axis, keep_dims=keepdims)

    def batch_norm(self, x, beta, gamma):
        mean, variance = tf.nn.moments(x, [0])
        normed = tf.nn.batch_normalization(tf.identity(x), mean, variance, beta, gamma, self.epsilon())
        return normed

    def log(self, x):
        return tf.log(x)

    def exp(self, x):
        return tf.exp(x)

    def pow(self, x, a):
        return tf.pow(x, a)

    def sqrt(self, x):
        x = tf.clip_by_value(x,
                             tf.cast(0., dtype=self.floatx()),
                             tf.cast(np.inf, dtype=self.floatx()))
        return tf.sqrt(x)

    def categorical_crossentropy(self, output, target, from_logits=False):
        if not from_logits:
            output /= tf.reduce_sum(output,
                                    axis=len(output.get_shape())-1,
                                    keep_dims=True)
            output = tf.clip_by_value(output, tf.cast(self.epsilon(), dtype=self.floatx()),
                                    tf.cast(1.- self.epsilon(), dtype=self.floatx()))
            return - tf.reduce_sum(target * tf.log(output),
                                   axis=len(output.get_shape()) - 1)
        else:
            return tf.nn.softmax_cross_entropy_with_logits(logits=output, labels=target)

    def concatenate(self, tensors, axis=-1):
        return tf.concat(tensors, axis=axis)

    def sort(self, tensor):
        values, indices = tf.nn.top_k(-tensor, k=tf.shape(tensor)[0])
        return -values, indices

    def argmin(self, tensor, axis=0):
        return tf.argmin(tensor, axis=axis)

    def map(self, function, input):
        return tf.map_fn(function, input)

    def rnn(self, step_function, input, initial_states):
        def step(accumulator, value):
            _, new_accumulator = step_function(value, accumulator)
            return new_accumulator
        result = tf.scan(step, input, initial_states)
        return result

    def while_loop(self, condition, body, loop_vars, **kwargs):
        return tf.while_loop(condition, body, loop_vars)

    def scan(self, fn, elems, initializer=None):
        return tf.scan(fn, elems, initializer=initializer, back_prop=True)

    def logdet(self, A):
        A = (A + self.matrix_transpose(A)) / 2.
        term = tf.log(tf.matrix_diag_part(tf.cholesky(A)))
        return 2 * tf.reduce_sum(term, -1)

    def einsum(self, subscripts, *operands):
        return tf.einsum(subscripts, *operands)

    def cholesky(self, A, lower=True):
        assert lower is True
        return tf.cholesky(A)

    # Tensorflow interface

    def placeholder(self, dtype, shape=None, name=None):
        return self._placeholder(dtype=dtype, shape=shape, name=name)

    def variable(self, initial_value=None, trainable=True, name=None):
        return self._variable(initial_value=initial_value, trainable=trainable, name=name)

    def assign(self, a, b):
        raise NotImplementedError

    def to_float(self, x):
        return self.cast(x, self.floatx())

    def constant(self, value, dtype=None, shape=None):
        raise NotImplementedError

    def get_shape(self, x):
        return self.shape(x)

    def get_value(self, variable):
        return self.get_current_session().run(variable)

    def concat(self, values, axis=-1):
        return tf.concat(values, axis=axis)

    def gather(self, params, indices):
        return tf.gather(params, indices)

    def gather_nd(self, params, indices):
        return tf.gather_nd(params, indices)

    def equal(self, x, y):
        return tf.equal(x, y)

    def logical_and(self, x, y):
        return tf.logical_and(x, y)

    def matmul(self, a, b, transpose_a=False, transpose_b=False, a_is_sparse=False, b_is_sparse=False, name=None):
        return tf.matmul(a, b, transpose_a=transpose_a, transpose_b=transpose_b, a_is_sparse=a_is_sparse, name=name)

    def matrix_transpose(self, a):
        d = self.rank(a)
        return mx.sym.swapaxes(a, d-1, d-2)

    def matrix_diag(self, a):
        return tf.matrix_diag(a)

    def kronecker(self, A, B):
        C = (A[..., None, None] * B[..., None, None, :, :])
        blocks = [
            tf.unstack(a, axis=-3 % len(a.shape)) for a in
            tf.unstack(C, axis=-4 % len(C.shape))
        ]
        return tf.concat([
            tf.concat(a, -1) for a in blocks
        ], -2)

    def lower_triangular(self, a):
        raise NotImplementedError

    def matrix_inverse(self, a):
        raise NotImplementedError

    def expand_dims(self, x, dim=-1):
        return mx.sym.expand_dims(x, dim)

    def tile(self, input, multiples):
        return mx.sym.tile(input, multiples)

    def gradients(self, loss, variables):
        return loss.gradient(variables)

    def square(self, x):
        return tf.square(x)

    def clip_by_value(self, x, low, high):
        return tf.clip_by_value(x, low, high)

    def pack(self, values, axis=0, name='pack'):
        return tf.stack(values, axis=axis, name=name)

    def reduce_max(self, x, axis=None, keep_dims=False):
        return tf.reduce_max(x, axis=axis, keep_dims=keep_dims)

    def reduce_logsumexp(self, x, axis=None, keep_dims=False):
        return tf.reduce_logsumexp(x, axis=axis, keep_dims=keep_dims)

    def matrix_solve(self, matrix, rhs, adjoint=None):
        return tf.matrix_solve(matrix, rhs, adjoint=adjoint)

    # Theano interface

    def dim(self, x):
        return len(x.get_shape())

    def scalar(self, name=None, dtype=None, shape=[]):
        dtype = dtype or self.floatx()
        return self._placeholder(dtype=dtype, shape=shape, name=name)

    def vector(self, name=None, dtype=None, shape=[None]):
        dtype = dtype or self.floatx()
        return self._placeholder(dtype=dtype, shape=shape, name=name)

    def matrix(self, name=None, dtype=None, shape=[None, None]):
        dtype = dtype or self.floatx()
        return self._placeholder(dtype=dtype, shape=shape, name=name)

    def tensor3(self, name=None, dtype=None, shape=[None, None, None]):
        dtype = dtype or self.floatx()
        return self._placeholder(dtype=dtype, shape=shape, name=name)

    def tensor4(self, name=None, dtype=None, shape=[None, None, None, None]):
        dtype = dtype or self.floatx()
        return self._placeholder(dtype=dtype, shape=shape, name=name)

    def shared(self, value, name=None):
        return self._variable(initial_value=value, name=name)

    def arange(self, start, stop=None, step=None):
        return self.range(start, stop=stop, step=step)

    def sparse_dot(self, x, y):
        return tf.sparse_tensor_dense_matmul(x, y)

    def dot(self, x, y):
        return tf.matmul(x, y)

    def outer(self, x, y):
        return x[...,:,None] * y[...,None,:]

    def eye(self, d, batch_shape=None):
        diag = mx.sym.arange(d)
        return mx.sym.one_hot(diag, d)

    def function(self, inputs, outputs, updates=[]):
        raise NotImplementedError

    def grad(self, loss, variables):
        return loss.gradient(variables)

    def sqr(self, x):
        return tf.square(x)

    def argmax(self, x, axis=None):
        return tf.argmax(x, axis=axis)

    def max(self, x, axis=None, keepdims=False):
        return tf.reduce_max(x, axis=axis, keep_dims=keepdims)

    def logsumexp(self, x, axis=None, keepdims=False):
        return tf.reduce_logsumexp(x, axis=axis, keep_dims=keepdims)

    def switch(self, condition, then_expression, else_expression):
        '''Switches between two operations depending on a scalar value (int or bool).
        Note that both `then_expression` and `else_expression`
        should be symbolic tensors of the *same shape*.
        # Arguments
            condition: scalar tensor.
            then_expression: TensorFlow operation.
            else_expression: TensorFlow operation.
        '''
        return tf.where(condition, then_expression, else_expression)

    def alloc(self, value, shape, unbroadcast=None, dtype=None):
        dtype = dtype or self.floatx()
        vals = tf.fill(tf.stack(shape), np.array(value).astype(dtype))
        new_shape = []
        for s in shape:
            if isinstance(s, tf.Tensor):
                new_shape.append(None)
            else:
                new_shape.append(s)
        vals.set_shape(new_shape)
        return vals

    def range(self, start, limit=None, delta=1):
        if limit is None:
            return tf.range(start, delta=delta)
        return tf.range(start, limit, delta=delta)

    def solve(self, a, b):
        return tf.matrix_solve(a, b)

    def one_hot(self, indices, depth):
        return tf.one_hot(indices, depth)

    # Science methods

    def gammaln(self, x):
        return tf.lgamma(x)

    def multigammaln(self, a, p):
        p = self.to_float(p)
        p_ = self.cast(p, 'int32')
        a = a[..., None]
        i = self.to_float(self.range(1, p_ + 1))
        term1 = p * (p - 1) / 4. * self.log(np.pi)
        term2 = self.gammaln(a - (i - 1) / 2.)
        return term1 + self.sum(term2, axis=-1)

    def digamma(self, a):
        return tf.digamma(a)
