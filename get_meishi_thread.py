from bs4 import BeautifulSoup
import time, requests, pickle
from tqdm import tqdm
from urllib.parse import urljoin
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import sys
from PyQt5.QtWidgets import QApplication


class GetMeiShiThread(QThread):
    image_signal = pyqtSignal(dict)
    
    def __init__(self, headers, url):
        super().__init__()
        self.headers = headers
        temp_url = url.rstrip('/') + '/'
        self.url = temp_url
    
    
    def set_food_name(self, food_name):
        self.food_name = food_name
        
    
    def get_response(self, url, headers, retry_times, wait_time):
        tryTime = 0
        while True:
            try:
                tryTime = tryTime + 1
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response    
            except:
                if tryTime >= retry_times:
                    return None
                print(f"url 获取失败，当前尝试次数{tryTime}, 等待时间{wait_time}s")
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
            if 'x-oss-process=style' not in img_url:
                continue

            temp_name = img_url.split('?')[0]
            name = temp_name.split('/')[-1].split('.')[0]
            houzhui = '.jpg' if temp_name.split('.')[-1].startswith('j') else '.png'
            total_name = f"300_{name}{houzhui}"
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
            if '下一页' in tag.contents:
                nextLink = urljoin(url, link)
                print("下一页：", link)
                continue
            if 'recipe-' not in link:
                continue

            # 将相对路径转换为绝对路径
            if not requests.compat.urlparse(link).netloc:
                link = requests.compat.urljoin(url, link)
                
            all_links.append(link)
            all_links = list(set(all_links))
        
        return all_links, nextLink
    

    def test(self):
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
    search_url = 'https://home.meishichina.com/search/'
    
    douguo = GetMeiShiThread(headers, search_url)
    douguo.set_food_name("板栗")
    douguo.connect_signal()
    douguo.test()

    sys.exit(app.exec_())