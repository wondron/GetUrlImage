from PyQt5.QtWidgets import QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QWidget
from PyQt5.QtGui import QPainter, QMouseEvent, QWheelEvent
from PyQt5.QtCore import Qt, QRectF, QPointF
import get_douguo_thread
import cv2, os
import numpy as np
from PIL import Image


class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scaleFactor = 1.15
        self.pixmap_item = None
        self.rect_item = None
        self.rect_info = None
        self.start_pos = None
        self.end_pos = None
        self.dragging = False
        self.position_label = QLabel()
        self.position_label.setStyleSheet("background-color: white;")
        self.position_label.setFixedWidth(150)

        
    def display_image(self, pixmap):
        self.scene.removeItem(self.rect_item)
        self.rect_item = None
        self.rect_info = None
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        # 添加红框
        self.add_red_border()

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.scale(self.scaleFactor, self.scaleFactor)
        else:
            self.scale(1 / self.scaleFactor, 1 / self.scaleFactor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.start_pos = self.mapToScene(event.pos())

            if(self.start_pos.x() < 0):
                self.start_pos.setX(0)

            if(self.start_pos.y() < 0):
                self.start_pos.setY(0)

            if self.rect_item:
                self.scene.removeItem(self.rect_item)
            self.rect_item = QGraphicsRectItem()
            self.rect_item.setPen(Qt.red)
            self.scene.addItem(self.rect_item)
        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.dragging = True
            self.origin = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.pixmap_item == None:
            return        
        
        if self.start_pos:
            self.end_pos = self.mapToScene(event.pos())

            if(self.end_pos.x() > self.pixmap_item.boundingRect().width()):
                self.end_pos.setX(self.pixmap_item.boundingRect().width())
            
            if(self.end_pos.y() > self.pixmap_item.boundingRect().height()):
                self.end_pos.setY(self.pixmap_item.boundingRect().height())

            sub_pos = self.end_pos - self.start_pos
            if((sub_pos.x() < 0) or (sub_pos.y() < 0)):
                if self.rect_item is not None:
                    self.scene.removeItem(self.rect_item)
                    self.rect_item = None

                return

            self.rect_info = QRectF(self.start_pos, self.end_pos)
            if not self.rect_item:
                self.rect_item = QGraphicsRectItem()
                self.rect_item.setPen(Qt.red)
                self.scene.addItem(self.rect_item)

            self.rect_item.setRect(self.rect_info)

        elif self.dragging:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self.origin.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self.origin.y()))
            self.origin = event.pos()
        # 更新鼠标位置信息
        scene_pos = self.mapToScene(event.pos())
        self.position_label.setText(f"X: {int(scene_pos.x())}, Y: {int(scene_pos.y())}")

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # return
            self.start_pos = None
            self.end_pos = None
        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.dragging = False
            self.unsetCursor()

    def add_red_border(self):
        if self.pixmap_item:
            rect = self.pixmap_item.boundingRect()
            border_rect = QGraphicsRectItem(rect)
            border_rect.setPen(Qt.black)
            self.scene.addItem(border_rect)

    def get_label_rect(self):
        img_size = []
        if self.rect_info is not None:
            img_size.append(int(self.rect_info.left()))
            img_size.append(int(self.rect_info.top()))
            img_size.append(int(self.rect_info.right()))
            img_size.append(int(self.rect_info.bottom()))
        
        return img_size
    