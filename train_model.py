
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Convolution2D, Flatten, Dropout, MaxPool2D, Dense, Activation, BatchNormalization, Conv2D
from keras.optimizers import Adam
from PIL import Image
import os
from keras import regularizers


import string
# 验证码字母和数字的字符串
CHRS = string.ascii_lowercase + string.digits

num_classes = 36
batch_size = 32
epochs = 15

img_path = os.getcwd() + '/train_pictures/'

x_train = []
y_label = []
img_cols, img_rows = 22, 12

input_shape = (img_cols, img_rows, 1)

for file_name in os.listdir(img_path):
    image = Image.open(img_path + file_name)
    # 将所有 pixel 映射到 lambda 函数上，放回一个只含 True, False 的图像矩阵
    im = image.point(lambda x: x != 43, mode='1')
    # 切割单个字符 y 轴的坐标上下限
    y_upper, y_lower = 0, 22
    # 切割单个字符 x 轴的坐标
    split_line = [5, 17, 29, 41, 53]
    # 将验证码切割成四个区域（crop 函数接受图像的左上，右下四个坐标，返回这个区域的图像）
    ims = [im.crop([left, y_upper, right, y_lower]) for left, right in zip(split_line[:-1], split_line[1:])]

    # 获取图像标签
    img_name = file_name.split('.')[0]

    for i, im in enumerate(ims):
        # 将 True, False 矩阵转换为浮点矩阵
        im_array = 1.0 * np.array(im)
        # 获取图像的矩阵形状，维度从高到低，此时为（22, 12）
        img_rows, img_cols = np.shape(im)
        # 为了能将图片输入训练，改变图片形状
        im_array = im_array.reshape(img_rows, img_cols, 1)
        # 将 单个验证码像素矩阵 存入训练集列表
        x_train.append(im_array)
        # 将 单个验证码 在字符串中的索引作为标签，存入训练标签集
        y_label.append(CHRS.index(img_name[i]))

X = np.stack(x_train)
Y = np.stack(y_label)
Y = keras.utils.np_utils.to_categorical(Y, num_classes)

split_point = 3500
x_train, y_train, x_test, y_test = X[:split_point], Y[:split_point], X[split_point:], Y[split_point:]

# keras序贯模型，不分叉
model = Sequential()
# 卷积层1，个数32，尺寸3*3，填充方式valid，步长默认1*1
model.add(Convolution2D(
    filters=32,
    kernel_size=(3, 3),
    padding='valid',
    input_shape=input_shape,
    name='conv2d_1'
))
# 批规范化处理
model.add(BatchNormalization())
# 激活函数relu
model.add(Activation('relu', name='activation_1'))
# 卷积层2，个数32，尺寸3*3，填充方式valid，步长默认1*1
model.add(Convolution2D(
    filters=32,
    kernel_size=(3, 3),
    name='conv2d_2'
))
model.add(BatchNormalization())
model.add(Activation('relu', name='activation_2'))

# 池化层，尺寸2*2，步长为2*2，填充方式为valid
model.add(MaxPool2D(
    pool_size=(2, 2),
    strides=(2, 2),
    padding='valid',
    name='max_pooling2d_1'
))
model.add(Dropout(0.25))
# 转化为一维矩阵
model.add(Flatten(name='flatten_1'))
# 全连接层，128个神经元
model.add(Dense(128, name='dense_1'))
model.add(BatchNormalization())
model.add(Activation('relu', name='activation_3'))

# 分类层，L2正则优化
model.add(Dense(num_classes,
                kernel_regularizer=regularizers.l2(0.01),
                name='dense_2'))
# 分类层，激活函数sofomax
model.add(Activation('softmax', name='activation_4'))

# 自适应学习率的算法adam
adam = Adam(lr=0.001)

# 配置模型，优化器为adam，损失函数为，指标为准确率
model.compile(
    optimizer=adam,
    loss=keras.losses.categorical_crossentropy,
    metrics=['accuracy'],
)

# 拟合模型
model.fit(
    x=x_train,
    y=y_train,
    epochs=epochs,
    validation_split=0.33,
    batch_size=batch_size,
    validation_data=(x_test, y_test)
)
model.save('test1.h5')