import requests
from PIL import Image
from io import BytesIO
import os

def save_image_from_url(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image.save(save_path)
        print(f"图像已保存到: {save_path}")
    except Exception as e:
        print(f"保存图像时出错：{e}")

# 示例使用
url = "https://i3r.meishichina.com/atta/step/2015/03/17/201503175c828b58324c4ffe.jpg"
save_path = os.path.join(os.getcwd(), "saved_image.jpg")
save_image_from_url(url, save_path)
