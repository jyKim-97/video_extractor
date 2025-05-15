import pytesseract
import cv2
from datetime import datetime

fname = "E:\\exp_day03_trial2_m02_f03\\exp_day03_2_m02_f03.mkv"

def main():
    cap = cv2.VideoCapture(fname)
    # print(cap.isOpened())
    
    _, frame = cap.read()
    
    frame = frame[:100, 1600:, :]
    print(parse_timestamp(frame))
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    
    # # cv2.imshow("Test", frame)
    # # cv2.imshow("Test", thresh)
    # # cv2.waitKey(0)    
    # # cv2.destroyAllWindows()
    
    # # 
    # custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:/.,msΔt'
    # text = pytesseract.image_to_string(thresh, config=custom_config)
    # text = text.split("\n")
    # print(text)
    
    # timestamp = text[0]
    # dt =  datetime.strptime(timestamp, "%y:%m:%d/%H:%M:%S.%f")
    # print(dt)
    
    # # time_str = "17:41:53.782"
    # # t = datetime.strptime(time_str, "%H:%M:%S.%f").time()

    # # Convert to seconds since midnight
    # total_seconds = dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1_000_000
    # print(total_seconds)
    # date_str, clock_str = timestamp.split('/')
    # print(date_str)
    # dt_date = datetime.strptime(date_str, "%y:%m:%d")
    # dt_clock = datetime.strptime(clock_str, "%H:%M:%S.%f")
    # # print(dt_date, dt)
    # dt = dt_date + dt_clock
    # print(dt)

    
    # print(date_str)
    # dt = datetime.strptime(date_str, "%Y:%m:%d/%H:%M:%S.%f")
    # print(dt)

def parse_timestamp(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:/.,msΔt'
    text = pytesseract.image_to_string(thresh, config=custom_config)
    text = text.split("\n")
    
    timestamp = text[0]
    dt = datetime.strptime(timestamp, "%y:%m:%d/%H:%M:%S.%f")
    
    time_str = dt.strftime("%H:%M:%S.%f")
    sec = dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1_000_000
    
    return time_str, sec
    

if __name__ == "__main__":
    main()