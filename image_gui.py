import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QSizePolicy, QProgressBar, QSplitter
from PyQt5.QtGui import QPixmap, QImage, QTextCursor
from PyQt5.QtCore import pyqtSignal, QThread, QUrl, QByteArray, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import get_douguo_thread
import cv2, os
import numpy as np
from PIL import Image

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图像获取软件')

        # 创建两个窗口
        self.l_widget = QWidget()
        self.r_widget = QWidget()

        # 设置窗口背景颜色以便于区分
        self.l_widget.setStyleSheet("background-color: lightblue;")
        self.r_widget.setStyleSheet("background-color: lightgreen;")

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

        # 设置分割器比例
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        # 创建一个垂直布局并添加分割器
        vbox = QVBoxLayout(self)
        vbox.addWidget(splitter)
        self.setLayout(vbox)

        # 设置窗口初始大小
        self.resize(800, 400)

        # 食材名称选择
        label_layout = QHBoxLayout()
        self.label = QLabel("食材名称")
        self.foodLabel = QTextEdit("板栗")
        self.foodLabel.setMaximumHeight(25)
        self.showImage = QPushButton("开始搜索")
        # self.showImage.clicked.connect(self.get_image_url)
        label_layout.addWidget(self.label)
        label_layout.addWidget(self.foodLabel)
        label_layout.addWidget(self.showImage)
        left_layout.addLayout(label_layout)

        # 保存位置选择
        savePath_layout = QHBoxLayout()
        save_label = QLabel("保存地址")
        self.save_path = QTextEdit("")
        self.save_path.setMaximumHeight(25)
        self.dialog = QPushButton("...")
        # self.dialog.clicked.connect(self.select_folder)
        savePath_layout.addWidget(save_label)
        savePath_layout.addWidget(self.save_path)
        savePath_layout.addWidget(self.dialog)
        left_layout.addLayout(savePath_layout)

        # 图像显示
        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy(QSizePolicy.Preferred , QSizePolicy.Expanding))
        left_layout.addWidget(self.image_label)

        # 网络获取
        self.network_manager = QNetworkAccessManager(self)
        # self.network_manager.finished.connect(self.handle_request)

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

        # 日志输出
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        right_layout.addWidget(self.log_edit)


def main():
    app = QApplication(sys.argv)
    main_window = Window()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
