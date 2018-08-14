'''
    GUI for selecting outline of the shape
'''
import sys
from math import atan2, pi

import cv2

from .frames import frames_from_argv
from .shower import FrameShower, BaseController


class DragController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dragging = False
        self.frame = self.xstart = self.ystart = None

    def handle_leftclick(self, x, y):
        self.xstart = x
        self.ystart = y
        self.x = x
        self.y = y
        self.dragging = True
        self.redraw()

    def handle_leftup(self, x, y):
        self.dragging = False

    def handle_mousemove(self, x, y):
        if self.dragging:
            self.x = x
            self.y = y
            self.redraw()

    def redraw(self):
        self.draw_frame(self.frame)

    def draw_frame(self, frame):
        if len(frame.shape) == 2:
            frame = cv2.merge((frame, frame, frame))
        self.frame = frame
        if self.dragging:
            frame = frame.copy()
            self.draw_on_top(frame)
        super().draw_frame(frame)

    def draw_on_top(self, frame):
        cv2.rectangle(frame, (self.xstart, self.ystart), (self.x, self.y), 255, 3)


class RodSelectController(DragController):
    def draw_on_top(self, frame):
        deltax = self.x - self.xstart
        deltay = self.y - self.ystart
        pixel_distance = (deltax ** 2 + deltay ** 2) ** 0.5
        theta = pi/2 - atan2(deltax, deltay)
        theta_deg = theta * 180 / pi
        pixels_per_mm = pixel_distance / 200
        pixel_diameter = int(round(20 * pixels_per_mm))

        cv2.ellipse(frame, (self.x, self.y), (pixel_diameter, pixel_diameter),
                theta_deg - 90, 0, 180, (0, 255, 0), 2)
        cv2.ellipse(frame, (self.xstart, self.ystart), (pixel_diameter,
            pixel_diameter), theta_deg + 90, 0, 180, (0, 255, 0), 2)


def main(argv):
    name, frames = frames_from_argv(argv)

    shower = FrameShower(name, frames)
    controller = RodSelectController(shower)
    shower.show(controller)

if __name__ == "__main__":
    main(sys.argv[1:])
