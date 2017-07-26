# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 20:03:51 2017

@author: Chaelya
"""

from PyQt5.QtCore import Qt, QFile, pyqtSignal
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

import datetime
import os

import Utility as util
from UserModel import UserFilter


class PrivateChatWindow(QtWidgets.QWidget):

    send = pyqtSignal(str, str)

    openInfoWindow = pyqtSignal(str)

    def __init__(self, main, ID, name = ''):
        super(PrivateChatWindow, self).__init__()

        self.channelName = name
        self.channelID = ID

        self.ownCharacters = []

        self.main = main


        self.textStream = QtWidgets.QTextBrowser()
        self.textStream.document().setMetaInformation( QtGui.QTextDocument.DocumentUrl, "file:" + os.getcwd() + "/")
        self.textStream.setOpenExternalLinks(True)
        #self.textStream.setReadOnly(True)

        self.textEntry = QtWidgets.QPlainTextEdit()
        self.textEntry.installEventFilter(self)

        self.notification = QtWidgets.QCheckBox('Notifications')
        self.character = QtWidgets.QComboBox()
        proxyModel = UserFilter(onlyOwn = True)
        proxyModel.setSourceModel(self.main.commandHandler.userList)
        self.character.setModel(proxyModel)



        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.textStream,0,0,1,3)
        layout.setColumnStretch(1,1)
        layout.setRowStretch(0,1)

        layout.addWidget(self.character,1,0)
        layout.addWidget(self.notification,1,2)
        layout.addWidget(self.textEntry,2,0,1,3)

        self.setLayout(layout)


        #self.addPost('Chaelya','Test \n [eicon]creme fraiche[/eicon]Blab, [i]Lorem Ipsum[/i] [u]Lorem Ipsum[/u]yxcsskdhgfsdkfgsd\n  kjgfskdhfskjg<br>dfsdjh\n gfksgh<br> dfkjshgdfksdhg<br>fksdhgkhsdgfkhgsd<br> kfhgsdfdsdffffffff')
        #self.addPost('Kylaan','More [user]Xillen[/user] post Test\n Test [s]Lorem Ipsum[/s][big]Lorem Ipsum[/big] [small]Lorem Ipsum[/small]\n')


    def addPost(self, text, me = False):
        user = self.channelID
        util.imageLoader.getIcon(user)
        now = datetime.datetime.now()
        html = util.parseBB(text)
        adAd=""
        if me:
            user = self.character.currentText()
        html = """<table style='width:100%'><tr>
                <td rowspan=2 style='vertical-align: top; width:60px'><img src='icons/{0}.png' width='50' align='top' hspace='' vspace=''></td>
                <td><strong>{5}{1}</strong></td>
                <td style='width:100%' align=right>{2}:{3}</td></tr>
                <tr><td colspan=2 rowspan=2>{4}</td></tr></table><br>""".format(user.lower(), user,now.hour, now.minute, html, adAd )
        self.displayHtml(html, now)

    def displayHtml(self, html, now):
        '''Write to Widget to display text'''

        self.textStream.textCursor().insertHtml(html)
        self.textStream.setVisible(True);

        #Log to disk
        outfile = QFile()
        directory = "logs Characters/{}".format(self.channelID)
        if not os.path.exists(directory):
            os.makedirs(directory)
        outfile.setFileName("logs Characters/{}/{}-{}-{}.html".format(self.channelID, now.year, str(now.month).zfill(2), str(now.day).zfill(2)) )
        outfile.open(QtCore.QIODevice.Append)
        print("1")
        stream = QtCore.QTextStream(outfile)
        print("2")
        stream<<html.replace('icons','../../icons')
        print("3")
        outfile.close()
        print("4")

    def sendPost(self):
        text = self.textEntry.toPlainText()
        self.main.commandHandler.sendPrivateMessage("Synea", self.channelID, text) #self.character.currentText()
        self.addPost(text, me=True)
        self.textEntry.setPlainText('')

    def closeWindow(self):
        print("Closed Window: {}".format(self.channelName))

    def eventFilter(self, widget, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            widget is self.textEntry):
            key = event.key()
            if key == Qt.Key_Return:
                self.sendPost()
                return True
        return QtWidgets.QWidget.eventFilter(self, widget, event)
