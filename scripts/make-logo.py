#!/usr/bin/env python3

import argparse
import math
from collections import namedtuple


# default settings

width = 160
height = 160
stroke = 14
gap = 8
m_angle = 60.0
w_angle = 60.0
color = "black"
bg_color = None
o_color = color
o_fill_color = None
m_color = color
w_color = color


parser = argparse.ArgumentParser(
    description="generate an SVG for the logo or favicon")
parser.add_argument('--favicon', action='store_true',
                    help='set defaults for favicon')
args = parser.parse_args()

if args.favicon:
    import sys
    print('NOTE: to make a 16x16 favicon from the SVG, try this:\n'
          '  $ convert -resize 16x16 -background none file.svg favicon.ico\n'
          'This assumes you have imagemagick installed',
          file=sys.stderr)
    stroke = 10
    gap = 10
    o_color = m_color = w_color = "#2244AA"
    o_fill_color = "white"


# these will adjust based on selected settings

o_radius = (width - stroke) / 2
m_radius = o_radius - stroke - gap
w_radius = m_radius - stroke - gap

m_l_angle = 90 + (m_angle / 2)
m_r_angle = 90 - (m_angle / 2)
w_l_angle = 270 - (w_angle / 2)
w_r_angle = -w_angle

m_outer = m_radius + (stroke / 2)
m_inner = m_radius - (stroke / 2)
w_outer = w_radius + (stroke / 2)
w_inner = w_radius - (stroke / 2)
m_w_gap = m_inner - w_outer

Point = namedtuple('Point', 'x y')

def p2e(radius, angle):
    """convert polar coordinates to euclidean"""
    radians = math.radians(angle)
    return Point(round(radius * math.cos(radians), 2),
                 round(-radius * math.sin(radians), 2))

def adjust_angle(h, o=None):
    """
    find the angle such that *o* is the opposite length at hypotenuse *h*
    """
    if o is None:
        o = float(stroke) / 2
    else:
        o = float(o)
    return math.degrees(math.asin(o/h))

### preamble

print('<?xml version="1.0" standalone="no"?>')
print('<svg width="{}" height="{}"'.format(width, height))
print('     xmlns="http://www.w3.org/2000/svg" version="1.1">')
if bg_color:
    print('  <rect x="0" y="0" width="{}" height="{}" fill="{}" />'
          .format(width, height, bg_color))
print('  <g transform="translate({}, {})">'.format(width/2, height/2))

### O is just a circle

print('    <circle id="o" cx="0" cy="0" r="{}"'.format(o_radius))
print('            stroke="{}" stroke-width="{}" fill="{}" />'
      .format(o_color, stroke, 'none' if not o_fill_color else o_fill_color))

### M is a path

#     m2       m5
#   /    \   /    \
#  | m11 m3-m4 m8 |
#  |   |\     /|  |
#  |   |m10-m9 |  |
#  m1-m12      m7-m6

m1 = p2e(m_outer, w_l_angle + adjust_angle(m_outer))
m2 = p2e(m_outer, m_l_angle - adjust_angle(m_outer))
dy = m2.y + gap/2 + stroke
dx = -(dy * math.tan(math.radians(m_angle / 2)))
m3 = Point(m2.x + dx, m2.y - dy)
m4 = Point(-m3.x, m3.y)
m5 = Point(-m2.x, m2.y)
m6 = Point(-m1.x, m1.y)
m7 = p2e(m_inner, w_r_angle - adjust_angle(m_inner))
m8 = p2e(m_inner, m_r_angle - adjust_angle(m_inner))
dy = m8.y  + gap/2
dx = -(dy * math.tan(math.radians(m_angle / 2)))
m9 = Point(m8.x - dx, m8.y - dy)
m10= Point(-m9.x, m9.y)
m11= Point(-m8.x, m8.y)
m12= Point(-m7.x, m7.y)

print('    <path id="m" d="')
print('      M {0.x} {0.y}'.format(m1))
print('      A {0} {0} 0 0 1 {1.x} {1.y}'.format(m_outer, m2))
print('      L {0.x} {0.y}'.format(m3))
print('      H {0.x}'.format(m4))
print('      L {0.x} {0.y}'.format(m5))
print('      A {0} {0} 0 0 1 {1.x} {1.y}'.format(m_outer, m6))
print('      L {0.x} {0.y}'.format(m7))
print('      A {0} {0} 0 0 0 {1.x} {1.y}'.format(m_inner, m8))
print('      L {0.x} {0.y}'.format(m9))
print('      H {0.x}'.format(m10))
print('      L {0.x} {0.y}'.format(m11))
print('      A {0} {0} 0 0 0 {1.x} {1.y}'.format(m_inner, m12))
print('      Z"')
print('      stroke="{0}" stroke-width="0" fill="{0}" />'.format(m_color))

### W is a path

# w2-w3           w8-w9
# |  |  w5-----w6 |  |
# |  | /        \ |  |
# |  w4 w12-w11 w7  |
#  \    /     \    /
#    w1        w10

w1 = p2e(w_outer, w_l_angle + adjust_angle(w_outer))
w2 = p2e(w_outer, m_l_angle + adjust_angle(w_outer, o=(stroke/2)+gap))
w3 = Point(w2.x + stroke * math.sin(math.radians(m_angle / 2)),
           w2.y + stroke * math.cos(math.radians(m_angle / 2)))
w4 = p2e(w_inner, w_l_angle - adjust_angle(w_inner))
dy = w4.y - gap/2
dx = -(dy * math.tan(math.radians(w_angle / 2)))
w5 = Point(w4.x - dx, w4.y - dy)
w6 = Point(-w5.x, w5.y)
w7 = Point(-w4.x, w4.y)
w8 = Point(-w3.x, w3.y)
w9 = Point(-w2.x, w2.y)
w10= Point(-w1.x, w1.y)
dy = w10.y - gap/2 - stroke
dx = dy * math.tan(math.radians(w_angle / 2))
w11= Point(w10.x - dx, w10.y - dy)
w12= Point(-w11.x, w11.y)

print('    <path id="w" d="')
print('      M {0.x} {0.y}'.format(w1))
print('      A {0} {0} 0 0 1 {1.x} {1.y}'.format(w_outer, w2))
print('      L {0.x} {0.y}'.format(w3))
print('      A {0} {0} 0 0 0 {1.x} {1.y}'.format(w_inner, w4))
print('      L {0.x} {0.y}'.format(w5))
print('      L {0.x} {0.y}'.format(w6))
print('      L {0.x} {0.y}'.format(w7))
print('      A {0} {0} 0 0 0 {1.x} {1.y}'.format(w_inner, w8))
print('      L {0.x} {0.y}'.format(w9))
print('      A {0} {0} 0 0 1 {1.x} {1.y}'.format(w_outer, w10))
print('      L {0.x} {0.y}'.format(w11))
print('      L {0.x} {0.y}'.format(w12))
print('      Z"')
print('      stroke="{0}" stroke-width="0" fill="{0}"/>'.format(w_color))

### postamble

print('  </g>')
print('</svg>')
