from PyQt5.QtWidgets import (
        QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsLineItem
)

from PyQt5.QtGui import QPixmap, QImage, QFontMetrics, QPen
from PyQt5.QtCore import Qt, QRectF
from .custom_widgets import DraggableDot, DotLinkInteractor, RADIUS


MAX_WIDTH = 1600
MAX_HEIGHT = 1080


class ScencePanel(QGraphicsView):
    def __init__(self, enable_selection=True):
        super().__init__()
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setMinimumSize(640, 480)
        self.enable_selection = enable_selection
        self.frame_size = None
        if self.enable_selection:
            self.pen = QPen(Qt.red, 2)
            self.rect_link = DotLinkInteractor(self)
            self.dots = []
            self.lines = []
            self.clicked = False
            self.is_rect = False
    
    def clear_scene(self):
        self._scene.clear()
        
    def update_scene(self, frame):
        self.clear_scene()
        
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(pixmap_item)
        
        # resize view to fit image
        if self.frame_size is None:
            r1 = MAX_WIDTH/w if w > MAX_WIDTH else 1
            r2 = MAX_HEIGHT/h if h > MAX_HEIGHT else 1
            r = min(r1, r2)
            
            wr = int(w*r)
            hr = int(wr * h/w)
            self.setMinimumSize(wr, hr)
            self.setMaximumSize(wr, hr)
        
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(pixmap_item, Qt.KeepAspectRatio)
        
        if self.frame_size is None:
            self.setFixedSize(wr, hr)
            self.frame_size = (wr, hr)
        
    def reset_sel(self):
        self.clear_points()
    
    def mousePressEvent(self, event):
        if not self.enable_selection:
            return super().mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:
            self.is_rect = False
            pos = self.mapToScene(event.pos())
            
            clicked_item = None
            for dot in self.dots:
                d = (dot.pos[0] - pos.x())**2 + (dot.pos[1] - pos.y())**2
                if d < RADIUS*2:
                    clicked_item = dot
                    break
                
            if clicked_item is not None:
                clicked_item.select_item()
            else:
                if len(self.dots) == 4:
                    return

                # Draw a dot
                dot = DraggableDot(pos.x(), pos.y(), r=RADIUS)
                dot.setPen(self.pen)
                self._scene.addItem(dot)
                self.dots.append(dot)
                
                dot2 = self.dots[-1]
                if len(self.dots) > 1:
                    dot1 = self.dots[-2]
                    self.connect_dots(dot1, dot2)
                if len(self.dots) == 4:
                    dot1 = self.dots[0]
                    self.connect_dots(dot1, dot2)
                    
        elif event.button() == Qt.RightButton:
            self.is_rect = True
            self.rect_link.handle_mouse_press(event)
        
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.is_rect:
            self.rect_link.handle_mouse_move(event)
            super().mouseMoveEvent(event)

    def connect_dots(self, dot1, dot2):
        line = QGraphicsLineItem(dot1.pos[0], dot1.pos[1], dot2.pos[0], dot2.pos[1])
        line.setPen(self.pen)
        self._scene.addItem(line)
        self.lines.append(line)
        
        dot1.add_connection(line, dot2)
        dot2.add_connection(line, dot1)
    
    def clear_points(self):
        for item in self.lines + self.dots:
            self._scene.removeItem(item)
        self.lines.clear()
        self.dots.clear()
        self.rect_link.reset()
        
    def get_points(self):
        if self.is_rect:
            pos = self.rect_link.get_rect()
            return pos
        else:
            return [(d.pos[0], d.pos[1]) for d in self.dots]