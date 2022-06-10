# import the necessary packages
from queue import Queue
import io
import dbus

try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except ImportError:
    print("PiCamera or cv2 not installed")

import time

# constants
FRAME_SIZE = 510
FRAMERATE = 24
HEIGHT = 640
WIDTH = 480

class Camera:
    capturing = False
    queue = Queue(0)

    def __init__(self):

        try:
            # initialize the camera and grab a reference to the raw camera capture
            self.camera = PiCamera()
            self.camera.resolution = (HEIGHT, WIDTH)
            self.camera.framerate = FRAMERATE
        except:
            print("Cannot create PiCamera")
            self.counter = 0

        # allow the camera to warmup
        time.sleep(0.1)

    def parse(self, buffer):
        print("Parse frame")
        print("Length: " + len(buffer))
        parsedBytes = 0

        while (parsedBytes < len(buffer)):
            print("ParsedBytes: " + parsedBytes)
            frame = []
            if (len(buffer) - parsedBytes) > FRAME_SIZE:
                frame[0] = 1
                frame[1:] = buffer[parsedBytes: (parsedBytes + FRAME_SIZE)]
                parsedBytes += FRAME_SIZE
            else:
                frame[0] = 0
                frame[1:] = buffer[parsedBytes:]
                parsedBytes += len(buffer) - parsedBytes
                
            self.queue.put(frame)

    def run(self):
        try:
            self.capturing = True
            # capture frames from the camera
            stream = io.BytesIO()
            for frame in self.camera.capture_continuous(stream, format="jpeg", use_video_port=True):
                if self.capturing:
                    stream.seek(0)
                    
                    self.parse(stream.read())

                    stream.seek(0)
                    stream.truncate()
                else:
                    break
            
            stream.close()
        except:
            print("Camera Run Error")

    def get(self):
        if self.queue.empty():
            if (not hasattr(self, "camera")):
                self.counter = self.counter + 1
                return bytearray(str(self.counter), "utf-8")
            else:
                stream = io.BytesIO()
                self.camera.capture(stream, format="rgb", use_video_port=True)
                
                stream.seek(0)
                self.parse(stream.read())
                stream.seek(0)
                stream.close()
                return self.queue.get()
        else:
            return self.queue.get()

    def stop(self):
        self.capturing = False

    def close(self):
        if hasattr(self, "camera"):
            self.camera.close()