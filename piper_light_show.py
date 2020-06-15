################################################################################
# The MIT License (MIT)
#
# Copyright (c) 2020 Keith Evans
# Based on PewPew
# Copyright (c) 2019 Radomir Dopieralski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
################################################################################
from micropython import const
from adafruit_debouncer import Debouncer
import board
import busio
import time
from digitalio import DigitalInOut, Direction, Pull
import _spi_595

BLACK   = 0x00
RED     = 0x30
GREEN   = 0x0C
BLUE    = 0x03
CYAN    = GREEN + BLUE
MAGENTA = RED + BLUE
YELLOW  = RED + GREEN
WHITE   = RED + GREEN + BLUE

_FONT = (
        b'\xff\xff\xff\xff\xff\xff\xf3\xf3\xf7\xfb\xf3\xff\xcc\xdd\xee\xff\xff'
        b'\xff\xdd\x80\xdd\x80\xdd\xff\xf7\x81\xe4\xc6\xd0\xf7\xcc\xdb\xf3\xf9'
        b'\xcc\xff\xf6\xcdc\xdcf\xff\xf3\xf7\xfe\xff\xff\xff\xf6\xfd\xfc\xfd'
        b'\xf6\xff\xe7\xdf\xcf\xdf\xe7\xff\xff\xd9\xe2\xd9\xff\xff\xff\xf3\xc0'
        b'\xf3\xff\xff\xff\xff\xff\xf3\xf7\xfe\xff\xff\x80\xff\xff\xff\xff\xff'
        b'\xff\xff\xf3\xff\xcf\xdb\xf3\xf9\xfc\xff\xd2\xcd\xc8\xdc\xe1\xff\xf7'
        b'\xf1\xf3\xf3\xe2\xff\xe1\xce\xe3\xfd\xc0\xff\xe1\xce\xe3\xce\xe1\xff'
        b'\xf3\xf9\xdc\xc0\xcf\xff\xc0\xfc\xe4\xcf\xe1\xff\xd2\xfc\xe1\xcc\xe2'
        b'\xff\xc0\xdb\xf3\xf9\xfc\xff\xe2\xcc\xe2\xcc\xe2\xff\xe2\xcc\xd2\xcf'
        b'\xe1\xff\xff\xf3\xff\xf3\xff\xff\xff\xf3\xff\xf3\xf7\xfe\xcf\xf3\xfc'
        b'\xf3\xcf\xff\xff\xc0\xff\xc0\xff\xff\xfc\xf3\xcf\xf3\xfc\xff\xe1\xcf'
        b'\xe3\xfb\xf3\xff\xe2\xcd\xc4\xd4\xbd\xd2\xe2\xdd\xcc\xc4\xcc\xff\xe4'
        b'\xcc\xe4\xcc\xe4\xff\xe2\xcd\xfc\xcd\xe2\xff\xe4\xdc\xcc\xdc\xe4\xff'
        b'\xd0\xfc\xf4\xfc\xd0\xff\xd0\xfc\xfc\xf4\xfc\xff\xd2\xfd\xfc\x8d\xd2'
        b'\xff\xcc\xcc\xc4\xcc\xcc\xff\xd1\xf3\xf3\xf3\xd1\xff\xcb\xcf\xcf\xdc'
        b'\xe2\xff\xdc\xcc\xd8\xf4\xc8\xff\xfc\xfc\xfc\xec\xc0\xff\xdd\xc4\xc0'
        b'\xc8\xcc\xff\xcd\xd4\xd1\xc5\xdc\xff\xe2\xdd\xcc\xdd\xe2\xff\xe4\xcc'
        b'\xcc\xe4\xfc\xff\xe2\xcc\xcc\xc8\xd2\xcf\xe4\xcc\xcc\xe0\xcc\xff\xd2'
        b'\xec\xe2\xce\xe1\xff\xc0\xe2\xf3\xf3\xf3\xff\xcc\xcc\xcc\xdd\xe2\xff'
        b'\xcc\xcc\xdd\xe6\xf3\xff\xcc\xc8\xc4\xc0\xd9\xff\xcc\xd9\xe2\xd9\xcc'
        b'\xff\xcc\xdd\xe6\xf3\xf3\xff\xc0\xde\xf7\xed\xc0\xff\xd0\xfc\xfc\xfc'
        b'\xd0\xff\xfc\xf9\xf3\xdb\xcf\xff\xc1\xcf\xcf\xcf\xc1\xff\xf3\xd9\xee'
        b'\xff\xff\xff\xff\xff\xff\xff\x80\xff\xfc\xf7\xef\xff\xff\xff\xff\xd2'
        b'\xcd\xcc\x86\xff\xfc\xe4\xdc\xcc\xe4\xff\xff\xd2\xfd\xbc\xc6\xff\xcf'
        b'\xc6\xcd\xcc\x86\xff\xff\xd6\xcd\xb1\xd2\xff\xcb\xb7\xc1\xf3\xf3\xf6'
        b'\xff\xe2\xcc\xd2\xdf\xe1\xfc\xe4\xdc\xcc\xcc\xff\xf3\xfb\xf1\xb3\xdb'
        b'\xff\xcf\xef\xc7\xcf\xdd\xe2\xfd\xec\xd8\xf4\xcc\xff\xf6\xf3\xf3\xf3'
        b'\xdb\xff\xff\xd9\xc4\xc8\xcc\xff\xff\xe4\xdd\xcc\xcc\xff\xff\xe2\xcc'
        b'\xcc\xe2\xff\xff\xe4\xdc\xcc\xe4\xfc\xff\xc6\xcd\xcc\xc6\xcf\xff\xc9'
        b'\xf4\xfc\xfc\xff\xff\xd2\xf8\xcb\xe1\xff\xf3\xd1\xf3\xb3\xdb\xff\xff'
        b'\xcc\xcc\xcd\x82\xff\xff\xcc\xdd\xe6\xf3\xff\xff\xcc\xc8\xd1\xd9\xff'
        b'\xff\xcc\xe6\xe6\xcc\xff\xff\xdc\xcd\xd2\xcf\xe1\xff\xc0\xdb\xf9\xc0'
        b'\xff\xd3\xf3\xf9\xf3\xd3\xff\xf3\xf3\xf7\xf3\xf3\xff\xf1\xf3\xdb\xf3'
        b'\xf1\xff\xbfr\x8d\xfe\xff\xfff\x99f\x99f\x99')

