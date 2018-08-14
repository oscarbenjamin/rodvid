'''
    GUI for selecting outline of the shape
'''
import sys
from math import atan2, pi, cos, sin

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


class RodShape(object):

    LENGTH = 100 # mm length
    RADIUS = 10 # mm radius
    GREEN = (0, 255, 0)

    def __init__(self, xc, yc, theta, scale):
        self.xc = xc
        self.yc = yc
        self.theta = theta
        self.scale = scale

    @classmethod
    def from_xypair(cls, x1, y1, x2, y2):
        if y2 > y1:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        delta_x = x2 - x1
        delta_y = y2 - y1
        theta = atan2(delta_y, delta_x)
        scale = (delta_x**2 + delta_y**2)**0.5 / cls.LENGTH
        xc = x1 + delta_x / 2
        yc = y1 + delta_y / 2
        return RodShape(xc, yc, theta, scale)

    def corners(self):
        c = cos(self.theta)
        s = sin(self.theta)
        L = self.scale * self.LENGTH / 2
        R = self.scale * self.RADIUS
        lower_centre = x1, y1 = (self.xc - L*c, self.yc - L*s)
        upper_centre = x2, y2 = (self.xc + L*c, self.yc + L*s)
        lower_left  = (x1 - R*s, y1 + R*c)
        lower_right = (x1 + R*s, y1 - R*c)
        upper_left  = (x2 - R*s, y2 + R*c)
        upper_right = (x2 + R*s, y2 - R*c)
        return (lower_left, lower_centre, lower_right, upper_left,
                upper_centre, upper_right)

    def draw(self, img):
        ll, lc, lr, ul, uc, ur = self.corners()
        for (x1, y1), (x2, y2) in ((ll, lr), (lr, ur), (ur, ul), (ul, ll)):
            p1 = (int(round(x1)), int(round(y1)))
            p2 = (int(round(x2)), int(round(y2)))
            cv2.line(img, p1, p2, self.GREEN, 2)
        R_pix = int(round(self.scale * self.RADIUS))
        theta_deg = self.theta * 180 / pi
        x1, y1 = uc
        cv2.ellipse(img, (int(x1), int(y1)), (R_pix, R_pix), theta_deg - 90, 0, 180, self.GREEN, 2)
        x1, y1 = lc
        cv2.ellipse(img, (int(x1), int(y1)), (R_pix, R_pix), theta_deg + 90, 0, 180, self.GREEN, 2)


class RodSelectController(DragController):
    def draw_on_top(self, frame):
        shape = RodShape.from_xypair(self.xstart, self.ystart, self.x, self.y)
        shape.draw(frame)


def main(argv):
    name, frames = frames_from_argv(argv)

    shower = FrameShower(name, frames)
    controller = RodSelectController(shower)
    shower.show(controller)

if __name__ == "__main__":
    main(sys.argv[1:])
