import sys
import time

import cv2

from .frames import frames_from_argv
from .shower import FrameShower, BaseController

class PlayController(BaseController):

    def __init__(self, shower):
        super().__init__(shower)
        self.fps = 25
        self.restart()

    def handle_trackbar(self, frameno):
        self.shower.show_frame(frameno)
        self.restart()

    def set_speed(self, speed):
        self.restart()

    def pause(self):
        self.shower.controller = PauseController(self.shower)

    def handle_leftclick(self, x, y):
        self.pause()

    def restart(self):
        self.start_frame = self.shower.current_frame
        self.start_time = time.time()

    def tick(self):
        frames_shown = int(self.fps * (time.time() - self.start_time))
        expected_frame = self.start_frame + self.shower.speed * frames_shown
        if expected_frame != self.shower.current_frame:
            if expected_frame >= len(self.shower.frames):
                self.pause()
                return
            self.shower.show_frame(expected_frame)


class PauseController(BaseController):
    def handle_leftclick(self, x, y):
        self.shower.controller = PlayController(self.shower)


def play_frames(name, frames):
    shower = FrameShower(name, frames)
    controller = PlayController(shower)
    shower.show(controller)

def main(argv):
    name, frames = frames_from_argv(argv)
    play_frames(name, frames)


if __name__ == "__main__":
    main(sys.argv[1:])
