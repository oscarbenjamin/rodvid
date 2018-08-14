import sys

import cv2

from .frames import frames_from_argv


class FrameShower(object):

    TRACKBAR = 'Frame (#)'

    def __init__(self, name, frames):
        self.name = name
        self.frames = frames
        self._setting_trackbar = False
        self.current_frame = 1
        self.speed = 10

    def show(self, controller):
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.imshow(self.name, self.frames[0])
        cv2.createTrackbar(self.TRACKBAR, self.name, 1, len(self.frames),
                self.handle_trackbar)
        cv2.createTrackbar('Speed (10^(x/10))', self.name, 10, 100,
                self.handle_speedbar)
        cv2.setMouseCallback(self.name, self.handle_mouse)

        self.controller = controller
        self.event_loop()

        cv2.destroyAllWindows()

    def event_loop(self):
        while 1:
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                return
            else:
                self.controller.tick()

    def show_frame(self, frameno):
        self.set_trackbar(frameno)
        index = max(frameno-1, 0)
        cv2.imshow(self.name, self.frames[index])
        self.current_frame = frameno

    def handle_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.controller.handle_leftclick(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.controller.handle_leftup(x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            self.controller.handle_mousemove(x, y)

    def set_trackbar(self, frameno):
        self._setting_trackbar = True
        cv2.setTrackbarPos(self.TRACKBAR, self.name, frameno)
        self._setting_trackbar = False

    def handle_trackbar(self, frameno):
        if self._setting_trackbar:
            return
        self.controller.handle_trackbar(frameno)

    def handle_speedbar(self, speed):
        self.speed = speed
        self.controller.set_speed(speed)

class BaseController(object):

    def __init__(self, shower):
        self.shower = shower

    def handle_trackbar(self, frameno):
        self.shower.show_frame(frameno)

    def handle_leftclick(self, x, y): pass
    def handle_leftup(self, x, y): pass
    def handle_mousemove(self, x, y): pass
    def tick(self): pass
    def set_speed(self, speed): pass


def show_frames(name, frames):
    shower = FrameShower(name, frames)
    controller = BaseController(shower)
    shower.show(controller)


def main(argv):
    name, frames = frames_from_argv(argv)
    show_frames(name, frames)


if __name__ == "__main__":
    main(sys.argv[1:])
