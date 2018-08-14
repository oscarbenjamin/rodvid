'''
    edge.py

    Defines edge filter to be used on various frame objects
'''

import sys

import cv2
import numpy as np

from .frames import get_argument_parser, get_frames_from_parsed_args
from .play import play_frames


class Filter(object):

    def __init__(self, frames):
        self.frames = frames

    def filter(self):
        raise NotImplementedError('Subclasses should override this')

    def __getitem__(self, index):
        return self.filter(self.frames[index])

    def __len__(self):
        return len(self.frames)


class EdgeFilter(Filter):
    def __init__(self, frames, ksize, dtype=cv2.CV_64F):
        super().__init__(frames)
        self.dtype = dtype
        self.ksize = ksize


class LaplacianFilter(EdgeFilter):
    def filter(self, frame):
        frame_filt = cv2.Laplacian(frame, self.dtype, ksize=self.ksize)
        frame_filt /= frame_filt.max()
        return frame_filt


class LaplacianAbsFilter(EdgeFilter):
    def filter(self, frame):
        frame_filt = cv2.Laplacian(frame, self.dtype, ksize=self.ksize)
        frame_filt = np.abs(frame_filt)
        frame_filt /= frame_filt.max()
        return frame_filt


class SobelAbsFilter(EdgeFilter):
    def filter(self, frame):
        frame_dx = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=5)
        frame_dy = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=5)
        frame_mag = np.abs(frame_dx) + np.abs(frame_dy)
        frame_mag /= frame_mag.max()
        return frame_mag


choices = {
    'laplacian': LaplacianFilter,
    'laplacian-abs': LaplacianAbsFilter,
    'sobel-abs': SobelAbsFilter,
}


def main(argv):
    parser = get_argument_parser()

    parser.add_argument('--filter', type=str, default='laplacian', choices=choices)
    parser.add_argument('--ksize', type=int, default=5)

    args = parser.parse_args(argv)
    frames = get_frames_from_parsed_args(args)
    name = args.pattern[:20]

    frames_filt = choices[args.filter](frames, ksize=args.ksize)

    play_frames(name, frames_filt)

if __name__ == "__main__":
    main(sys.argv[1:])
