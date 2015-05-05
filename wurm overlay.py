#!/usr/bin/env python2

# auto detect map and closest wurm
# tequatl double damage and engie spot
# tequatl rotation helper
# change random magic numbers to constants
# allow resizing window

import ctypes
import mmap
import sys
import math
from PyQt4 import QtCore, QtGui

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


amber = [670.2831, -0.23419858515262604, -606.0043]
crimson = [198.8736, 16.052361, -438.4727]
cobalt = [-277.9741, -0.23419858515262604, -876.9177]

wurm = amber

current_map = 0
current_map_data = None
lastCoords = [0,0,0]
lastCameraPos = [0,0,0]
previous_tick = 0
result = None

memfile = mmap.mmap(0, ctypes.sizeof(Link), "MumbleLink")

class Overlay(QtGui.QWidget):
    def __init__(self):
        super(Overlay,self).__init__()

        pen = QtGui.QPen()
        self.pen = pen

        self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowTitleHint)
        self.setFixedSize(120, 120)
        self.setWindowOpacity(1)

        self.restoreGeometry(QtCore.QSettings("WurmBlockingHelper").value("overlay/geometry").toByteArray());

        msgBox = QtGui.QMessageBox(self)

        bcrimson = msgBox.addButton('Crimson', QtGui.QMessageBox.AcceptRole)
        bamber = msgBox.addButton('Amber', QtGui.QMessageBox.AcceptRole)
        bcobalt = msgBox.addButton('Cobalt', QtGui.QMessageBox.AcceptRole)

        QtCore.QObject.connect(bcrimson, QtCore.SIGNAL('clicked()'), self.btnClicked)
        QtCore.QObject.connect(bamber, QtCore.SIGNAL('clicked()'), self.btnClicked)
        QtCore.QObject.connect(bcobalt, QtCore.SIGNAL('clicked()'), self.btnClicked)

        msgBox.exec_()

        self.show()

        self.startTimer(200)

    def btnClicked(self):
        global wurm
        button = self.sender().text()
        print button
        if button == "Crimson":
            wurm = crimson
        if button == "Amber":
            wurm = amber
        if button == "Cobalt":
            wurm = cobalt

    def timerEvent(self, event):
        self.raise_() #keep always in the foreground hopefully maybe
        global current_map
        global current_map_data
        global lastCoords
        global lastCameraPos
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
            cameraPos = result.fCameraFront[0:3]
            if lastCoords != coords or cameraPos != lastCameraPos:
                lastCoords = coords
                lastCameraPos = cameraPos
                self.repaint()

    def closeEvent(self, event):
        QtCore.QSettings("WurmBlockingHelper").setValue("overlay/geometry", self.saveGeometry());

    def paintEvent(self, event):
        pen = self.pen
        dx = lastCoords[0]-wurm[0]
        dy = lastCoords[2]-wurm[2]
        l = math.sqrt(dx*dx + dy*dy)
        if l == 0: l = 1
        nx = dx / l
        ny = dy / l

        painter = QtGui.QPainter(self)

        lineLen = 30 * l

        # change color when in range
        if lineLen < 8:
            pen.setColor(QtGui.QColor(0, 255, 0))
        else:
            pen.setColor(QtGui.QColor(255, 0, 0))

        pen.setWidth(1)
        painter.setPen(self.pen)
        painter.drawEllipse(50, 50, 20, 20)

        # camera rotation stuffs
        cx = lastCameraPos[0]
        cy = lastCameraPos[2]

        l2 = math.sqrt(cx*cx + cy*cy)
        if l2 == 0: l2 = 1

        cx = cx / l2
        cy = cy / l2

        px1 = 60
        py1 = 60

        tx = -nx*lineLen
        ty = ny*lineLen

        px2 = tx * cx - ty * cy
        py2 = tx * cy + ty * cx

        #rotate by another 90*
        angle = math.pi / 2
        cos = math.cos(angle)
        sin = math.sin(angle)
        rx = px2 * cos - py2 * sin
        ry = px2 * sin + py2 * cos 

        px2 = rx + 60
        py2 = ry + 60

        pen.setWidth(5)
        painter.setPen(self.pen)
        painter.drawLine(px1, py1, px2, py2)

def main():
    global wurm

    a = QtGui.QApplication([])

    overlay = Overlay()
    overlay.setWindowTitle("")

    settings = QtCore.QSettings("WurmBlockingHelper");
    overlay.restoreGeometry(settings.value("overlay/geometry").toByteArray());

    a.exec_()

    settings.sync()

if __name__ == "__main__":
    main()

