from PyQt5.QtWidgets import (
        QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout,
        QToolButton, QLabel, QWidget, QFileDialog, QGraphicsPixmapItem,
        QGraphicsLineItem, QMessageBox
)

from PyQt5.QtGui import QPixmap, QImage, QFontMetrics, QPen
from PyQt5.QtCore import Qt, QRectF, pyqtSignal

# from ..processing import VideoReader
from ..processing.process_video import VideoReader
from .control_panel import ControllPanel
from .utils_gui import error2messagebox, tqdm_qt
from .custom_widgets import DraggableDot, DotLinkInteractor, ExportOptionDialog, RADIUS, set_is_square
import os


MAX_WIDTH = 1600
MAX_HEIGHT = 1080


class ScencePanel(QGraphicsView):
    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setMinimumSize(640, 480)
        self.pen = QPen(Qt.red, 2)
        self.rect_link = DotLinkInteractor(self)
        self.dots = []
        self.lines = []
        self.clicked = False
        self.is_rect = False
        self.frame_size = None
    
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


class VideoPanel(QWidget):
    
    add_crop_success = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.video_reader = None # VideoReader()
        # self.playing = False
        
    def init_ui(self):
        # entire layout
        layout = QVBoxLayout()
        
        # control panel
        layout_ui = self.init_ui_control_panel()
        layout.addLayout(layout_ui)
        
        # video scene
        self.scene_panel = ScencePanel()
        layout.addWidget(self.scene_panel)
        
        self.setLayout(layout)
    
    def init_ui_control_panel(self):
        layout = QHBoxLayout()
        self.button_load = QToolButton()
        self.text_load = QLabel("Video file name")
        
        self.button_load.setText("📁")
        self.button_load.clicked.connect(self._open_file_dialog)
        
        layout.addWidget(self.button_load)
        layout.addWidget(self.text_load)

        return layout
    
    def _open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, 
                                                  "Select video file", "",
                                                  "All files (*)"
                                                #   "Video Files (*.mp4, *.mkv, *.avi)" # ;;All file (*)
                                                  )
        if not filename: 
            return
        
        # set file name
        self.videofile = filename
        metrics = QFontMetrics(self.text_load.font())   
        elided_text = metrics.elidedText(filename, Qt.ElideLeft, self.text_load.width())
        self.text_load.setText(elided_text)
        
        # read video file
        self.video_reader = VideoReader(filename)
        frame = self.video_reader.read_frame()
        self.scene_panel.update_scene(frame)
        
    def connect_controllser(self, controller: ControllPanel):
        controller.reset_selected.connect(self.reset_crop)
        controller.add_selected.connect(self.add_crop)
        controller.export_selected.connect(self.export_video)
        controller.apply_selected.connect(self.apply_crop)
        controller.delete_selected.connect(self.delete_crop)
        controller.toggle_square.connect(self.make_square)
        self.add_crop_success.connect(controller.add_crop_item)
        
    def make_square(self, is_square):
        set_is_square(is_square)
        
    def delete_crop(self, cid):
        self.video_reader.delete_cache(cid)
    
    def reset_crop(self):
        self.scene_panel.reset_sel()
    
    @error2messagebox(to_warn=True)
    def add_crop(self, add_type: int):
        self.video_reader.cache_current_transform(add_type)
        self.add_crop_success.emit(add_type)
    
    @error2messagebox(to_warn=True)
    def export_video(self):
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  "Type video output prefix (avi)", "",
                                                  "All files (*)")
        prefix, ext = os.path.splitext(filename)
        
        # show popup to be exported
        dialog = ExportOptionDialog(self)
        if dialog.exec_():
            selection = dialog.get_selection()
        else:
            return
        
        done = self.video_reader.export_video(prefix, tqdm_qt,
                                              skip_video=not selection["video"],
                                              skip_ttl=not selection["ttl"],
                                              skip_timestamp=not selection["timestamp"])
        if done:
            QMessageBox.information(self, "Done", "Video export finished!")

    @error2messagebox(to_warn=True)
    def apply_crop(self, is_apply: int):
        if is_apply == 0:
            frame = self.video_reader.get_original_frame()
        elif is_apply == 1:
            pos = self.scene_panel.get_points()
            frame = self.video_reader.get_warped_frame(pos)
        elif is_apply >= 2:
            cid = is_apply - 2
            frame = self.video_reader.get_saved_warped_frame(cid)
        else:
            raise ValueError("Unexpected Apply ID")
            
        self.scene_panel.clear_points()
        self.scene_panel.update_scene(frame)
        
        
