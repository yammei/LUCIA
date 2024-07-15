import numpy as np
from method_logger import ML, log
from img_translation import *

class KernelConfig:
    def __init__(self):
        self.weight: float = .1
        self.size: int = 3
        self.num: int = 16
        self.stride: int = 1

def multiply_matrices(matrix_1: np.array, matrix_2: np.array) -> np.ndarray:
    ML.start(func_name='multiply_matrices', args={'matrix_1': type(matrix_1.shape), 'matrix_2': type(matrix_2.shape)})

    matrix_1_col_size = matrix_1.shape[1]
    matrix_2_row_size = matrix_2.shape[0]

    is_size_equal = (matrix_1_col_size == matrix_2_row_size)
    log(f"VARIABLE   is_size_equal = (matrix_1_col_size == matrix_2_row_size) = {is_size_equal}")

    if is_size_equal:
        product = np.matmul(matrix_1, matrix_2)
        ML.end(status=1, return_val=product)
        return product
    elif not is_size_equal:
        ML.end(status=0, return_val=None)
        return None

# Notes: S. Sabyasachi. (2018) Deciding optimal kernel size for CNN. https://towardsdatascience.com/deciding-optimal-filter-size-for-cnns-d6f7b56f9363
def generate_kernels(kernel: dict = KernelConfig()) -> np.ndarray:
    ML.start(func_name='generate_kernels', args={'kernel_weight': type(kernel.weight), 'kernel_size': type(kernel.size), 'kernel_num': type(kernel.num)})

    # Generates kernel.num amount of kernels 3x3 kernels each with 3 channels for RGB, or simply 3x3x3x16.
    kernels = np.random.randn(kernel.size, kernel.size, 3, kernel.num) * kernel.weight
    log(f"VARIABLE   kernels.shape = {kernels.shape}")


    ML.end(status=1, return_val=kernels)
    return kernels


def convolve(rgb_matrix: np.ndarray, kernels: np.ndarray, kernel: dict = KernelConfig()) -> np.ndarray:
    ML.start(func_name='convolve', args={'rgb_matrix': type(rgb_matrix), 'kernels': type(kernels), 'kernel': type(kernel)})

    # Sets feature map metadata.
    input_height, input_width, _ = rgb_matrix.shape
    output_height = (input_height - kernel.size) // kernel.stride + 1
    output_width = (input_width - kernel.size) // kernel.stride + 1
    feature_map: np.ndarray = np.zeros((output_height, output_width, kernel.num))

    for k in range(kernel.num):
        for i in range(0, input_height - kernel.size, kernel.stride):
            for j in range(0, input_height - kernel.size, kernel.stride):
                # Convolution operation fills out feature map width the product of rgb_matrix and kernels @ index k.
                feature_map[i//kernel.stride, j//kernel.stride] = np.sum(rgb_matrix[i:i+kernel.size, j:j+kernel.size, :] * kernels[:, :, :, k])

    # ReLU. Removes negative values.
    feature_map = np.maximum(0, feature_map)

    log(f"VARIABLE   feature_map.shape = {feature_map.shape}")
    ML.end(1, feature_map)
    return feature_map

# Notes: D. Matthew. (2017). Feature extracted by max pooling vs mean pooling. https://stats.stackexchange.com/questions/291451/feature-extracted-by-max-pooling-vs-mean-pooling
def pool(feature_map: np.ndarray, pool_size: int = 2, pool_stride: int = 2, pool_mode: str = 'max', kernel: dict = KernelConfig()) -> np.ndarray:
    ML.start('max_pooling', {'feature_map': type(feature_map), 'pool_size': type(pool_size), 'pool_mode': type(pool_mode)})

    # Sets pooled map metadata.
    input_height, input_width, _ = feature_map.shape
    output_height = (input_height - pool_size) // pool_stride + 1
    output_width = (input_width - pool_size) // pool_stride + 1
    pooled_map: np.ndarray = np.zeros((output_height, output_width, kernel.num))

    for k in range(kernel.num):
        for i in range(input_height - pool_size + 1, pool_stride):
            for j in range(input_width - pool_size + 1, pool_stride):
                # Downsamples feature map by taking max value in a (pool_size x pool_size) sliding window for all feature maps (k).
                pooled_map[i//pool_stride, j//pool_stride] = np.max(feature_map[i:i+pool_size, j:j+pool_size, k])

    log(f"VARIABLE   pooled_map.shape = {pooled_map.shape}")
    ML.end(1, pooled_map)
    return pooled_map

'''
np.random.seed(1)
rand_matrix_1 = np.random.randint(50, 201, size=(6, 7))
rand_matrix_2 = np.random.randint(50, 201, size=(7, 9))
multiply_matrices(matrix_1=rand_matrix_1, matrix_2=rand_matrix_2)
'''

img_path: str = '../images/cat.png'
test_rgb_matrix: np.ndarray = generate_RGB_matrix(img_path)
default_kernels: np.ndarray = generate_kernels()
feature_map = convolve(test_rgb_matrix, default_kernels)
pooled_map = pool(feature_map)