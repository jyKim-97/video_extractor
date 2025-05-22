from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton ,QGroupBox, QScrollArea, QSpacerItem,
    QSizePolicy, QPushButton, QFormLayout, QGroupBox, QDoubleSpinBox, QCheckBox, QRadioButton, QComboBox,
    QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal
from .scene_panel import ScencePanel
from .utils_gui import error2messagebox
# from .video_panel import VideoPanel


cprefix = ["crop_", "ttl_", "time_"]

VIDEO = 0
TTL = 1
TIME = 2


class cItem(QPushButton):
    selected = pyqtSignal(int)
    def __init__(self, id, add_type):
        super().__init__()
        self.id = id
        self.setText("%s%d"%(cprefix[add_type], id))
        self.setCheckable(True)
        self.setChecked(False)
        self.setStyleSheet("background-color: lightgray;")
        # self.setStyleSheet("background-color: lightblue;")
        self.clicked.connect(self.set_checked)
        
    def set_checked(self):
        if self.isChecked():
            self.setStyleSheet("background-color: lightblue;")
            self.selected.emit(self.id)
        else:
            self.setStyleSheet("background-color: lightgray;")


class ControllPanel(QWidget):
    
    reset_selected = pyqtSignal()
    apply_selected = pyqtSignal(int)
    add_selected = pyqtSignal()
    delete_selected = pyqtSignal(int)
    export_selected = pyqtSignal()
    toggle_square = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.is_apply = False
        self.crop_id = 0
        self.crop_items = dict()
        # self.setMinimumWidth(100)
        self.setFixedWidth(200)
        self.init_ui()
        # self.trans_panel = None
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        empty_space = QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(empty_space)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        
        self.gb = QGroupBox("Add Crop")
        layout_gb = QVBoxLayout()
        
        self.button_reset = QPushButton("Clear")
        self.button_reset.clicked.connect(self.reset_crop)
        
        self.button_apply = QPushButton("Apply")
        self.button_apply.clicked.connect(self.apply_crop)
        
        self.button_add = QPushButton("Add")
        self.button_add.clicked.connect(self._add_crop)
        
        # self.button_add_ttl = QPushButton("Add_TTL")
        # self.button_add_ttl.clicked.connect(self.add_crop)
        
        # self.button_add_time = QPushButton("Add_TIME")
        # self.button_add_time.clicked.connect(self.add_crop)
        
        self.button_sq = QPushButton("Set Square")
        self.button_sq.setCheckable(True)
        self.button_sq.setChecked(False)
        self.button_sq.clicked.connect(self.set_square)
        
        self.button_del = QPushButton("Delete")
        self.button_del.clicked.connect(self.delete_crop)
        
        self.button_export = QPushButton("Export")
        self.button_export.clicked.connect(self.export_video)
        
        layout_gb.addWidget(self.button_reset)
        layout_gb.addWidget(self.button_apply)
        layout_gb.addWidget(self.button_add)
        # layout_gb.addWidget(self.button_add_ttl)
        # layout_gb.addWidget(self.button_add_time)
        layout_gb.addWidget(self.button_sq)
        layout_gb.addWidget(self.button_del)
        layout_gb.addWidget(self.button_export)
        
        self.gb.setLayout(layout_gb)
        layout.addWidget(self.gb)
        self.setLayout(layout)
        
        # self.trans_panel = TransformPanel()
    
    def set_square(self):
        self.toggle_square.emit(self.button_sq.isChecked())
        
    def delete_crop(self):
        for k, item in self.crop_items.items():
            if item.isChecked():
                cid = item.id
                self.scroll_layout.removeWidget(item)
                self.delete_selected.emit(cid)
                self.crop_items[k] = []
        
    def reset_crop(self):
        self.reset_selected.emit()
        for k, item in self.crop_items.items():
            if item.isChecked():
                item.setChecked(False)
        
    def _add_crop(self):
        self.add_selected.emit()
                    
    def add_crop_item(self, add_type):
        self.crop_items[self.crop_id] = cItem(self.crop_id, add_type)
        self.crop_items[self.crop_id].selected.connect(self.select_crop_item)
        
        self.scroll_layout.addWidget(
            self.crop_items[self.crop_id]
        )
        self.crop_id += 1
        
    def select_crop_item(self, cid):
        self.apply_selected.emit(cid+2)
        self.button_apply.setText("Reset")
        self.is_apply = True
        
    def apply_crop(self):
        if not self.is_apply:
            self.button_apply.setText("Reset") # -> 0
            self.is_apply = True
        else:
            self.button_apply.setText("Apply") # -> 1
            self.is_apply = False
        self.apply_selected.emit(self.is_apply)
        
    def export_video(self):
        self.export_selected.emit()

        
