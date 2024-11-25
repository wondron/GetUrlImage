import sys, os, cv2, requests, image_thread
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTextEdit, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QSizePolicy, QProgressBar, QSplitter, QComboBox 
from PyQt5.QtGui import QPixmap, QImage, QTextCursor
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QThread
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from io import BytesIO
import numpy as np
from PIL import Image
from class_viewer import ImageViewer
from save_image_thread import GetImageThread


class PicCaptureTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ini_thread()
        self.isRead = False
        self.image_dict = dict()
        self.image_url = []
        self.index = 0
        self.save_index = 0

    def initUI(self):
        # 设置窗口标题
        self.setWindowTitle("食材图像获取")
        self.resize(1500, 1200)

        # 创建两个窗口
        self.l_widget = QWidget()
        self.r_widget = QWidget()

        # 设置窗口背景颜色以便于区分
        self.l_widget.setStyleSheet("background-color: #f0f0f0; font-family: '微软雅黑'; border: 2px solid #ccc;")
        self.r_widget.setStyleSheet("background-color: #e0e0e0; font-family: '微软雅黑'; border: 2px solid #ccc;")

        # 在每个窗口中添加布局
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # 在布局中添加控件
        self.l_widget.setLayout(left_layout)
        self.r_widget.setLayout(right_layout)

        # 创建一个水平分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.l_widget)
        splitter.addWidget(self.r_widget)

        # 创建一个垂直布局并添加分割器
        vbox = QVBoxLayout(self)
        vbox.addWidget(splitter)
        self.setLayout(vbox)

        # 食材名称选择
        label_layout = QHBoxLayout()
        self.label = QLabel("食材名称")
        self.label.setMinimumWidth(200)
        self.foodLabel = QTextEdit("板栗")
        self.foodLabel.setMaximumHeight(35)
        self.showImage = QPushButton("开始搜索")
        self.showImage.clicked.connect(self.get_image_url)
        self.autoSave = QCheckBox('自动保存')
        label_layout.addWidget(self.label)
        label_layout.addWidget(self.foodLabel)
        label_layout.addWidget(self.showImage)
        label_layout.addWidget(self.autoSave)
        left_layout.addLayout(label_layout)

        # 保存位置选择
        savePath_layout = QHBoxLayout()
        save_label = QLabel("保存地址")
        save_label.setMinimumWidth(200)
        self.save_path = QTextEdit("")
        self.save_path.setMaximumHeight(35)
        self.save_path.setText(os.getcwd())
        self.dialog = QPushButton("...")
        self.dialog.setMinimumWidth(50)
        self.dialog.clicked.connect(self.select_folder)
        savePath_layout.addWidget(save_label)
        savePath_layout.addWidget(self.save_path)
        savePath_layout.addWidget(self.dialog)
        left_layout.addLayout(savePath_layout)

        #进度条
        third_layout = QHBoxLayout()
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        
        self.methods = QComboBox()
        self.methods.setMinimumWidth(200)
        self.methods.insertItem(0, "豆果美食")
        self.methods.insertItem(1, "美食天下")
        self.methods.insertItem(2, "下厨房")
        self.methods.insertItem(3, "全获取")
        self.methods.setMaximumHeight(60)
        self.methods.currentIndexChanged.connect(self.on_select_method)
        third_layout.addWidget(self.methods)
        third_layout.addWidget(self.progressBar)
        left_layout.addLayout(third_layout)

        # 图像显示
        self.image_label = ImageViewer()
        self.image_label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        left_layout.addWidget(self.image_label)

        #操作按钮
        operator_layout = QHBoxLayout()
        self.up = QPushButton("上一张(1)")
        self.down = QPushButton("下一张(2)")
        self.save = QPushButton("保存(c)")
        self.delete = QPushButton("删除(v)")
        operator_layout.addWidget(self.up)
        operator_layout.addWidget(self.down)
        operator_layout.addWidget(self.save)
        operator_layout.addWidget(self.delete)
        left_layout.addLayout(operator_layout)
        # self.set_operator_statue(False)
        
        self.up.clicked.connect(self.on_last)
        self.down.clicked.connect(self.on_next)
        self.save.clicked.connect(self.on_save)
        self.delete.clicked.connect(self.on_delete)
        self.up.setShortcut('1')
        self.down.setShortcut('2')
        self.save.setShortcut('c')
        self.delete.setShortcut('v')

        # 网络获取
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.handle_request)

        # 日志输出
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        right_layout.addWidget(self.log_edit)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        self.mouse_pos_label = QLabel("鼠标位置: ")
        left_layout.addWidget(self.mouse_pos_label)
        self.image_label.position_label = self.mouse_pos_label

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        self.save_path.setText(folder_path)

    def get_image_url(self):
        print("检测项：", self.foodLabel.toPlainText())
        slct_name = self.foodLabel.toPlainText()
        file_path = self.save_path.toPlainText()
        
        if slct_name == "":
            print("未输入检测项，请输入后再操作！")
            return
        # self.set_operator_statue(False)
        self.progressBar.setValue(0)
        self.index = 0
        self.image_dict.clear()
        self.thread.set_detect_name(slct_name)
        self.thread.start()
    
        if self.autoSave.isChecked():
            self.save_thread.start()        
        
    def ini_thread(self):
        self.thread = image_thread.WorkThead('板栗', '豆果美食')
        self.thread.image_signal.connect(self.handle_result)
        
        self.save_thread = GetImageThread()
        
    def show_image(self, index):
        image_url = self.image_url[index]
        request = QNetworkRequest(QUrl(image_url))
        self.network_manager.get(request)

    def handle_request(self, reply):
        if reply.error() != QNetworkReply.NoError:
            print("Error: ", reply.errorString())
            return
        
        pixmap = QPixmap()
        buffer = reply.readAll()
        pixmap.loadFromData(buffer)
        q_image = pixmap.toImage()

        # Convert QImage to OpenCV format
        q_image = q_image.convertToFormat(QImage.Format.Format_RGB32)
        width = q_image.width()
        height = q_image.height()
        ptr = q_image.bits()
        ptr.setsize(q_image.byteCount())
        image_array = np.array(ptr).reshape(height, width, 4)

        # Convert to RGB for OpenCV
        self.opencv_image = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
        # resized_cv_image = self.resize_image(self.opencv_image)
        resized_cv_image = self.opencv_image.copy()
        resized_cv_image = cv2.cvtColor(resized_cv_image, cv2.COLOR_BGR2RGB)

        # Convert back to QImage
        height, width, channel = resized_cv_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(resized_cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        # self.image_label.setPixmap(pixmap)
        self.image_label.display_image(pixmap)

    def resize_image(self, opencv_image):
        (h, w) = opencv_image.shape[:2]
        scale_width = self.image_label.size().width() / w
        scale_height = self.image_label.size().height() / h

        scale = min(scale_width, scale_height)
        
        # 计算新的图像尺寸
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized_image = cv2.resize(opencv_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized_image

    def handle_result(self, result):
        print("获取图像数量: ", len(result))
        if( not len(result)):
            return
        
        self.image_dict.update(result)
        self.image_url = list(self.image_dict.keys())
        # self.set_operator_statue(True)
        self.progressBar.setMaximum(len(self.image_url))
        if(self.index == 0):
            self.show_image(0)
            
        if self.autoSave.isChecked():
            slct_name = self.foodLabel.toPlainText()
            file_path = self.save_path.toPlainText()
            self.save_thread.set_image_folder(file_path, slct_name)
            self.save_thread.add_image_url(result)
        
    def write(self, text):
        cursor = self.log_edit.textCursor()
        cursor.insertText(text)
        self.log_edit.moveCursor(QTextCursor.End)
        
    def flush(self):
        self.log_edit.ensureCursorVisible()

    def close(self):
        sys.stdout = self.original_stdout

    def set_operator_statue(self, statue):
        self.up.setDisabled(not statue)
        self.down.setDisabled(not statue)
        self.save.setDisabled(not statue)
        self.delete.setDisabled(not statue)

        if not statue:
            self.progressBar.setValue(0)
        else:
            self.progressBar.setMaximum(len(self.image_url))

    def on_next(self):
        if(self.index < len(self.image_url) - 1):
            self.index = self.index + 1
            self.show_image(self.index)
            self.progressBar.setValue(self.index + 1)
        else:
            print("已经是最后一张了！")

    def on_last(self):
        if(self.index > 0):
            self.index = self.index - 1
            self.show_image(self.index)
            self.progressBar.setValue(self.index + 1)
        else:
            print("已经是第一张了！")
            
    def on_save_image(self):
        image_url = self.image_url
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
        for url in image_url:
            try:
                response = requests.get(url, headers)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                image_name = self.image_dict[image_url]
                file_folder = os.path.normpath(self.save_path.toPlainText())
                os.makedirs(file_folder, exist_ok=True)
                save_path = os.path.join(file_folder, self.foodLabel.toPlainText())
                os.makedirs(save_path, exist_ok=True)
                save_path = os.path.join(save_path, image_name)
                image.save(save_path)
            except Exception as e:
                print(f"保存图像时出错：{e}")
                        
    def on_save(self):
        if self.image_url == []:
            print("没有图片可以保存！")
            return
        
        image_name = self.image_dict[self.image_url[self.index]]
        file_folder = os.path.normpath(self.save_path.toPlainText())
        os.makedirs(file_folder, exist_ok= True)
        save_path = os.path.join(file_folder, self.foodLabel.toPlainText())
        os.makedirs(save_path, exist_ok= True)
        save_path = os.path.join(save_path, image_name)

        #图像裁剪
        image_rgb = cv2.cvtColor(self.opencv_image, cv2.COLOR_BGR2RGB)
        rect_info= self.image_label.get_label_rect()
        if len(rect_info) == 4:
            image_rgb = image_rgb[rect_info[1]:rect_info[3], rect_info[0]:rect_info[2]]

        image_pil = Image.fromarray(image_rgb)
        image_pil.save(save_path)
        self.on_next()
        
    def on_delete(self):
        image_name = self.image_dict[self.image_url[self.index]]
        file_folder = os.path.normpath(self.save_path.toPlainText())
        save_path = os.path.join(file_folder, self.foodLabel.toPlainText())
        save_path = os.path.join(save_path, image_name)
        if(os.path.exists(save_path)):
            print("存在图像，开始删除：", image_name)
            os.remove(save_path)
        else:
            print("不存在图像，不删除")
        
        self.on_next()

    def on_select_method(self):
        self.thread.set_patu_method(self.methods.currentText())


def main():
    app = QApplication(sys.argv)

    ex = PicCaptureTool()
    ex.show()

    ex.original_stdout = sys.stdout
    sys.stdout = ex

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()