K_RIGHT = const(0x01)
K_DOWN  = const(0x02)
K_LEFT  = const(0x04)
K_UP    = const(0x08)
K_O     = const(0x40)
K_X     = const(0x80)

_screen = None

# Map a 24-bit color tuple (RR, GG, BB) to a 6-bit color
#
def rgb_to_byte(color):
  r = ((color[0] >> 6) & 3) << 4
  g = ((color[1] >> 6) & 3) << 2
  b = ((color[2] >> 6) & 3)
  return (r | g | b)

# Placeholder for global brightness setting
#
def brightness(level):
    pass

def show(pix):
    _screen.blit(pix)

def tick(delay):
    global _tick

    _tick += delay
    time.sleep(max(0, _tick - time.monotonic()))

# Directional PAD
#
def keys():
    global _up, _down, _left, _right
    value = 0
    if not _up.value:
        value = value | K_UP
    if not _down.value:
        value = value | K_DOWN
    if not _left.value:
        value = value | K_LEFT
    if not _right.value:
        value = value | K_RIGHT
    return value

class GameOver(Exception):
    pass

class Pix:
    def __init__(self, width=8, height=8, buffer=None):
        if buffer is None:
            buffer = bytearray(width * height)
        self.buffer = buffer
        self.width = width
        self.height = height

    @classmethod
    def from_text(cls, string, color=None, bgcolor=0, colors=None):
        pix = cls(4 * len(string), 6)
        font = memoryview(_FONT)
        if colors is None:
            if color is None:
                colors = (3, 2, 1, bgcolor)
            else:
                colors = (color, color, bgcolor, bgcolor)
        x = 0
        for c in string:
            index = ord(c) - 0x20
            if not 0 <= index <= 95:
                continue
            row = 0
            for byte in font[index * 6:index * 6 + 6]:
                for col in range(4):
                    pix.pixel(x + col, row, colors[byte & 0x03])
                    byte >>= 2
                row += 1
            x += 4
        return pix

    @classmethod
    def from_iter(cls, lines):
        pix = cls(len(lines[0]), len(lines))
        y = 0
        for line in lines:
            x = 0
            for pixel in line:
                pix.pixel(x, y, pixel)
                x += 1
            y += 1
        return pix

    def pixel(self, x, y, color=None):
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return 0
        if color is None:
            return self.buffer[x + y * self.width]
        self.buffer[x + y * self.width] = color

    def box(self, color, x=0, y=0, width=None, height=None):
        x = min(max(x, 0), self.width - 1)
        y = min(max(y, 0), self.height - 1)
        width = max(0, min(width or self.width, self.width - x))
        height = max(0, min(height or self.height, self.height - y))
        for y in range(y, y + height):
            xx = y * self.width + x
            for i in range(width):
                self.buffer[xx] = color
                xx += 1

    def blit(self, source, dx=0, dy=0, x=0, y=0,
             width=None, height=None, key=None):
        if dx < 0:
            x -= dx
            dx = 0
        if x < 0:
            dx -= x
            x = 0
        if dy < 0:
            y -= dy
            dy = 0
        if y < 0:
            dy -= y
            y = 0
        width = min(min(width or source.width, source.width - x),
                    self.width - dx)
        height = min(min(height or source.height, source.height - y),
                     self.height - dy)
        source_buffer = memoryview(source.buffer)
        self_buffer = self.buffer
        if key is None:
            for row in range(height):
                xx = y * source.width + x
                dxx = dy * self.width + dx
                self_buffer[dxx:dxx + width] = source_buffer[xx:xx + width]
                y += 1
                dy += 1
        else:
            for row in range(height):
                xx = y * source.width + x
                dxx = dy * self.width + dx
                for col in range(width):
                    color = source_buffer[xx]
                    if color != key:
                        self_buffer[dxx] = color
                    dxx += 1
                    xx += 1
                y += 1
                dy += 1

    def __str__(self):
        return "\n".join(
            "".join(
                ('.', '+', '*', '@')[self.pixel(x, y)]
                for x in range(self.width)
            )
            for y in range(self.height)
        )


