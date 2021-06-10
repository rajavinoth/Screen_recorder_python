import cv2
import numpy as np
import pyautogui
import sounddevice as sd
import threading
import audio_recorder
from datetime import datetime

screenWidth, screenHeight = pyautogui.size()
SCREEN_SIZE = (screenWidth, screenHeight)

fourcc = cv2.VideoWriter_fourcc(*"XVID")

out = cv2.VideoWriter("output.avi", fourcc, 20.0, (SCREEN_SIZE))


#audio setup
fs = 44100
sd.default.samplerate = fs
sd.default.channels = 1
duration = 3600  # seconds
intruction_note = ''
stream = None
my_Recorder = audio_recorder.Recode_audio()


def rec_video():
    my_Recorder.on_rec()
    frame_count = 1
    while True:
        # make a screenshot
        img = pyautogui.screenshot()
        #to capture perticular region
        # img = pyautogui.screenshot(region=(0, 0, 300, 400))
        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(img)
        # convert colors from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # write the frame
        print(frame_count)
        print(datetime.now())
        out.write(frame)
        frame_count += 1
        # show the frame
        # cv2.imshow("screenshot", frame)
        # if the user clicks q, it exits
        if intruction_note == "stop":
            print('sstop')
            # sd.stop()
            my_Recorder.on_stop()
            break

    # make sure everything is closed when exited
    cv2.destroyAllWindows()
    out.release()


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


# both threads completely executed
print("Done!")