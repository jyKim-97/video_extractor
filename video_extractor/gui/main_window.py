import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication
from .video_panel import VideoPanel
from .control_panel import ControllPanel


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Video Extractor Tool")
        
        self.init_ui()
        
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.vpanel = VideoPanel()
        layout.addWidget(self.vpanel, stretch=9)
        
        self.vcpanel = ControllPanel()
        self.vpanel.connect_controllser(self.vcpanel)
        layout.addWidget(self.vcpanel, stretch=1)
        
        self.setLayout(layout)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
        