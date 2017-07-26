
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 20:03:51 2017

@author: Chaelya
"""

import datetime
import os

from PyQt5.QtCore import Qt, QFile, pyqtSignal, QTimer
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

import Utility as util
from UserModel import UserFilter, CharacterDelegate


class ChatWindow(QtWidgets.QWidget):

    send = pyqtSignal(str, str)

    openInfoWindow = pyqtSignal(str)

    def __init__(self, main, ID, name = ''):
        super(ChatWindow, self).__init__()

        self.channelName = name
        self.channelID = ID

        self.main = main

        self.syncStream = {}

        #outfile = QFile()
        #outfile.setFileName("logs/{}.txt".format(ID))
        #outfile.open(QIODevice.Append)
        self.description = QtWidgets.QTextBrowser()
        self.description.setOpenExternalLinks(True)
        self.textStream = QtWidgets.QTextBrowser()
        self.textStream.document().setMetaInformation(QtGui.QTextDocument.DocumentUrl, "file:" + os.getcwd() + "/")
        self.textStream.setOpenExternalLinks(True)
        #self.textStream.setReadOnly(True)

        self.userList = QtWidgets.QListView()
        proxyModel = UserFilter(self.channelID)
        proxyModel.setSourceModel(self.main.commandHandler.userList)
        self.userList.setModel(proxyModel)
        self.userList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.userList.setItemDelegate(CharacterDelegate())
        self.userList.show()
        self.userList.doubleClicked.connect(self.showInfo)
        self.userList.customContextMenuRequested.connect(self.showContextMenu)

        self.textEntry = QtWidgets.QPlainTextEdit()
        self.textEntry.installEventFilter(self)
        #self.textEntry.returnPressed.connect(self.sendPost)
        self.notification = QtWidgets.QCheckBox('Notifications')

        self.character = QtWidgets.QComboBox()
        proxyModel = UserFilter(self.channelID, onlyOwn = True)
        proxyModel.setSourceModel(self.main.commandHandler.userList)
        self.character.setModel(proxyModel)

        layout = QtWidgets.QGridLayout()
        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(Qt.Vertical)
        splitter.addWidget(self.description)
        splitter.addWidget(self.textStream)
        splitter.setSizes([1, 3])
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 0, 0, 1, 2)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(0, 1)



        layout.addWidget(self.userList, 0, 2)
        layout.addWidget(self.character, 1, 0)
        layout.addWidget(self.notification, 1, 2)
        layout.addWidget(self.textEntry, 2, 0, 1, 3)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimeout)
        self.timer.start(20000)

    def onTimeout(self):
        now = datetime.datetime.now()
        for k in list(self.syncStream.keys()):
            if (now - self.syncStream[k][0]).total_seconds() > 60:
                del self.syncStream[k]

    def showContextMenu(self, pos):
        position = self.userList.mapToGlobal(pos)

        target = self.userList.model().getObject(self.userList.indexAt(pos))


        submenu = QtWidgets.QMenu()
        actionProfile = submenu.addAction("Show Profile")
        actionMessage = submenu.addAction("Private Message")
        actionBookmark = submenu.addAction("Bookmark")
        actionFriend = submenu.addAction("Send Friend Request")
        actionLeave = submenu.addAction("Leave Channel")
        ignoreActions = submenu.addMenu("Ignore:")

        actionProfile.triggered.connect(lambda: self.showInfo(position))
        actionMessage.triggered.connect(lambda: self.main.getPrivateWindow(target.name))
        actionLeave.triggered.connect(lambda: self.main.commandHandler.leaveChannel(self.character.getText(), self.channelID))

        if not target.isIgnored():
            actionIgnore = ignoreActions.addAction("Ignore Character")
            actionIgnore.triggered.connect(lambda: self.main.commandHandler.setIgnore(self.character.getText(), target.name))
        else:
            actionUnIgnore = ignoreActions.addAction("Unignore Character")
            actionUnIgnore.triggered.connect(lambda: self.main.commandHandler.setUnignore(self.character.getText(), target.name))

        for i in range(self.character.count()):
            model = self.userList.model()
            if model.getObject(model.index(i,0)).isChanOp(self.channelID):
                modActions = submenu.addMenu("Moderation:")
                modActions.addAction("Give Chan Op")
                modActions.addAction("Remove Chan Op")
                modActions.addAction("Kick")
                modActions.addAction("Ban")
                break
        submenu.exec(position);

    def addPost(self, user, text, ad=False):
        util.imageLoader.loadImage(user)
        now = datetime.datetime.now()
        html = util.parseBB(text)
        if text in self.syncStream:
            if user not in self.syncStream[text][1]:
                self.syncStream[text][1].append(user)
                return
            #elif now-self.syncStream[text][0]

        self.syncStream[text] = [now, [user]]

        adAd=""
        if ad:
            adAd="Advertisement: "
        html = """<table style='width:100%'><tr>
                <td rowspan=2 style='vertical-align: top; width:60px'><img src='icons/{0}.png' width='50' align='top' hspace='' vspace=''></td>
                <td><strong>{5}{1}</strong></td>
                <td style='width:100%' align=right>{2}:{3}</td></tr>
                <tr><td colspan=2 rowspan=2>{4}</td></tr></table><br>""".format(user.lower(), user,now.hour, str(now.minute).zfill(2), html, adAd )
        self.displayHtml(html, now)

    def displayPunishment(self, operator, user, time):
        if time < 0:
            action = "banned"
        elif time == 0:
            action = "kicked"
        else:
            action = "banned for {} minutes".format(time)
        now = datetime.datetime.now()

        html = """<table style='width:100%'><tr>
                <td><strong>{2} has been {0} by {1}</strong></td>
                <td style='width:100%' align=right>{3}:{4}</td></tr>""".format(action, operator, user, now.hour, now.minute,)
        self.displayHtml(html, now)

    #Not the fun kind
    def displayHtml(self, html, now):
        #Write to Widget to display text
        self.textStream.textCursor().insertHtml(html)
        self.textStream.setVisible(True);

        #Log to disk
        outfile = QFile()
        directory = "logs Channels/{}".format(self.channelName)
        if not os.path.exists(directory):
            os.makedirs(directory)
        outfile.setFileName("logs Channels/{}/{}-{}-{}.html".format(self.channelID,now.year,str(now.month).zfill(2),str(now.day).zfill(2)) )
        outfile.open(QtCore.QIODevice.Append)
        stream = QtCore.QTextStream(outfile)
        stream<<html.replace('icons','../../icons')
        outfile.close()

    def setDescription(self, message):
        html = util.parseBB(message)
        self.description.setHtml(html)

    def showInfo(self, index):
        user = self.userList.model().getName(index)
        self.openInfoWindow.emit(user)

    def sendPost(self):
        text = self.textEntry.toPlainText()
        self.main.commandHandler.sendToChannel(self.character.currentText(), self.channelID, text)
        self.addPost(self.character.currentText(), text)
        self.textEntry.setPlainText('')

    def closeWindow(self):
        self.character.setCurrentIndex(0)
        lst = [self.character.itemText(i) for i in range(self.character.count())]
        print("Closed Window: {}".format(self.channelName))
        for name in lst:
            self.main.commandHandler.leaveChannel(name, self.channelID)

    def eventFilter(self, widget, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            widget is self.textEntry):
            key = event.key()
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if key == Qt.Key_Return and not modifiers == Qt.AltModifier:
                self.sendPost()
                return True
        return QtWidgets.QWidget.eventFilter(self, widget, event)


class InfoWindow(QtWidgets.QDialog):
    def __init__(self, user):
        super(InfoWindow, self).__init__()
        layout = QtWidgets.QGridLayout()
        img = util.imageLoader.getIcon(user)
        icon = QtWidgets.QLabel()
        icon.setPixmap(img.pixmap(100,100))
        label = QtWidgets.QLabel()
        label.setText("<strong><a href='https://www.f-list.net/c/{0}'>{0}</a> </strong>".format(user))
        label.setTextFormat(Qt.RichText)
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label.setOpenExternalLinks(True)

        keys = ['Species', 'Age', 'Apparent Age', 'Gender', 'Dom/Sub Role',
                'Orientation', 'Occupation', 'Language preference',
                'Desired post length', 'Furry preference']
        self.labels = {}
        layout.addWidget(icon)
        layout.addWidget(label)
        for key in keys:
            self.labels[key] = QtWidgets.QLabel('{}:'.format(key))
            layout.addWidget(self.labels[key])
        self.setLayout(layout)

    def setValue(self, key, value):
        if key in self.labels:
            self.labels[key].setText('{}: {}'.format(key, value))


