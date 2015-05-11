# gw2-wurm-blocking-helper

A small overlay for Guild Wars 2 to help with the Triple Trouble event.  
Makes use of the mumblelink api to interface with the game.

## Usage:

Run Guild Wars 2 in Windowed or Windowed Fullscreen mode, this will not work in Fullscreen mode!  
Left click drag to move the window, right click to close it.  
Scroll your mouse wheel to zoom.  
Hold the Alt key to enable the window border and resize the window.  
  
The block spots will show up when you move in range of each wurm.  
The inner circle shows the actual blockspot.  
The outer circle is one full dodging distance away from the blockspot.  

###Dependencies:
* python 2.7
* pyqt 4.8.6
* py2exe to build the standalone app

Original script this is based on:
https://github.com/zeeZ/gw2-location/blob/master/client/location_sender.py
