from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton ,QGroupBox, QScrollArea, QSpacerItem,
    QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt


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
    add_selected = pyqtSignal(int)
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
        self.button_add.clicked.connect(self.add_crop)
        
        self.button_add_ttl = QPushButton("Add_TTL")
        self.button_add_ttl.clicked.connect(self.add_crop)
        
        self.button_add_time = QPushButton("Add_TIME")
        self.button_add_time.clicked.connect(self.add_crop)
        
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
        layout_gb.addWidget(self.button_add_ttl)
        layout_gb.addWidget(self.button_add_time)
        layout_gb.addWidget(self.button_sq)
        layout_gb.addWidget(self.button_del)
        layout_gb.addWidget(self.button_export)
        
        self.gb.setLayout(layout_gb)
        layout.addWidget(self.gb)
        self.setLayout(layout)
    
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
        
    def add_crop(self):
        if self.sender() == self.button_add:
            self.add_selected.emit(VIDEO)
        elif self.sender() == self.button_add_ttl:
            self.add_selected.emit(TTL)
        elif self.sender() == self.button_add_time:
            self.add_selected.emit(TIME)
                    
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
        