from bs4 import BeautifulSoup
import time, requests, os, pickle
from tqdm import tqdm
from urllib.parse import urljoin
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import sys
from PyQt5.QtWidgets import QApplication


class GetImageThread(QThread):
    
    image_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.save_dict = {}
        self.current_idx = 0
        self.headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
        
    
    def add_image_url(self, new_image):
        
        dict_a = self.save_dict
        dict_b = new_image
        
        dict_a.update(dict_b)
        self.save_dict = dict_a
        

    def set_image_folder(self, folder_path, food_name):
        os.makedirs(folder_path, exist_ok=True)
        self.save_path = os.path.join(folder_path, food_name)
        os.makedirs(self.save_path, exist_ok=True)
        time.sleep(1)
        
        
    def reset_data(self):
        self.save_dict.clear()
        self.current_idx = 0
        if self.isRunning():
            self.terminate()
            
    
    def test(self):
        while True:
            if self.current_idx >= len(self.save_dict.keys()):
                print("未发现新增dict，暂停一秒，继续检查。")
                time.sleep(1)
                continue
            
            image_url = list(self.save_dict.keys())[self.current_idx]
            self.current_idx = self.current_idx + 1
            image_name = self.save_dict[image_url]
            save_path = os.path.join(self.save_path, image_name)
            try:
                response = requests.get(image_url, headers = self.headers)
                response.raise_for_status()
                with open(f"{self.save_path}/{image_name}", 'wb') as f:
                    f.write(response.content)
                    # print(f"图像保存位置：{save_path}")
            except Exception as e:
                print(f"图像获取失败，{e}")
            time.sleep(1)
    
    def run(self):
        while True:
            if self.current_idx >= len(self.save_dict.keys()):
                # print("未发现新增dict，暂停一秒，继续检查。")
                time.sleep(1)
                continue
            
            image_url = list(self.save_dict.keys())[self.current_idx]
            self.current_idx = self.current_idx + 1
            image_name = self.save_dict[image_url]
            save_path = os.path.join(self.save_path, image_name)
            try:
                response = requests.get(image_url, headers = self.headers)
                response.raise_for_status()
                with open(f"{self.save_path}/{image_name}", 'wb') as f:
                    f.write(response.content)
                    # print(f"图像保存位置：{save_path}")
            except Exception as e:
                print(f"图像获取失败，{e}")
            time.sleep(1)
                
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    save_thread = GetImageThread()
    save_thread.set_image_folder('D:/01-code', '板栗')
    save_thread.start()
    
    image_save_dict = {}
    with open('image_dicts.pkl', 'rb') as f:
        image_save_dict = pickle.load(f)
        
    image_save_dicts = {}
    with open('image_dictss.pkl', 'rb') as f:
        image_save_dicts = pickle.load(f)
    
    data_dict = image_save_dict

    time.sleep(5)
    save_thread.add_image_url(image_save_dict)
    
    time.sleep(5)
    save_thread.set_image_folder('D:/01-code', '呵呵')
    
    time.sleep(5)
    save_thread.set_image_folder('D:/01-code', '你好')
    save_thread.add_image_url(image_save_dicts)
    
    sys.exit(app.exec_())