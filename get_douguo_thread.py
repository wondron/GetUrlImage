from bs4 import BeautifulSoup
import time, requests
from PIL import Image
from tqdm import tqdm
from io import BytesIO
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import sys, os, warnings, yaml
from PyQt5.QtWidgets import QApplication

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


class GetDouGuoThread(QThread):
    image_signal = pyqtSignal(dict)
    
    def __init__(self, headers, url):
        super().__init__()
        self.headers = headers
        self.url = url.rstrip('/') + '/'
        
        current_directory = os.getcwd()
        self.yaml_path = os.path.join(current_directory, 'image_link.yaml')
        self.image_links = self.read_image_links()
        
    def read_image_links(self):
        image_links = []
        try:
            with open(self.yaml_path, 'r') as files:
                for line in files:
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
        from urllib.parse import quote
        try_time = 0
        encoded_url = quote(url, safe='/:?=&')
        while try_time < retry_times:
            try:
                try_time += 1
                response = requests.get(encoded_url, headers=headers, timeout=10)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    print(f"403 Forbidden: 可能需要检查 Headers 或使用代理。尝试 {try_time}/{retry_times}")
                else:
                    print(f"HTTP 错误：{e}")
            except Exception as e:
                print(f"请求失败：{e}，尝试 {try_time}/{retry_times}，等待 {wait_time}s")
            time.sleep(wait_time + try_time * 2)  # 增加动态延时
        return None
    
    
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

    def get_image_url(self, url):
        all_links = []
        nextLink = ''
        response = self.get_response(url, self.headers, 3, 5)
        if response is None:
            print("结果未获取，结束线程。")
            return all_links, nextLink
        
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', href=True)

        for tag in a_tags:
            link = tag['href']
            if tag.contents.__contains__('下一页'):
                nextLink = requests.compat.urljoin(url, link)
                continue
            if not link.__contains__('cookbook'):
                continue
            if not requests.compat.urlparse(link).netloc:
                link = requests.compat.urljoin(url, link)
            all_links.append(link)
            
        return list(set(all_links)), nextLink
    
    def save_image_from_url(self, url, save_path):
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            image.save(save_path)
            print(f'图像已保存到：{save_path}')
        except Exception as e:
            print(f"保存图像时出错：{e}")
    
    def test(self):
        save_path = os.path.join(os.getcwd(), 'image', self.food_name)
        os.makedirs(save_path, exist_ok=True)
        
        first_url = self.url + self.food_name
        print("搜索URL：", first_url)
        
        all_links, next_link = self.get_image_url(first_url)
        img_dicts = dict()
        
        while next_link:
            for link in all_links:
                with open(self.yaml_path, 'a') as file:
                    yaml.dump([link], file)
                
                if link in self.image_links:
                    print("该链接已下载，跳过。")
                    continue
                img_dicts = self.parse_image(link)
                print("解析出的图片链接：", img_dicts)
                
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.douguo.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    search_url = 'https://www.douguo.com/caipu/'
    
    douguo = GetDouGuoThread(headers, search_url)
    douguo.set_food_name("枸杞叶")
    douguo.connect_signal()
    douguo.test()

    sys.exit(app.exec_())