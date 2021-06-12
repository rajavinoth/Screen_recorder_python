import cv2
import numpy as np
import pyautogui
import threading
import audio_recorder
from mouse_movement import get_cursor, add_mouse
import mss
import os
import io
import PIL.Image as Image
import shutil


screenWidth, screenHeight = pyautogui.size()
SCREEN_SIZE = (screenWidth, screenHeight)

fourcc = cv2.VideoWriter_fourcc(*"XVID")

out = cv2.VideoWriter("output.avi", fourcc, 30.0, (SCREEN_SIZE))

intruction_note = ''
my_Recorder = audio_recorder.Recode_audio()


frame_list = []

def rec_video():
    my_Recorder.on_rec()
    while True:
        # make a screenshot
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = bytearray(frame)
        with mss.mss() as sct:
            screen = sct.monitors[0]
        img_with_mouse = add_mouse(img, screen['width'])
        frame_list.append(img_with_mouse)
        if intruction_note == "stop":
            print('sstop')
            my_Recorder.on_stop()
            process_video(frame_list)
            break
    # make sure everything is closed when exited
    # cv2.destroyAllWindows()
    out.release()

def process_video(frame_list):
    print('Inside save')
    frame_count = 1
    try:
        shutil.rmtree('temp')
    except:
        print('Folder Not exists or file may open in other application!')
    try:
        os.mkdir('temp')
    except:
        print('Folder Already Exists!')
    for img in frame_list:
        raw_image = mss.tools.to_png(img, (1920, 1080))
        img_with_mouse = Image.open(io.BytesIO(raw_image))
        img_with_mouse = np.array(img_with_mouse)
        out.write(img_with_mouse)
        out.write(img_with_mouse)
        frame_count += 1
    print('Process Done')
    return 1

t1 = threading.Thread(target=rec_video, args=())
# t2 = threading.Thread(target=my_Recorder.on_rec(), args=())

def startprogram():
    # starting thread 1
    print('Start1')
    t1.start()
    # starting thread 2
    print('Start2')
    # t2.start()
    print('Started')
    # wait until thread 1 is completely executed
    # t1.join()
    # wait until thread 2 is completely executed
    # t2.join()

while True:
    ab = input('Enter your instruction:')
    if ab == 'stop':
        print('set stop')
        intruction_note = "stop"
    elif ab == 'start':
        startprogram()
    elif ab == 'close':
        break