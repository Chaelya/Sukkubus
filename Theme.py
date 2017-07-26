#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 23:46:52 2017

@author: Chaelya
"""


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QStyleFactory, qApp





def setTheme(theme):
    themeCollection[theme]()


def setDarkTheme():
    darkPalette = QPalette()
    qApp.setStyle(QStyleFactory.create("Fusion"))
    darkPalette.setColor(QPalette.Window, QColor(53,53,53))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Base, QColor(25,25,25))
    darkPalette.setColor(QPalette.AlternateBase, QColor(53,53,53))
    darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Button, QColor(53,53,53))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))

    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.HighlightedText, Qt.black)

    qApp.setPalette(darkPalette)

    qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

def setBlueTheme():
    darkPalette = QPalette()
    qApp.setStyle(QStyleFactory.create("Fusion"))
    darkPalette.setColor(QPalette.Window, Qt.darkBlue)
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Base, Qt.darkCyan)
    darkPalette.setColor(QPalette.AlternateBase, Qt.darkBlue)
    darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Button, Qt.darkBlue)
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))

    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.HighlightedText, Qt.black)

    qApp.setPalette(darkPalette)

    qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

def setPinkTheme():
    darkPalette = QPalette()
    qApp.setStyle(QStyleFactory.create("Fusion"))
    darkPalette.setColor(QPalette.Window, Qt.darkMagenta)
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Base, Qt.magenta)
    darkPalette.setColor(QPalette.AlternateBase, Qt.darkMagenta)
    darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Button, Qt.darkMagenta)
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))

    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.HighlightedText, Qt.black)

    qApp.setPalette(darkPalette)

    qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

themeCollection = {}
themeCollection['dark'] = setDarkTheme
themeCollection['blue'] = setBlueTheme
themeCollection['pink'] = setPinkTheme