from io import BytesIO

from PIL import Image
from flask import Flask
from flask import request
from captcha.my_captche.predict_model import predict_img


__all__ = ['app']
app = Flask(__name__)


@app.route('/')
def index():
    return '<h2>Welcome to Captcha Predict System</h2>'


@app.route('/captcha', methods=['POST'])
def get_captcha():
    images = request.get_data()
    image = Image.open(BytesIO(images))
    fp = BytesIO()
    image.save(fp, format='PNG')
    fp = fp.getvalue()

    images = Image.open(BytesIO(fp))
    yzm = predict_img(images)
    return yzm


if __name__ == '__main__':
    app.run()
