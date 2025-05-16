# video_extractor
Crop and extract informations (LED, timestamp) from the video

# Installation
```bash
$ pip install .
```

# Usage
## GUI mode
```bash
$ extract_video
```
In GUI mode, please follow these steps
1) Load video file (select folder icon)
2) select region of interest to be exported
    - **mouse left click**: freely movable four points
    - **mouse right click**: rectangular shape box
    - if you toggle **make_square** button, the rectangle box will be changed to the square box
    - press **Clear** if you want to remove the selection
3) Check selected region by pressing **Apply**
    - If you accept the selected region, please press follow buttons
        - **Add**: cropped is the video to be exported
        - **Add TTL**: cropped region is RGB TTL signal
        - **Add timestamp**: cropped region shows timestamp (Please include delta t together)
    - If you don't want to accep the region, please select "reset" button
4) If you added cropped region, the item will be shown in the top-right area.
5) Repeat 2-3 to select all the regions. If you wronly added, press the target item (the color of the selected item will be changed to blue). Then, press **Delete** button.
6) After selection, please press **Export** button to export"
    - Select export file name (don't put extension such as .avi to file name)
    - The pop will be shown. Select all the dataset that you want to export.
    - If you just keep the information about the selected region (not processing), uncheck the item. This will be helpful when you need to convert timestamp dataset, because it takes long times to be processed. After selecting timestamp region, you can run program with CLI method to process all the timestamp overnight.
- The output file will be...
    - Encoded video: <prefix>(%d).avi
    - RGB value of TTL: <prefix>_ttl(%d).csv
    - timestamp: <prefix>_timestamp(%d).txt
    - transformation information: <prefix>_trans_option.pkl
- If you want to reuse information about selected region, use CLI mode.

## CLI mode
```bash
$ extract_video --use_cli --transform=<transformation info file name> --fout=<prefix to be exported>
```
If you want to skip specific file types, please use these options
1) video export: --skip_video
2) TTL export: --skip_ttl
3) timestamp export: --skip_timestamp

For example, if you want to only process timestamp information, you can type the command as
```
$ extract_video --use_cli --transform="./data_trans_option(5).pkl" --fout="./test_export" --skip_video --skip_ttl
```
