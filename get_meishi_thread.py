from bs4 import BeautifulSoup
from PIL import Image
import time, requests, os, sys
from io import BytesIO
from urllib.parse import urljoin
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
import warnings
import yaml


warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

class GetMeiShiThread(QThread):
    image_signal = pyqtSignal(dict)

    def __init__(self, headers, url):
        super().__init__()
        self.headers = headers
        self.url = url.rstrip('/') + '/'
        
        current_directory = os.getcwd()
        self.yaml_path = os.path.join(current_directory, 'imagey.yaml')
        self.image_links = self.read_image_links()
        
        # print(self.image_links)
    
    def read_image_links(self):
        image_links = []
        try:
            with open(self.yaml_path, 'r') as file:
                for line in file:
                    if line.strip():
                        image_links.append(line.strip()[2:])
            os.remove(self.yaml_path)
            return image_links
        except Exception as e:
            print(f"读取image_links.yaml时出错：{e}")
            return []

    def set_food_name(self, food_name):
        self.food_name = food_name

    def get_response(self, url, headers, retry_times, wait_time):
        try_time = 0
        while try_time < retry_times:
            try:
                try_time = try_time + 1
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response
            except Exception as e:
                print(f"URL 获取失败：{url}, 当前尝试次数 {try_time}, 等待时间 {wait_time}s，错误：{e}")
                time.sleep(wait_time)
        return None

    def parse_image(self, image_url):
        dicts = {}
        response = self.get_response(image_url, self.headers, 3, 5)
        if response is None:
            print(f"{image_url}, 图像获取失败，返回空字典！")
            return dicts

        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        img_tag_data = soup.find_all("data-src")

        for img_tag in img_tags:
            img_url = img_tag.get('data-src')
            if img_url is None:
                img_url = img_tag.get('src')
            
            if not img_url or 'avatar' in img_url or 'x-oss-process=style' not in img_url:
                continue

            temp_name = img_url.split('?')[0]
            name = temp_name.split('/')[-1].split('.')[0]
            houzhui = '.jpg' if temp_name.split('.')[-1].startswith('j') else '.png'
            total_name = f"300_{name}{houzhui}"
            dicts[temp_name] = total_name

        return dicts

    def get_image_url(self, url):
        all_links = []
        next_link = ''
        response = self.get_response(url, self.headers, 3, 5)
        if response is None:
            print("结果未获取，结束线程。")
            return all_links, next_link

        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', href=True)

        for tag in a_tags:
            link = tag['href']
            if '下一页' in tag.contents:
                next_link = urljoin(url, link)
                continue
            if 'recipe-' not in link:
                continue
            if not requests.compat.urlparse(link).netloc:
                link = urljoin(url, link)
            all_links.append(link)

        return list(set(all_links)), next_link

    def save_image_from_url(self, url, save_path):
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            image.save(save_path)
            print(f"图像已保存到: {save_path}")
        except Exception as e:
            print(f"保存图像时出错：{e}")

    def test(self):
        save_path = os.path.join(os.getcwd(), "image", self.food_name)
        os.makedirs(save_path, exist_ok=True)

        first_url = self.url + self.food_name
        # print("搜索 URL：", first_url)

        all_links, next_link = self.get_image_url(first_url)
        img_dicts = {}

        while next_link:
            for link in all_links:
                with open(self.yaml_path, 'a') as file:
                    yaml.dump([link], file)
                    
                if link in self.image_links:
                    print("跳过已下载的链接：link")
                    continue
                img_dicts = self.parse_image(link)
                # print("解析出的图片链接：", img_dicts)

                for key, value in img_dicts.items():
                    saves = os.path.join(save_path, value)
                    self.save_image_from_url(key, saves)
                    time.sleep(1)

            all_links, next_link = self.get_image_url(next_link)

    def run(self):
        self.test()

    def connect_signal(self):
        self.image_signal.connect(self.output_result)

    def output_result(self, result):
        print("\n输出结果：", result)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Referer": "https://home.meishichina.com/",
    }
    search_url = 'https://home.meishichina.com/search/'

    douguo = GetMeiShiThread(headers, search_url)
    douguo.set_food_name("枸杞叶")
    douguo.connect_signal()
    douguo.test()

    sys.exit(app.exec_())
