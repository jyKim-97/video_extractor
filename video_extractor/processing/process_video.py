import cv2
import numpy as np
from tqdm import tqdm
from dataclasses import dataclass
import pickle as pkl
from typing import List
import csv
import pytesseract
from datetime import datetime

from ..gui.control_panel import VIDEO, TTL, TIME


FPS = 25
EXT = ".avi"

@dataclass
class TransformInfo:
    M: np.ndarray[float]
    max_width: int
    max_height: int
    type: int = -1
    
    def transform(self, frame):
        return cv2.warpPerspective(frame, self.M, (self.max_width, self.max_height))
    
    
def parse_timestamp(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    try:
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:/.,msΔt'
        text = pytesseract.image_to_string(thresh, config=custom_config)
        text = text.split("\n")
        
        timestamp = text[0]
        dt = datetime.strptime(timestamp, "%y:%m:%d/%H:%M:%S.%f")
        
        time_str = dt.strftime("%H:%M:%S.%f")
        sec_str = "%.3f"%(dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1_000_000)
    except Exception as e:
        print("Error while parsing: ", e)
        
        time_str = ""
        sec_str = ""
    
    print(time_str, sec_str)
    return time_str, sec_str


class VideoReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.cap = None
        self.frame = None
        self.warped = None
        self.transformer = None
        self.transformer_set: List[TransformInfo] = []
        self.warped_set = []
        self._open_video()
        
    def _open_video(self):
        self.cap = cv2.VideoCapture(self.file_path)
        if not self.cap.isOpened():
            self.cap = None
            raise FileExistsError(f"Cannot open video file: {self.file_path}")
        
    def read_frame(self):
        if self.cap is None:
            return None
        
        sucess, frame = self.cap.read()
        if not sucess:
            return None
        
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.frame
    
    def close(self):
        if self.cap is not None:
            self.cap.close()
    
    def get_warped_frame(self, pts):
        if self.frame is None:
            return None
        
        rect = order_points(pts)

        # Compute width and height of the new image
        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        max_width = int(max(widthA, widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        max_height = int(max(heightA, heightB))

        # Destination rectangle
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype="float32")
        
        # build transform info
        self.transformer = TransformInfo(
            M=cv2.getPerspectiveTransform(rect, dst),
            max_width=max_width,
            max_height=max_height
        )

        # Compute transform and warp
        self.warped = self.transformer.transform(self.frame)
        
        return self.warped
    
    def get_saved_warped_frame(self, cid):
        if cid >= len(self.warped_set):
            raise ValueError("Selected ID exceedes warpped image number")
        return self.warped_set[cid]
    
    def get_original_frame(self):
        self.warped = None
        return self.frame
    
    def apply_warped(self):
        if self.warped is not None:
            self.frame = self.warped
            self.warped = None
            
    def load_transforminfo(self, file_path):
        with open(file_path, "rb") as f:
            self.transformer = pkl.load(f)
        
        if not isinstance(self.transformer, TransformInfo):
            raise TypeError("Invalid transform info file")
        
        # Check if the transformer is valid
        if self.transformer.M is None or self.transformer.max_width <= 0 or self.transformer.max_height <= 0:
            raise ValueError("Invalid transform info")
            
    def export_transforminfo(self, file_path):
        with open(file_path, "wb") as f:
            pkl.dump(self.transformer_set, f)
    
    def export_video(self, prefix, progbar=tqdm):
        
        frame_num = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        is_exist = False
        for trans in self.transformer_set:
            if trans is not None:
                is_exist = True
                break
        if not is_exist:
            raise ValueError("Please set the transformation information first")
        
        # open video set
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        
        video_trans_set = []
        cap_set = []
        
        ttl_trans_set = []
        ttl_rgb_set = []
        
        date_trans = None
        
        nstack = 0
        for trans in self.transformer_set:
            if trans is None:
                continue
            if trans.type == TTL:
                ttl_trans_set.append(trans)
                ttl_rgb_set.append(np.zeros((frame_num, 3)))
            elif trans.type == VIDEO:
                fname = prefix + "(%d).avi"%(nstack)
                out = cv2.VideoWriter(fname, fourcc, FPS, (trans.max_width, trans.max_height))
                if not out.isOpened():
                    raise ValueError("Cannot open the writable video file")
                cap_set.append(out)
                video_trans_set.append(trans)
                nstack += 1
            elif trans.type == TIME:
                if date_trans is not None:
                    raise ValueError("More than one time frame exists")
                date_trans = trans
                date_set = []
            else: 
                raise ValueError("Unexpected type") 
        
        pbar = progbar(total=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), desc="Exporting video")
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for n in range(frame_num):
            
            frame = self.read_frame()
            if frame is None:
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # video
            for cout, trans in zip(cap_set, video_trans_set):
                warp = trans.transform(frame)
                cout.write(warp)
            # ttl
            for i, trans in enumerate(ttl_trans_set):
                warp = trans.transform(frame)
                ttl_rgb_set[i][n] = warp.mean(axis=0).mean(axis=0)
            
            # time value
            warp = date_trans.transform(frame)
            date_set.append(parse_timestamp(warp))
                
            pbar.update(n=1)
        
        for cout in cap_set:
            cout.release()
        # export TTL
        for i, ttl_rgb in enumerate(ttl_rgb_set):
            fname = prefix+"_ttl(%d).csv"%(i)
            self.save_ttl(ttl_rgb, fname)
        # export TIME
        self.save_datestr(date_set, prefix+"_timestamp.txt")
        # save transform
        self.save_transform(prefix)
            
        pbar.close()
        return True
    
    def save_datestr(self, date_set, fname):
        with open(fname, "w") as fp:
            for time_str, sec_str in date_set:
                fp.write("%s,%s\n"%(time_str, sec_str))
    
    def save_ttl(self, ttl, fname):
        with open(fname, "w") as fp:
            csv_writer = csv.writer(fp)
            for n in range(len(ttl)):
                csv_writer.writerow(ttl[n])
        
    def save_transform(self, prefix):
        with open(prefix+"_trans_option.pkl", "wb", newline='') as fp:
            pkl.dump(self.transformer_set, fp)
    
    def cache_current_transform(self, cache_type):
        if self.transformer is None:
            raise ValueError("Transformation information is not determined. Please run apply first")
        
        self.transformer.type = cache_type
        self.transformer_set.append(self.transformer)
        self.warped_set.append(self.warped)
        self.transformer = None
        
    def delete_cache(self, cid):
        self.transformer_set[cid] = None
        self.warped_set[cid] = None
    
    
def order_points(pts):
    # Convert to np array if needed
    pts = np.array(pts, dtype="float32")

    # Sum of x + y → top-left has the smallest sum, bottom-right the largest
    s = pts.sum(axis=1)
    top_left = pts[np.argmin(s)]
    bottom_right = pts[np.argmax(s)]

    # Difference y - x → top-right has the smallest difference, bottom-left the largest
    diff = np.diff(pts, axis=1)
    top_right = pts[np.argmin(diff)]
    bottom_left = pts[np.argmax(diff)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")


def histogram_equal(image):
    # Color image
    if len(image.shape) == 3:
        ycrcb_array = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        y, cr, cb = cv2.split(ycrcb_array)
        merge_array = cv2.merge([cv2.equalizeHist(y), cr, cb])
        output = cv2.cvtColor(merge_array, cv2.COLOR_YCrCb2RGB)
    # Gray image
    else:
        output = cv2.equalizeHist(image)
    return output


if __name__ == "__main__":
    pass