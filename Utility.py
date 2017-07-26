# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 21:03:04 2017

@author: Chaelya
"""

from PyQt5.QtGui import QPixmap, QIcon
#from PyQt5.QtCore import *
import requests

import bbcode



parser = bbcode.Parser()
parser.add_simple_formatter('hr', '<hr/>', standalone=True)
parser.add_simple_formatter('sub', ' <sub>%(value)s</sub>')
parser.add_simple_formatter('sup', ' <sup>%(value)s</sup>')
parser.add_simple_formatter('big', ' <span style="font-size:15px">%(value)s</span>')
parser.add_simple_formatter('small', ' <span style="font-size:9px">%(value)s</span>')
parser.add_simple_formatter('user', ' <strong><a href="https://www.f-list.net/c/%(value)s">%(value)s</a></strong>')


def eicon_formatter (tag_name, value, options, parent, context):
    imageLoader.loadEIcon(value)
    return "<img src='icons/{}.png'>".format(value)

def icon_formatter (tag_name, value, options, parent, context):
    imageLoader.loadImage(value)
    return "<a href='https://www.f-list.net/c/{0}'><img src='icons/{0}.png'></a>".format(value)

parser.add_formatter('eicon', eicon_formatter)
parser.add_formatter('icon', icon_formatter)

def render_color(tag_name, value, options, parent, context):
    return '<span style="color:{0};">{1}</span>'.format(tag_name, value)

for color in ('red', 'blue', 'green', 'yellow', 'black', 'white', 'pink', 'grey', 'orange', 'purple', 'brown', 'cyan'):
    parser.add_formatter(color, render_color)

def parseBB(text):
    return parser.format(text)


class ImageLoader():
    def __init__(self):
        self.images = {}

    def loadEIcon(self, name):
        if name in self.images:
            return
        img = requests.get('https://static.f-list.net/images/eicon/{0}.png'.format(name.lower()))
        pixmap=QPixmap()
        pixmap.loadFromData(img.content)
        f = open('eicons/{}.png'.format(name.lower()),'wb')
        f.write(img.content)
        f.close()
        self.images[name] = pixmap


    def loadImage(self, name):
        if name in self.images:
            return
        try:
            img = requests.get('https://static.f-list.net/images/avatar/{0}.png'.format(name.lower()))
        except requests.exceptions.ConnectionError:
            return
        pixmap=QPixmap()
        pixmap.loadFromData(img.content)
        f = open('icons/{}.png'.format(name.lower()),'wb')
        f.write(img.content)
        f.close()
        self.images[name] = pixmap


    def getIcon(self, name):
        img = 'icons/' + name.lower() +'.png'
        return QIcon(img)


    def getEIcon(self, name):
        img = 'eicons/' + name.lower() +'.png'
        return QIcon(img)




imageLoader = ImageLoader()