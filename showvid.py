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


def show_frames(name, frames):

    def show_frame(frameno):
        nonlocal current_frame
        current_frame = frameno
        index = max(frameno - 1, 0)
        cv2.imshow(name, frames[index])
        cv2.setTrackbarPos('Frame #', name, frameno)

    def start_playing():
        nonlocal playing, time_started
        playing = True
        time_started = time.time() - current_frame / fps

    def stop_playing():
        nonlocal playing, time_started
        playing = False
        time_started = None

    def handle_trackbar(frameno):
        if not playing:
            show_frame(frameno)

    def mouse_handler(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if playing:
                stop_playing()
            else:
                start_playing()

    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar('Frame #', name, 1, len(frames), handle_trackbar)
    cv2.setMouseCallback(name, mouse_handler)

    current_frame = 1
    time_started = None
    playing = False
    fps = 25

    start_playing()

    while 1:
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
        if playing:
            new_time = time.time()
            expected_frame = int(fps * (new_time - time_started))
            if expected_frame != current_frame:
                show_frame(expected_frame)

    cv2.destroyAllWindows()

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
