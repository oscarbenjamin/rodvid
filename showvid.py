#!/usr/bin/env python3

import sys
from rodvid.play import main

def edge_filter(img):
    #img_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
    #img_y = cv3.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)
    #img_mag = np.abs(img_x) + np.abs(img_y)
    img_mag = cv2.Laplacian(img, cv2.CV_64F, ksize=5)
    img_mag /= img_mag[:].max()
    return img_mag

if __name__ == "__main__":
    main(sys.argv[1:])
