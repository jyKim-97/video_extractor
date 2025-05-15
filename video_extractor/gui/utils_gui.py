from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QApplication, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt, QElapsedTimer, QTimer
import traceback


def error2messagebox(to_warn=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(traceback.format_exc())
                print(e)
                if to_warn:
                    QMessageBox.warning(None, "Warning", str(e))
                else:
                    QMessageBox.critical(None, "Error", str(e))
                    raise
        return wrapper
    return decorator


class tqdm_qt(QDialog):
    def __init__(self, total=0, desc="Processing...", parent=None, **kwargs):
        super().__init__(parent)
        self.total = total
        self.desc = desc
        self.n = 0

        self.elapsed_timer = QElapsedTimer()
        self.timer_ui = QTimer(self)
        self.timer_ui.timeout.connect(self.update_time_label)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Progressing")
        layout = QVBoxLayout()

        self.label_desc = QLabel(self.desc)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.total)
        self.label_time = QLabel("0:00 / ??:??")

        layout.addWidget(self.label_desc)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label_time)

        self.setLayout(layout)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(400, 100)

        self.elapsed_timer.start()
        self.timer_ui.start(1000)

        self.show()

    def update(self, n=1):
        self.n += n
        self.progress_bar.setValue(self.n)
        self.update_time_label()
        QApplication.processEvents()

        if self.n >= self.total:
            self.close()

    def update_time_label(self):
        elapsed_ms = self.elapsed_timer.elapsed()
        elapsed_s = elapsed_ms / 1000
        total_est = elapsed_s / self.n * self.total if self.n > 0 else 0

        def format_time(seconds):
            m, s = divmod(int(seconds), 60)
            return f"{m}:{s:02d} min"

        text = f"left: {format_time(total_est-elapsed_s)} / total: {format_time(total_est)}"
        self.label_time.setText(text)

    def close(self):
        self.timer_ui.stop()