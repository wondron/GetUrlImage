from PyQt5.QtCore import pyqtSignal, QThread
from get_xiaCF_thread import GetXiaCFThread
from get_douguo_thread import GetDouGuoThread
from get_meishi_thread import GetMeiShiThread
import sys
from PyQt5.QtWidgets import QApplication

class WorkThead(QThread):
    image_signal = pyqtSignal(dict)
    
    def __init__(self, detect_name, thread_name):
        super().__init__()
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
        
        search_url = 'https://www.douguo.com/caipu/'
        self.douguo = GetDouGuoThread(headers, search_url)
        
        search_url = 'https://home.meishichina.com/search/'
        self.meishi = GetMeiShiThread(headers, search_url)
        
        search_url = 'https://www.xiachufang.com/search/?keyword={}&cat=1001'
        self.xiaCF = GetXiaCFThread(headers, search_url)
        self.set_detect_name(detect_name)
        self.method = thread_name
        
        self.image_dict = {}
        
        self.douguo.image_signal.connect(self.on_signal_image_get)
        self.meishi.image_signal.connect(self.on_signal_image_get)
        self.xiaCF.image_signal.connect(self.on_signal_image_get)


    def set_detect_name(self, name):
        self.douguo.set_food_name(name)
        self.meishi.set_food_name(name)
        self.xiaCF.set_food_name(name)
        

    def set_patu_method(self, name):
        print("修改爬图方式：", name)
        self.method = name


    def on_signal_image_get(self, image_dict):
        self.image_signal.emit(image_dict)


    def run(self):
        self.image_dict.clear()
        
        try:
            print("多线程执行：", self.method)
            if self.method == "豆果美食":
                self.douguo.start()
            elif self.method == "美食天下":
                self.meishi.start()
            elif self.method == "下厨房":
                self.xiaCF.start()
            elif self.method == "全获取":
                print("获取所有图像")
                self.douguo.start()
                while self.douguo.isRunning():
                    pass
                
                self.meishi.start()
                while self.meishi.isRunning():
                    pass
                
                self.xiaCF.start()
                while self.xiaCF.isRunning():
                    pass  
        except Exception as e:
            print(f"An error occurred: {e}")
            self.result_signal.emit(dict())
            
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    thread = WorkThead("猴脑", "全获取")
    thread.start()
    
    sys.exit(app.exec_())