from PyQt5.QtWidgets import (
        QVBoxLayout, QHBoxLayout,
        QToolButton, QLabel, QWidget, QFileDialog, QMessageBox
)

from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt, pyqtSignal

# from ..processing import VideoReader
from ..processing.process_video import VideoReader
from .control_panel import ControllPanel, TransformPanel
from .utils_gui import error2messagebox, tqdm_qt
from .custom_widgets import ExportOptionDialog, set_is_square
from .scene_panel import ScencePanel
import os

from ..gui.control_panel import VIDEO, TTL, TIME





class VideoPanel(QWidget):
    
    add_crop_success = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.video_reader = None # VideoReader()
        self.trans_panel = None # Transformpanel
     
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
        controller.add_selected.connect(self.transform_crop)
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
    def transform_crop(self):
        """
        Open new window for detailed transformation setting
        """
        self.trans_panel = TransformPanel(self.video_reader.get_current_frame())
        self.trans_panel.signal_trans_update.connect(self._update_trans)
        self.trans_panel.signal_trans_add.connect(self._add_trans)
        self.trans_panel.show()
        self.trans_panel.raise_()
        self.trans_panel.activateWindow()
        
    def _update_trans(self, value: dict):
        frame = self.video_reader.adjust_image(self.video_reader.get_current_frame(),
                                               value.get("Brightness", 0),
                                               value.get("Contrast", 1),
                                               value.get("Histnorm", False))
        self.trans_panel.update_scene(frame)
    
    def _add_trans(self, cache_type):
        self.trans_panel.close()
        self.video_reader.cache_current_transform(cache_type)
        self.add_crop_success.emit(cache_type)
    
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
