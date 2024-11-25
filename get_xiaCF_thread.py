from bs4 import BeautifulSoup
import time, requests
from tqdm import tqdm
from urllib.parse import urljoin
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import sys, os
from PyQt5.QtWidgets import QApplication


class GetXiaCFThread(QThread):
    image_signal = pyqtSignal(dict)
    
    def __init__(self, headers, url):
        super().__init__()
        self.headers = headers
        temp_url = url.rstrip('/') + '/'
        self.url = temp_url
        self.image_links = self.read_image_links()
        print(self.image_links)
        
        
    def read_image_links(self):
        image_links = []
        try:
            with open('image_links.yaml', 'r') as file:
                for line in file:
                    if line.strip():
                        image_links.append(line.strip()[2:])
                os.remove('image_links.yaml')
            return image_links
        except Exception as e:
            print(f"读取image_links.yaml时出错：{e}")
            return []
    
    def set_food_name(self, food_name):
        self.food_name = food_name
        
    
    def get_response(self, url, headers, retry_times, wait_time):
        tryTime = 0
        while True:
            try:
                tryTime = tryTime + 1
                response = requests.get(url, headers=headers, timeout=10)  # 设置超时时间
                response.raise_for_status()
                return response    
            except requests.exceptions.RequestException as e:
                if tryTime >= retry_times:
                    return None
                print(f"url 获取失败，当前尝试次数{tryTime}, 等待时间{wait_time}s, 错误信息: {e}")
                time.sleep(wait_time)

        
    def parse_image(self, image_url):
        dicts = {}
        response = self.get_response(image_url, self.headers, 3, 5)
        
        if response is None:
            print(f"{image_url}, 图像获取失败, 返回空字典！")
            return {}
        # 找到所有的图片标签
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        for img_tag in img_tags:
            # 获取图片的URL
            img_url = img_tag.get('src')
            if not img_url.__contains__('imageView2/2'):
                continue

            temp_name = img_url.split('?')[0]
            name = temp_name.split('/')[-1]
            name = name.split('.')[0]
            name = name.split('_')[0]
            houzhui = '.jpg'
            format_name = temp_name.split('.')[-1]
            houzhui = '.jpg' if 'j' in format_name else '.png'
            total_name = "400_" + name + houzhui
            dicts[temp_name] = total_name
        
        return dicts


    def get_image_url(self, url):
        all_links = []
        nextLink = ''
        
        response = self.get_response(url, self.headers, 3, 5)
        if response is None:
            return all_links, nextLink
        
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', href=True)
        print("权限申请成功！")

        for tag in a_tags:
            link = tag['href']
            if tag.contents.__contains__('下一页'):
                nextLink = requests.compat.urljoin(url, link)
                print("下一页：", tag['href'])
                continue
            if not link.__contains__('/recipe/'):
                continue

            # 将相对路径转换为绝对路径
            if not requests.compat.urlparse(link).netloc:
                link = requests.compat.urljoin(url, link)
                
            all_links.append(link)
            all_links = list(set(all_links))
        
        return all_links, nextLink
    

    def test(self):
        first_url = self.url.format(self.food_name)
        
        print("搜索URL：", first_url)
        all_links, next_link = self.get_image_url(first_url)
        img_dicts = dict()
        
        while next_link != '':
            for link in all_links:
                img_dicts = self.parse_image(link)
                self.image_signal.emit(img_dicts)
                time.sleep(2)
            all_links, next_link = self.get_image_url(next_link)
            
    def run(self):
        first_url = self.url + self.food_name
        
        print("搜索URL：", first_url)
        all_links, next_link = self.get_image_url(first_url)
        img_dicts = dict()
        
        while next_link != '':
            for link in all_links:
                img_dicts = self.parse_image(link)
                self.image_signal.emit(img_dicts)
                time.sleep(2)
            all_links, next_link = self.get_image_url(next_link)

    def connect_signal(self):
        self.image_signal.connect(self.output_result)

    def output_result(self, result):
        print("\n输出结果：", result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    search_url = 'https://www.xiachufang.com/search/?keyword={}&cat=1001'
    
    douguo = GetXiaCFThread(headers, search_url)
    douguo.set_food_name("穿心莲")
    douguo.connect_signal()
    douguo.test()

    sys.exit(app.exec_())