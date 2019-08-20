from keras.models import load_model
import numpy as np
from PIL import Image
import string
import requests
from io import BytesIO
import tensorflow as tf


# 验证码字母和数字的字符串
CHRS = string.ascii_lowercase + string.digits
img_cols, img_rows = 22, 12
input_shape = (img_cols, img_rows, 1)

model = load_model('test1.h5')
graph = tf.get_default_graph()


def predict_img(image):
    # 将所有 pixel 映射到 lambda 函数上，放回一个只含 True, False 的图像矩阵
    im = image.point(lambda x: x != 43, mode='1')
    # 切割单个字符 y 轴的坐标上下限
    y_upper, y_lower = 0, 22
    # 切割单个字符 x 轴的坐标
    split_line = [5, 17, 29, 41, 53]
    # 将验证码切割成四个区域（crop 函数接受图像的左上，右下四个坐标，返回这个区域的图像）
    ims = [im.crop([left, y_upper, right, y_lower]) for left, right in zip(split_line[:-1], split_line[1:])]

    Y = []
    for i, im in enumerate(ims):
        # 将 True, False 矩阵转换为浮点矩阵
        im_array = 1.0 * np.array(im)
        # 获取图像的矩阵形状，维度从高到低，此时为（22, 12）
        img_rows, img_cols = np.shape(im)
        # 为了能将图片输入训练，改变图片形状
        im_array = im_array.reshape(1, img_rows, img_cols, 1)
        # 将 单个验证码像素矩阵 存入训练集列表
        with graph.as_default():
            y_probs = model.predict(im_array)
        y = CHRS[y_probs[0].argmax(-1)]
        Y.append(y)
    return ''.join(Y)


if __name__ == '__main__':

    for i in range(10):
        url = 'http://jwc.gdlgxy.com/CheckCode.aspx'
        req = requests.get(url)

        image = Image.open(BytesIO(req.content))
        fp = BytesIO()
        image.save(fp, format='PNG')
        fp = fp.getvalue()

        images = Image.open(BytesIO(fp))
        print('加载模型成功')
        # img = Image.open('0anp.png')
        yzm = predict_img(images)
        images.save(f'{yzm}.png')
        print(yzm)

