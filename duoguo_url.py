from bs4 import BeautifulSoup
import time, requests
from tqdm import tqdm
from PyQt5.QtCore import pyqtSignal, QThread
import sys
from PyQt5.QtWidgets import QApplication


class GetImageThread(QThread):
    result_signal = pyqtSignal(dict)
        
    def __init__(self, headers, url):
        super().__init__()
        self.headers = headers
        temp_url = url.rstrip('/') + '/'
        self.url = temp_url

    def set_food_name(self, food_name):
        self.food_name = food_name

    def getImageUrl(self, url):
        # 用于存储所有链接的列表
        all_links = []
        nextLink = ''
        # 发送HTTP请求获取网页内容
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # 如果请求失败，将抛出异常
        except requests.RequestException as e:
            print(f"请求异常: {e}，再次开始检测！")
            try:
                time.sleep(5)
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  # 如果请求失败，将抛出异常
            except requests.RequestException as e:
                return [], ''
        
        # 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', href=True)
        print("权限申请成功！")

        # 遍历所有<a>标签，提取href属性中的链接
        for tag in a_tags:
            link = tag['href']
            if tag.contents.__contains__('下一页'):
                nextLink = requests.compat.urljoin(url, link)
                continue
            
            if not link.__contains__('cookbook'):
                continue

            # 将相对路径转换为绝对路径
            if not requests.compat.urlparse(link).netloc:
                link = requests.compat.urljoin(url, link)
            all_links.append(link)
            all_links = list(set(all_links))
        
        return all_links, nextLink

    def parser_image(self, image_url):
        dicts = {}
        try:
            response = requests.get(image_url, headers=self.headers)
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                print("网址请求异常，等待1秒后继续申请！")
                time.sleep(5)
                response = requests.get(image_url, headers=self.headers)
                response.raise_for_status()
            except requests.HTTPError as e:
                print("网址请求再次异常，等待1秒后，下一个网址！")
                print("图像地址：", image_url)
                time.sleep(5)
                return dicts
        
        # 找到所有的图片标签
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if not img_url.__contains__('/200_'):
                continue
            full_img_url = img_url.replace('/200_', '/yuan_') if '/200_' in img_url else img_url
            temp_name = img_url.split('/')[-1]
            name = temp_name.split('.')[0]
            houzhui = '.jpg' if temp_name.split('.')[1].__contains__('j') else '.png'
            name = name + houzhui
            dicts[full_img_url] = name
        
        return dicts

    def get_total_images_url(self):
        firstUrl = self.url + self.food_name
        
        print("搜索url:", firstUrl)
        all_links, next_link = self.getImageUrl(firstUrl)
        
        img_dicts = dict()
        while next_link != '':
            for link in tqdm(all_links, ncols=70):
                img_dicts = self.parser_image(link)
                self.result_signal.emit(img_dicts)
                
            all_links, next_link = self.getImageUrl(next_link)

    def connect_signal(self):
        self.result_signal.connect(self.output_result)

    def output_result(self, result):
        print("\n输出结果：", result)
    
    def run(self):
        self.get_total_images_url()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    search_url = 'https://www.douguo.com/caipu/'
    
    douguo = GetImageThread(headers, search_url)
    douguo.set_food_name("板栗")
    douguo.connect_signal()
    douguo.start()

    sys.exit(app.exec_())