class TransformPanel(QWidget):
    
    signal_trans_update = pyqtSignal(dict)
    signal_trans_add  = pyqtSignal(int)
    
    def __init__(self, frame):
        super().__init__()
        self.setWindowTitle("Transform Panel")
        self.setGeometry(100, 100, 400, 300)
        self.init_frame = frame
        self.frame = self.init_frame.copy()
        self.ctrl_fields = dict()
        self.ctrl_value = None
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.scene = ScencePanel()
        self.scene.update_scene(self.init_frame)
        layout.addWidget(self.scene)
        
        # add image control
        gb_box = QGroupBox("Image control")
        layout_gb = QVBoxLayout()
        
        # image setting
        ## brightness, contrast
        layout_form = QFormLayout()
        self._add_dspinbox(layout_form, "Brightness", vmin=-50, vmax=50, vdefault=0)
        self._add_dspinbox(layout_form, "Contrast", vmin=0, vmax=50, vdefault=1)
        ## turn on histogram
        self._add_checkbox(layout_form, "Histnorm")
        layout_gb.addLayout(layout_form)
        
        # type setting
        self.cb_type = QComboBox()
        self.cb_type.addItem("None", userData=-1)
        self.cb_type.addItem("Video", userData=VIDEO)
        self.cb_type.addItem("TTL", userData=TTL)
        self.cb_type.addItem("Timestamp", userData=TIME)
        layout_gb.addWidget(self.cb_type)
        
        self.button_apply = QPushButton("Apply")
        self.button_apply.clicked.connect(self._read_value)
        layout_gb.addWidget(self.button_apply)
        
        self.button_add = QPushButton("Add")
        self.button_add.clicked.connect(self._add_transform)
        layout_gb.addWidget(self.button_add)
        
        self.buttton_reset = QPushButton("Reset")
        self.buttton_reset.clicked.connect(self._reset)
        layout_gb.addWidget(self.buttton_reset)
        
        gb_box.setLayout(layout_gb)
        
        layout.addWidget(gb_box)
        
        self.setLayout(layout)
        
    def connect_controlpanel(self, video_panel, control_panel: ControllPanel):
        video_panel.trans_panel = self
        control_panel.trans_panel = self
        self.signal_trans_add.connect(video_panel.add_transform)
        self.signal_trans_update.connect(video_panel.update_transform)
    
    @error2messagebox(to_warn=True)
    def _add_transform(self, *args):
        if self.ctrl_value is None:
            raise ValueError("Please apply the change first")
        
        value = self.cb_type.currentData()
        if value == -1:
            raise ValueError("Please select exporting type")
        
        self.signal_trans_add.emit(value)
        
    def _add_dspinbox(self, layout: QFormLayout, key, vmin=-50, vmax=50, vdefault=0):
        obj = QDoubleSpinBox()
        obj.setRange(vmin, vmax)
        obj.setValue(vdefault)
        layout.addRow(key, obj)
        self.ctrl_fields[key] = (obj, "dspin")
        
    def _add_checkbox(self, layout: QVBoxLayout, key):
        obj = QCheckBox(key)
        layout.addWidget(obj)
        self.ctrl_fields[key] = (obj, "checkbox")
        
    def _read_value(self):
        self.ctrl_value = dict()
        for key in self.ctrl_fields.keys():
            obj, obj_type = self.ctrl_fields[key]
            if obj_type == "dspin":
                self.ctrl_value[key] = obj.value()
            elif obj_type == "checkbox":
                self.ctrl_value[key] = obj.isChecked()
            else:
                raise ValueError("Unknown type in control panel")
        self.signal_trans_update.emit(self.ctrl_value)
        
    def update_scene(self, frame):
        self.scene.update_scene(frame)
        
    def _reset(self):
        self.ctrl_value = None
        for key in self.ctrl_fields.keys():
            obj, obj_type = self.ctrl_fields[key]
            if obj_type == "dspin":
                obj.setValue(0)
            elif obj_type == "checkbox":
                obj.setCheckState(0)
            else:
                raise ValueError("Unknown type in control panel")
        self.frame = self.init_frame.copy()
        self.scene.update_scene(self.frame)

