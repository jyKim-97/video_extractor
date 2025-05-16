import sys
from PyQt5.QtWidgets import QApplication
from .gui import MainWindow
from .processing import VideoReader
import argparse
import sys


def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_cli", action="store_true", default=False,
                        help="Use CLI")
    parser.add_argument("--video", default=None, type=str,
                        help="Video file name")
    parser.add_argument("--transform", default=None, type=str,
                        help="Transformation information list (.pkl file)")
    parser.add_argument("--fout", default=None, type=str,
                        help="Output file name")
    parser.add_argument("--skip_timestamp", action="store_true", default=False,
                        help="skip timestamp OCR")
    parser.add_argument("--skip_video", action="store_true", default=False,
                        help="skip video processing")
    parser.add_argument("--skip_ttl", action="store_true", default=False,
                        help="skip ttl extraction")
    return parser


# def main(use_cli=None, video=None, transform=None, fout=None,
#          skip_timestamp=None, skip_video=None, skip_ttl=None):
def main():
    
    args = build_args().parse_args()
    
    if not args.use_cli:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        if args.video is None or args.transform is None or args.fout is None:
            raise ValueError("Option video, transform, and fout must be specified for cli")

        vobj = VideoReader(args.video)
        vobj.load_transforminfo(args.transform)
        vobj.export_video(args.fout,
                          skip_timestamp=args.skip_timestamp,
                          skip_video=args.skip_video,
                          skip_ttl=args.skip_ttl)


if __name__ == "__main__":
    main()
    # main(**vars(build_args().parse_args()))