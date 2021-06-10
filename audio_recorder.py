import numpy as np
import sounddevice as sd
import soundfile as sf
import queue
import threading

class Recode_audio():
    def __init__(self):
        super().__init__()
        self.stream = None
        self.recording = self.previously_recording = False
        self.audio_q = queue.Queue()
        self.peak = 0
        self.metering_q = queue.Queue(maxsize=1)
        self.input_overflows = 0
        self.create_stream()
        # while True:
        #     x = input('Enter process :')
        #     if x == 'start':
        #         self.on_rec()
        #     elif x == 'stop':
        #         self.on_stop()
        #     elif x == 'close':
        #         break

    def create_stream(self, device=None):
        if self.stream is not None:
            self.stream.close()
        self.stream = sd.InputStream(
            device=device, channels=1, callback=self.audio_callback)
        self.stream.start()

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status.input_overflow:
            # NB: This increment operation is not atomic, but this doesn't
            #     matter since no other thread is writing to the attribute.
            self.input_overflows += 1
            # NB: self.recording is accessed from different threads.
            #     This is safe because here we are only accessing it once (with a
            #     single bytecode instruction).
        if self.recording:
            self.audio_q.put(indata.copy())
            self.previously_recording = True
        else:
            if self.previously_recording:
                self.audio_q.put(None)
                self.previously_recording = False

        self.peak = max(self.peak, np.max(np.abs(indata)))
        try:
            self.metering_q.put_nowait(self.peak)
        except queue.Full:
            pass
        else:
            self.peak = 0


    def on_rec(self):
            self.recording = True

            filename = 'myfile.wav'

            if self.audio_q.qsize() != 0:
                print('WARNING: Queue not empty!')
            self.thread = threading.Thread(
                target=self.file_writing_thread,
                kwargs=dict(
                    file=filename,
                    mode='x',
                    samplerate=int(self.stream.samplerate),
                    channels=self.stream.channels,
                    q=self.audio_q,
                ),
            )
            self.thread.start()

    def on_stop(self, *args):
        self.recording = False


    def _wait_for_thread(self):
        if self.thread.is_alive():
            self.wait_for_thread()
            return
        self.thread.join()

    def file_writing_thread(self, *, q, **soundfile_args):
        """Write data from queue to file until *None* is received."""
        # NB: If you want fine-grained control about the buffering of the file, you
        #     can use Python's open() function (with the "buffering" argument) and
        #     pass the resulting file object to sf.SoundFile().
        with sf.SoundFile(**soundfile_args) as f:
            while True:
                data = q.get()
                if data is None:
                    break
                f.write(data)
