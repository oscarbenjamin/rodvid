'''
    GUI for selecting outline of the shape
'''
import sys
from math import atan2, pi, cos, sin

import cv2
from scipy.optimize import minimize
from scipy.interpolate import RegularGridInterpolator
import numpy as np

from .frames import frames_from_argv
from .shower import FrameShower, BaseController
from .filters import SobelAbsFilter, BlurFilter, CompressFilter, SharpenFilter


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
        frame = frame.copy()
        self.draw_on_top(frame)
        super().draw_frame(frame)

    def draw_on_top(self, frame):
        cv2.rectangle(frame, (self.xstart, self.ystart), (self.x, self.y), 255, 3)


class RodShape(object):

    LENGTH = 100 # mm length
    RADIUS = 10 # mm radius
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)

    def __init__(self, xc, yc, theta, scale):
        self.xc = xc
        self.yc = yc
        self.theta = theta
        self.scale = scale
        self.points = []

    def __str__(self):
        return 'RodShape(%r, %r, %r, %r)' % (self.xc, self.yc, self.theta, self.scale)

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

    def generate_points(self, npoints):
        N1 = 3 * npoints // 8
        N2 = npoints // 8
        ll, lc, lr, ul, uc, ur = self.corners()
        points = []
        for (xstart, ystart), (xend, yend) in [(ll, ul), (lr, ur)]:
            for n in range(1, N1):
                alpha = n / N1
                x = (1-alpha)*xstart + alpha*xend
                y = (1-alpha)*ystart + alpha*yend
                points.append((x, y))
        for centre, angle in ((lc, self.theta + pi/2), (uc, self.theta - pi/2)):
            for n in range(N2+1):
                xc, yc = centre
                theta = angle + n/N2 * pi
                R = self.scale * self.RADIUS
                x = xc + R*cos(theta)
                y = yc + R*sin(theta)
                points.append((x, y))
        self.points = points


    def draw(self, img):
        ll, lc, lr, ul, uc, ur = self.corners()
        for (x1, y1), (x2, y2) in ((ll, lr), (lr, ur), (ur, ul), (ul, ll)):
            p1 = (int(round(x1)), int(round(y1)))
            p2 = (int(round(x2)), int(round(y2)))
            cv2.line(img, p1, p2, self.GREEN, 1)
        R_pix = int(round(self.scale * self.RADIUS))
        theta_deg = self.theta * 180 / pi
        x1, y1 = uc
        cv2.ellipse(img, (int(x1), int(y1)), (R_pix, R_pix), theta_deg - 90,
                0, 180, self.GREEN, 1)
        x1, y1 = lc
        cv2.ellipse(img, (int(x1), int(y1)), (R_pix, R_pix), theta_deg + 90,
                0, 180, self.GREEN, 1)


class RodSelectController(DragController):

    def draw_on_top(self, frame):
        if self.dragging:
            self.shape = RodShape.from_xypair(self.xstart, self.ystart, self.x, self.y)
            self.shape.draw(frame)
        elif hasattr(self, 'shape'):
            self.shape.draw(frame)

    def handle_leftup(self, x, y):
        super().handle_leftup(x, y)
        import cProfile, pstats

        profiler = cProfile.Profile()    # create profiler
        profiler.enable()                # start profiling

        self.shape = fit_shape(self.frame, self.shape)
        profiler.disable()               # end profiling

        pstat_profile = pstats.Stats(profiler, stream=sys.stdout) # create a pstats object from the profile bound to a file stream
        pstat_profile.sort_stats('cumulative')
        pstat_profile.print_stats() # print stats to a file

        self.shape.generate_points(100)
        self.points = self.shape.points
        self.redraw()

def fit_shape(frame, shape):
    if len(frame.shape) == 3:
        frame = frame[:,:,0]

    x = np.arange(frame.shape[1])
    y = np.arange(frame.shape[0])
    f = RegularGridInterpolator((y, x), frame, bounds_error=False, fill_value=0)

    def objective(X):
        xc, yc, theta, scale = X
        test_shape = RodShape(xc, yc, theta, scale)
        test_shape.generate_points(1000)
        points = test_shape.points
        points = np.array([[y, x] for x, y in points])
        return - sum(f(points))

    X0 = shape.xc, shape.yc, shape.theta, shape.scale

    ret = minimize(objective, X0, method='powell')
    #ret = minimize(objective, X0, method='Nelder-Mead')
    if not ret.success:
        print(ret)

    return RodShape(*ret.x)

def interp_pixel(frame, x, y):
    if not (0 < x < frame.shape[1]-1 and 0 < y < frame.shape[0]-1):
        return 0
    x1 = int(x)
    y1 = int(y)
    x2 = x1 + 1
    y2 = y1 + 1
    dx = x - x1
    dy = y - y1
    pixel = ( frame[y1, x1]*(1-dx)*(1-dy)
            + frame[y2, x1]*dx*(1-dy)
            + frame[y1, x2]*(1-dx)*dy
            + frame[y2, x2]*dx*dy)
    return pixel


def main(argv):
    name, frames = frames_from_argv(argv)

    frames = SobelAbsFilter(frames, ksize=5)
    #frames = SharpenFilter(frames, None)
    #frames = BlurFilter(frames, ksize=5)
    #frames = CompressFilter(frames, None)

    shower = FrameShower(name, frames)
    controller = RodSelectController(shower)
    shower.show(controller)

if __name__ == "__main__":
    main(sys.argv[1:])
