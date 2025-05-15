import argparse
from processing.process_video import VideoReader
import pickle as pkl


def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=str,
                        help="Video file name")
    parser.add_argument("--transform", required=True, type=str,
                        help="Transformation information list")
    parser.add_argument("--fout", required=True, type=str,
                        help="Output file name")
    return parser


def cut_video(video, transform, fout):
    
    with open(transform, "rb") as fp:
        trans_list = pkl.load(fp)
        
    video_reader = VideoReader(video)
    video_reader.transformer_set = trans_list
    video_reader.export_video()
    
    video_reader.export_video(fout)
    
    # video_reader.export_video()