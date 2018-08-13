#!/usr/bin/env python3

import os, os.path
import itertools
import sys
import argparse
import time

import cv2

class FramesFromImages(object):

    def __init__(self, pattern, startindex, cv2readflag):
        self.filenames = self.get_filenames(pattern, startindex)
        self.cv2readflag = cv2readflag
        if not self.filenames:
            filename = pattern % (startindex,)
            raise ValueError('No such file: %r' % filename)

    def get_filenames(self, pattern, startindex):
        '''Check filesystem for filenames matching pattern'''
        filenames = []
        for index in itertools.count(startindex):
            filename = pattern % (index,)
            if not os.path.exists(filename):
                break
            filenames.append(filename)
        return filenames

    def __getitem__(self, index):
        return cv2.imread(self.filenames[index], self.cv2readflag)

    def __len__(self):
        return len(self.filenames)


class FrameShower(object):

    TRACKBAR = 'Frame (#)'

    def __init__(self, name, frames):
        self.name = name
        self.frames = frames
        self._setting_trackbar = False
        self.current_frame = 1
        self.speed = 10

    def show(self):
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.imshow(self.name, self.frames[0])
        cv2.createTrackbar(self.TRACKBAR, self.name, 1, len(self.frames),
                self.handle_trackbar)
        cv2.createTrackbar('Speed (10^(x/10))', self.name, 10, 100,
                self.handle_speedbar)
        cv2.setMouseCallback(self.name, self.handle_mouse)

        self.controller = PlayController(self)
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


class PlayController(object):

    def __init__(self, shower):
        self.shower = shower
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


class PauseController(object):

    def __init__(self, shower):
        self.shower = shower

    def handle_trackbar(self, frameno):
        self.shower.show_frame(frameno)

    def handle_leftclick(self, x, y):
        self.shower.controller = PlayController(self.shower)

    def tick(self): pass

    def set_speed(self, speed): pass

def show_frames(name, frames):
    FrameShower(name, frames).show()

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('pattern', type=str,
            help='%%-style pattern for the frames')
    parser.add_argument('startindex', type=int, default=1, nargs='?',
            help='index of first frame')
    args = parser.parse_args(args)

    try:
        args.pattern % (args.startindex,)
    except TypeError:
        print()
        print('Invalid pattern: %r' % (args.pattern,))
        print()
        raise

    frames = FramesFromImages(args.pattern, args.startindex, cv2.IMREAD_UNCHANGED)
    name = args.pattern[:20]
    show_frames(name, frames)


if __name__ == "__main__":
    #
    # Run as something like:
    #
    #   $ ./showvid.py folder/vidname%03d.jpg 7
    #
    # This will show frames:
    #
    #   folder/vidname007.jpg
    #   folder/vidname008.jpg
    #   ...
    #
    main(sys.argv[1:])
