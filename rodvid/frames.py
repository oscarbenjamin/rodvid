'''
    frames.py

    Defines the FramesFromImages class which exposes a sequence interface for
    the frames in a folder full of images.
'''

import os
import os.path
import argparse
import itertools

import cv2


class FramesFromImages(object):

    def __init__(self, pattern, startindex, cv2readflag=None):
        self.filenames = self.get_filenames(pattern, startindex)
        if cv2readflag is None:
            cv2readflag = cv2.IMREAD_UNCHANGED
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


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('pattern', type=str,
            help='%%-style pattern for the frames')
    parser.add_argument('startindex', type=int, default=1, nargs='?',
            help='index of first frame')
    return parser


def get_frames_from_parsed_args(args):
    try:
        args.pattern % (args.startindex,)
    except TypeError:
        print()
        print('Invalid pattern: %r' % (args.pattern,))
        print()
        raise
    return FramesFromImages(args.pattern, args.startindex)


def frames_from_argv(argv):
    parser = get_argument_parser()
    args = parser.parse_args(argv)
    frames = get_frames_from_parsed_args(args)
    name = args.pattern[:20]
    return name, frames


def main(argv):
    name, frames = frames_from_argv(argv)
    print('%s : %d frames' % (name, len(frames)))


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
