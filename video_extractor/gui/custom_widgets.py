from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsItem,
    QCheckBox, QMessageBox, QDialogButtonBox, QDialog
)

from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QPointF, QObject

MAKE_SQUARE = False
RADIUS = 10

def sign(val):
    return -1 if val < 0 else 1


class DraggableDot(QGraphicsEllipseItem):
    
    def __init__(self, x, y, r=3):
        super().__init__(-r, -r, r*2, r*2)
        self.setPos(x, y)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)
        self.setPen(Qt.red)
        self.setBrush(Qt.red)
        self.connected_lines = []
        self.pos = (x, y)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # new_pos = self.mapToScene(value)
            new_pos = (value.x(), value.y())
            for line, other_dot in self.connected_lines:
                other_pos = other_dot.pos
                line.setLine(other_pos[0], other_pos[1], new_pos[0], new_pos[1])
            self.pos = new_pos
        
        return super().itemChange(change, value)
    
    def add_connection(self, line, other_dot):
        self.connected_lines.append((line, other_dot))
        line.setLine(other_dot.pos[0], other_dot.pos[1], self.pos[0], self.pos[1])

    def mouseReleaseEvent(self, event):
        self.setSelected(False)
        self.setBrush(Qt.red)
        super().mouseReleaseEvent(event)
    
    def select_item(self):
        self.setSelected(True)
        self.setBrush(Qt.green)
        
    def move_item(self, x, y):
        self.setPos(x, y)
        self.pos = (x, y)
        value = QPointF(x, y)
        self.itemChange(QGraphicsItem.ItemPositionChange, value)


class DotLinkInteractor(QObject):
    def __init__(self, scene_panel, pen=None):
        super().__init__()
        self.scene_panel = scene_panel
        self.pen = pen or QPen(Qt.blue, 2)
        self.is_active = False
        self.start_dot = None
        self.follower_dot = None
        self.pos = []
        self.rect_pos = [[] for _ in range(4)]
        self.lines = []

    def toggle(self):
        self.is_active = not self.is_active
        self.active = self.is_active
        self.scene_panel.setMouseTracking(self.is_active)

    def handle_mouse_press(self, event):
        self.toggle()
        pos = self.scene_panel.mapToScene(event.pos())
        if self.is_active:
            if self.start_dot is None:
                self.start_dot = DraggableDot(pos.x(), pos.y())
                self.scene_panel._scene.addItem(self.start_dot)
                self.follower_dot = DraggableDot(pos.x(), pos.y())
                self.scene_panel._scene.addItem(self.follower_dot)
                self.pos.append((pos.x(), pos.y()))
        else:
            pos = self.read_pos(pos)
            self.follower_dot.move_item(pos.x(), pos.y())
            self.pos.append((pos.x(), pos.y()))
            
        self.generate_line((self.start_dot.x(), self.start_dot.y()),
                           (self.follower_dot.x(), self.follower_dot.y()))
            
    def handle_mouse_move(self, event):
        pos = self.scene_panel.mapToScene(event.pos())
        pos = self.read_pos(pos)
        if self.is_active and self.follower_dot:
            self.follower_dot.setPos(pos)
            self.generate_line(self.pos[0], (pos.x(), pos.y()))
            
    def read_pos(self, pos):
        if MAKE_SQUARE:
            pos0 = self.pos[0]
            dx = pos.x() - pos0[0]
            dy = pos.y() - pos0[1]
            d = min(abs(dx), abs(dy))
            xnew = int(pos0[0] + sign(dx)*d)
            ynew = int(pos0[1] + sign(dy)*d)
            pos.setX(xnew)
            pos.setY(ynew)
        return pos
            
    def generate_line(self, start_pos, end_pos):
        self.build_rect_pos(start_pos, end_pos)
        if len(self.lines) == 0:
            self.lines = [QGraphicsLineItem(*p) for p in self.rect_pos]
            for l in self.lines:
                l.setPen(self.pen)
                self.scene_panel._scene.addItem(l)
        else:
            for l, p in zip(self.lines, self.rect_pos):
                l.setLine(*p)
            
    def build_rect_pos(self, start_pos, end_pos):
        self.rect_pos = (
            (start_pos[0], start_pos[1], start_pos[0], end_pos[1]),
            (start_pos[0], end_pos[1], end_pos[0], end_pos[1]),
            (end_pos[0], end_pos[1], end_pos[0], start_pos[1]),
            (end_pos[0], start_pos[1], start_pos[0], start_pos[1])
        )
        
    def get_rect(self):
        return [
            (p[0], p[1]) for p in self.rect_pos
        ]

    def reset(self):
        self.active = False
        self.scene_panel.setMouseTracking(False)
        for l in self.lines + [self.start_dot, self.follower_dot]:
            if l is not None:
                self.scene_panel._scene.removeItem(l)

        self.lines.clear()
        self.pos.clear()
        self.start_dot = None
        self.follower_dot = None


class ExportOptionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Data Types to Export")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select datatype to be exported:"))

        self.chk_video = QCheckBox("Encoded video")
        self.chk_ttl = QCheckBox("TTL signal")
        self.chk_timestamp = QCheckBox("Timestamp")

        # Default: all checked
        self.chk_video.setChecked(True)
        self.chk_ttl.setChecked(True)
        self.chk_timestamp.setChecked(True)

        layout.addWidget(self.chk_video)
        layout.addWidget(self.chk_ttl)
        layout.addWidget(self.chk_timestamp)

        # Add OK/Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_selection(self):
        return {
            "video": self.chk_video.isChecked(),
            "ttl": self.chk_ttl.isChecked(),
            "timestamp": self.chk_timestamp.isChecked()
        }
        
        
def set_is_square(is_square):
    global MAKE_SQUARE
    MAKE_SQUARE = is_square