def init():
    global _screen, _tick, _spi, _chip_select
    global _up, _down, _left, _right

    if _screen is not None:
        return

    _screen = Pix(8, 8)
    _tick = time.monotonic()

    _chip_select = DigitalInOut(board.MISO)
    _chip_select.direction = Direction.OUTPUT
    _chip_select.value = False

    _spi = busio.SPI(board.SCK, MOSI=board.MOSI)

    while not _spi.try_lock():
        pass

    # It's taking 1.5 ms to draw the screen with a SPI clock
    # of 8 MHz. The goal is to leave 10% idle time for CircuitPython
    # to do other things. We are interrupting at a rate of 500 Hz.
    # If 8 MHz is too fast, then we will need to slow down the
    # interrupt rate and thus the screen refresh rate.
    _spi.configure(baudrate=8000000, phase=0, polarity=0)
    _spi_595.SPI_595(_spi, _chip_select, _screen.buffer)

    # TODO - handle DPAD for easier porting of PewPew projects
    # probably want to move this out later
    #
    # Directional pad pins need pull-ups enabled
    #
    _right = DigitalInOut(board.D4)
    _right.direction = Direction.INPUT
    _right.pull = Pull.UP

    _left = DigitalInOut(board.D3)
    _left.direction = Direction.INPUT
    _left.pull = Pull.UP

    _up = DigitalInOut(board.D1)
    _up.direction = Direction.INPUT
    _up.pull = Pull.UP

    _down = DigitalInOut(board.D0)
    _down.direction = Direction.INPUT
    _down.pull = Pull.UP

