import sys
from PyQt5.QtWidgets import QApplication
from .gui import MainWindow
from .processing import VideoReader
import argparse


def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", type=str, action="store_false", default=True,
                        help="Output file name")
    parser.add_argument("--video", default=None, type=str,
                        help="Video file name")
    parser.add_argument("--transform", default=None, type=str,
                        help="Transformation information list")
    parser.add_argument("--fout", default=None, type=str,
                        help="Output file name")
    return parser


def main(gui=None, video=None, transform=None, fout=None):
    if gui:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        if video is None or transform is None or fout is None:
            raise ValueError("Option video, transform, and fout must be specified for cli")
        
        vobj = VideoReader(video)
        vobj.export_video(fout)


if __name__ == "__main__":
    main(**vars(build_args().parse_args()))