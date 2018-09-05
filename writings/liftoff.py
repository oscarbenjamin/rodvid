#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

PILATEX = {
    0:'0',
    np.pi: r'\pi',
    np.pi/2: r'\frac{\pi}{2}',
    np.pi/3: r'\frac{\pi}{3}',
    np.pi/4: r'\frac{\pi}{4}',
}
for x, l in list(PILATEX.items()):
    if x != -x:
        PILATEX[-x] = '-' + PILATEX[x]

def set_ticks(axis, nums, **kwargs):
    axis.set_ticks(nums)
    axis.set_ticklabels(['$%s$' % PILATEX[x] for x in nums], **kwargs)

def main(filename=None):
    fig = plt.figure(figsize=(3, 3))
    ax = fig.add_axes([0.20, 0.20, 0.60, 0.60])

    theta = np.linspace(-np.pi/2, np.pi/2, 101)
    alpha = 1/12.
    props = {'linewidth':2, 'color':'black'}
    ax.plot(theta, +(4*alpha + np.cos(theta)**2)/np.cos(theta), **props)
    ax.plot(theta, -(4*alpha + np.cos(theta)**2)/np.cos(theta), **props)

    ax.set_xlim([-np.pi/2, np.pi/2])
    ax.set_ylim([-3, 3])
    set_ticks(ax.xaxis, [-np.pi/2, -np.pi/4, 0, np.pi/4, np.pi/2])

    ax.set_xlabel(r'$\theta$')
    ax.set_ylabel(r'$\frac{\dot{\theta}}{\omega}$', rotation=0)
    ax.grid()

    if filename is not None:
        fig.savefig(filename)
    else:
        plt.show()

if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
