#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2015 github.com/Stonos
# Copyright (C) 2015 Matteo Goggi <github.com/teomat>
# Copyright (C) 2015 Marcin Błaszyk <github.com/haldiraros>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ctypes
import mmap
import sys
import math
from PyQt4 import QtCore, QtGui
import json

class Link(ctypes.Structure):
    _fields_ = [
        ("uiVersion",       ctypes.c_uint32),
        ("uiTick",          ctypes.c_ulong),
        ("fAvatarPosition", ctypes.c_float * 3),
        ("fAvatarFront",    ctypes.c_float * 3),
        ("fAvatarTop",      ctypes.c_float * 3),
        ("name",            ctypes.c_wchar * 256),
        ("fCameraPosition", ctypes.c_float * 3),
        ("fCameraFront",    ctypes.c_float * 3),
        ("fCameraTop",      ctypes.c_float * 3),
        ("identity",        ctypes.c_wchar * 256),
        ("context_len",     ctypes.c_uint32),
        ("context",         ctypes.c_uint32 * (256/4)), # is actually 256 bytes of whatever
        ("description",     ctypes.c_wchar * 2048)

    ]

def Unpack(ctype, buf):
    cstring = ctypes.create_string_buffer(buf)
    ctype_instance = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
    return ctype_instance

coordinates = json.load(open("coordinates.json"))

current_map = 0
current_map_data = None
lastCoords = [0,0,0]
lastCameraRot = [0,0,0]
previous_tick = 0
result = None

memfile = mmap.mmap(0, ctypes.sizeof(Link), "MumbleLink")

class Overlay(QtGui.QWidget):
    def __init__(self):
        super(Overlay,self).__init__()

        pen = QtGui.QPen()
        self.pen = pen

        #changed flags a bit and background color to introduce transparency-- Elonora
        self.setWindowOpacity(0.66)

        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)
        self.setFixedSize(250, 250)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint )
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.restoreGeometry(QtCore.QSettings("WurmBlockingHelper").value("overlay/geometry").toByteArray());

        self.show()

        self.startTimer(1000/60)

#added events so that you can move window with left click and
# close it with right click-- Elonora
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        if event.button() == QtCore.Qt.RightButton:
            self.close()
        
    def mouseMoveEvent(self, event):
        x=event.globalX()
        y=event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)

    def timerEvent(self, event):
        self.raise_() #keep always in the foreground hopefully maybe
        global current_map
        global current_map_data
        global lastCoords
        global lastCameraRot
        global wurm
        global result
        memfile.seek(0)
        data = memfile.read(ctypes.sizeof(Link))
        result = Unpack(Link, data)
        if result.uiVersion == 0 and result.uiTick == 0:
            print("MumbleLink contains no data, setting up and waiting")
            try:
                init = Link(2,name="Guild Wars 2")
                memfile.seek(0)
                memfile.write(init)
            except Exception, e:
                logging.exception("Error writing init data",e)

        if result.uiTick != previous_tick:
            if result.context[7] != current_map:
                # Map change
                print("Player changed maps (%d->%d)" % (current_map, result.context[7]))
                current_map = result.context[7]                

            coords = result.fAvatarPosition[0:3]
            cameraRot = result.fCameraFront[0:3]
            if lastCoords != coords or cameraRot != lastCameraRot:
                lastCoords = coords
                lastCameraRot = cameraRot
                self.repaint()

    def closeEvent(self, event):
        QtCore.QSettings("WurmBlockingHelper").setValue("overlay/geometry", self.saveGeometry());

    def paintEvent(self, event):
        width = self.width()
        height = self.height()

        painter = QtGui.QPainter(self)
        pen = self.pen

        scale = 15

        def getCameraRotation():
            # camera rotation vector
            # we only care about the world from a top down view so we ignore the 3d y component
            cx = lastCameraRot[0]
            cy = lastCameraRot[2]

            # normalize the vector
            # needed cause we discarded the y component
            l = math.sqrt(cx*cx + cy*cy)
            if l == 0: l = 1
            cx = cx / l
            cy = cy / l

            return (cx, cy)

        rx,ry = getCameraRotation()
        
        # draw the player marker
        # rx,ry = camera rotation
        def drawPlayerPos(px,py, rx,ry, size):
            pen.setWidth(1)
            pen.setColor(QtGui.QColor(255, 255, 255))
            painter.setPen(self.pen)

            x1 = px + rx * -size
            x2 = px + rx * size
            y1 = py + ry * -size
            y2 = py + ry * size
            painter.drawLine(x1, y1, x2, y2)

            #rotate 90* for second line
            angle = math.pi / 2
            cos = math.cos(angle)
            sin = math.sin(angle)
            rx2 = rx * cos - ry * sin
            ry2 = rx * sin + ry * cos

            x1 = px + rx2 * -size
            x2 = px + rx2 * size
            y1 = py + ry2 * -size
            y2 = py + ry2 * size

            painter.drawLine(x1, y1, x2, y2)

        # draw the player at the center of the screen
        drawPlayerPos(width / 2,height / 2, rx,ry, size= 10)

        # px,py = player position
        # bx,by = blockspot
        # rx,ry = camera rotation
        def drawBlockSpot(px,py, bx,by, rx, ry, spotSize, dodgeSize):
            # vector from player to blockspot
            dx = px - bx
            dy = py - by

            # distance to blockspot
            l = math.sqrt(dx*dx + dy*dy)
            if l == 0: l = 1
            nx = dx / l
            ny = dy / l

            lineLen = scale * l

            tx = nx*lineLen
            ty = -ny*lineLen

            # rotate the vector by our camera rotation
            px2 = tx * rx - ty * ry
            py2 = tx * ry + ty * rx

            # rotate by another 90*
            angle = math.pi / 2
            cos = math.cos(angle)
            sin = math.sin(angle)
            rx = px2 * cos - py2 * sin
            ry = px2 * sin + py2 * cos 

            px1 = width / 2
            py1 = height / 2

            px2 = rx + px1
            py2 = ry + py1

            # change color when in range
            if lineLen < spotSize:
                pen.setColor(QtGui.QColor(0, 255, 0))
            else:
                pen.setColor(QtGui.QColor(255, 0, 0))

            pen.setWidth(1)
            painter.setPen(pen)

            painter.drawEllipse(px2 - spotSize, py2 - spotSize, spotSize * 2, spotSize * 2)
            painter.drawEllipse(px2 - dodgeSize, py2 - dodgeSize, dodgeSize * 2, dodgeSize * 2)

        px = lastCoords[0]
        py = lastCoords[2]

        for _,wurm in coordinates.iteritems():
            bx = wurm[0]
            by = wurm[1]
            drawBlockSpot(px,py, bx,by, rx,ry, spotSize = 6, dodgeSize = 110)

def main():
    a = QtGui.QApplication([])

    overlay = Overlay()
    overlay.setWindowTitle("")

    settings = QtCore.QSettings("WurmBlockingHelper");
    overlay.restoreGeometry(settings.value("overlay/geometry").toByteArray());

    a.exec_()

    settings.sync()

if __name__ == "__main__":
    main()

