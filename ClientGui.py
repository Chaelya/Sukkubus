#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 23:38:01 2017

@author: Chaelya
"""

import sys
import os
import traceback
import configparser
import logging

from PyQt5.QtCore import (Qt, QSize, pyqtSignal, QTimer)
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog
#import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QIcon




from SocketConnection import ClientSocket, Ticket
from WindowChat import ChatWindow, InfoWindow
from WindowPrivateChat import PrivateChatWindow
from CommandHandler import CommandHandler
from UserModel import UserFilter, CharacterDelegate
import Utility as util
from Theme import setTheme

path = os.path.abspath(os.path.dirname(__file__))
os.chdir(path)
print(os.getcwd())

config = configparser.ConfigParser()
config.read('settings.cfg')

if not config.has_section('LoginData'):
    config.add_section('LoginData')
    config.set('LoginData', 'username', "")
    config.set('LoginData', 'password', "")
if not config.has_section('Characters'):
    config.add_section('Characters')


class ChatClient(QtWidgets.QMainWindow):


    channelsUpdated = pyqtSignal()

    def __init__(self):
        super(ChatClient, self).__init__()
        #self.statusBar().showMessage('Ready')
        #self.showConfigDialog()

        self.setWindowTitle('Chat Client')

        self.ticket = None
        #Logic

        self.publicChannels = {}
        self.privateChannels = {}
        #Store here names of private channels you create on your own as their names don't get supplied.
        self.tempName = ""

        self.info = {}

        self.client = {}
        self.publicWindows = {}
        self.privateWindows = {}
        self.channels = None

        self.commandHandler = CommandHandler(self, self.client)

        self.getTicketInfo()

        self.chatWindow = QtWidgets.QTabWidget()
        self.chatWindow.setTabsClosable(True)
        self.chatWindow.setUsesScrollButtons(True)
        self.chatWindow.setMovable(True)
        self.chatWindow.setDocumentMode(True)
        self.chatWindow.setIconSize(QSize(50, 50))
        self.chatWindow.tabCloseRequested.connect(self.closeChatWindow)
        self.chatWindow.show()
        self.chatWindow.setGeometry(100, 100, 900, 600)

        self.status = StatusWindow(self)
        self.setCentralWidget(self.status)

        #Toplevel Menu
        toolbar = self.addToolBar('Exit')

        newPMAction = QtWidgets.QAction(QIcon('resources/status.png'), 'Private Message', self)
        configureAction = QtWidgets.QAction(QIcon('resources/configure.png'), 'Configure', self)
        channelsAction = QtWidgets.QAction(QIcon('resources/channel.png'), 'Show Channels', self)
        friendsAction = QtWidgets.QAction(QIcon('resources/friends.png'), 'Show Friends', self)
        #statusAction = QtWidgets.QAction(QIcon('resources/status.png'), 'Show Status', self)

        #channelsAction = QtWidgets.QAction(QIcon('resources/status.png'), 'Show channels', self)

        exitAction = QtWidgets.QAction(QIcon('resources/exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)


        toolbar.addAction(channelsAction)
        toolbar.addAction(friendsAction)
        #toolbar.addAction(statusAction)
        toolbar.addAction(configureAction)
        toolbar.addAction(exitAction)
        toolbar.addAction(newPMAction)
        #toolbar.addAction(channelsAction)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        configureAction.triggered.connect(self.showConfigDialog)
        #statusAction.triggered.connect(self.showStatus)
        friendsAction.triggered.connect(self.showFriends)

        channelsAction.triggered.connect(self.showChannels)

        newPMAction.triggered.connect(self.openMessageWindow)






        self.show()


        #self.getPrivateWindow("Chaelya")

#ToDo: Restore channels and PM window
#        lastChannels = configparser.ConfigParser()
#        lastChannels.read('channels.cfg')
#        for item in lastChannels.sections("Channels"):
#            if lastChannels.getBool(item,"Public"):
#                self.getWindow(ID)
#            else:
#                self.getPrivateWindow(ID)



    def showChannels(self):
        self.channels = ChannelsWindow(self)
        self.channelsUpdated.connect(self.channels.update)

    def openMessageWindow(self):
        text = QInputDialog.getText(self, "New Private Message",
                                    "Character:")
        if text[1]:
            self.getPrivateWindow(text[0])

    def showConfigDialog(self):
        SettingsDialog(self.ticket.data.get('characters'), self.client)


    def showFriends(self):
        self.friendWindow = FriendsWindow(self)


    def getTicketInfo(self):
        error = " "
        if config.get('LoginData', 'username') != "": #Check if keys are defined
            self.ticket = Ticket(config.get('LoginData', 'username'),
                                 config.get('LoginData', 'password'))
            error = self.ticket.error
        if error != "":
            while True:
                LoginDialog(error)
                self.ticket = Ticket(config.get('LoginData', 'username'),
                                     config.get('LoginData', 'password'))
                error = self.ticket.error
                if error == "":
                    break
                #Show login Dialog


    def loginCharacter(self, character):

        self.client[character].openConnection(config.get('LoginData', 'username'),
                                              config.get('LoginData', 'password'))
        self.client[character].onMessage.connect(self.commandHandler.onMessage)

    def logoutCharacter(self, character):
        self.client[character].logoutCharacter()

    def receiveChannelInvitation(self, user, key, title, channel):
        msgBox = QMessageBox()
        msgBox.setText("{} invited {} to the channel {}.".format(user, key, title))
        msgBox.setStandardButtons(QMessageBox.Open | QMessageBox.Discard)
        msgBox.setDefaultButton(QMessageBox.Open)
        ret = msgBox.exec()
        if ret == QMessageBox.Open:
            self.main.client[key].joinChannel(channel)
        elif QMessageBox.Discard:
            pass

    def globalNotification(self, user, msg):
        msgBox = QMessageBox()
        msgBox.setText("{}: {}.".format(user, msg))
        msgBox.setDefaultButton(QMessageBox.Close)
        msgBox.open()

    #Client Event handlers

    def changeChannelOpList(self, ID, users, addOps):
        self.getWindow(ID).changeChannelOpList(users, addOps)

    def setChannels(self, public, data):
        if public:
            self.publicChannels = {}
            for f in data:
                self.publicChannels[f['name']] = f['characters']
        else:
            self.privateChannels = {}
            for f in data:
                self.privateChannels[f['title']] = [f['name'],f['characters']]
        self.channelsUpdated.emit()

    def getWindow(self, ID):
        if not ID in self.publicWindows:
            if ID[:2] == "ADH":
                name = self.tempName
                for key in self.privateChannels:
                    if ID == self.privateChannels[key][0]:
                        name = key
                        break
            else:
                name = ID
            print("New window: {}".format(name))
            self.publicWindows[ID] = ChatWindow(self, ID, name)

            self.chatWindow.addTab(self.publicWindows[ID], QIcon('icons/Imaerizi-100.png'), name)
            self.publicWindows[ID].openInfoWindow.connect(self.openUserInfo)
        return self.publicWindows[ID]

    def getPrivateWindow(self, ID):
        if not ID in self.privateWindows:
            print("New window: {}".format(ID))
            self.privateWindows[ID] = PrivateChatWindow(self, ID)
            util.imageLoader.getIcon(ID)
            self.chatWindow.addTab(self.privateWindows[ID], util.imageLoader.getIcon(ID), ID)
        return self.privateWindows[ID]

    def enterChannel(self, ID, users, character):
        self.getWindow(ID)
        self.commandHandler.userList.addUsersToChannel(ID, users)

    def handleEnterChannel(self, ID, user, login):
        self.getWindow(ID).loginUser(user, login)

    def handleMessage(self, character, message, ID, ad ):
        self.getWindow(ID).addPost(character, message, ad)

    def handlePrivateMessage(self, ID, message):
        self.getPrivateWindow(ID).addPost(message)

    def handleDescription(self, ID, message):
        self.getWindow(ID).setDescription(message)

    def displayPunishment(self, ID, operator, user, time):
        self.getWindow(ID).displayPunishment(operator, user, time)


    def openUserInfo(self, name):
        if name not in self.info:
            self.info[name] = InfoWindow(name)
        self.info[name].show()
        for key in self.client:
            if self.client[key].state.text() == "Connected":
                self.commandHandler.getUserInfo(key,name)
                break

    def handleUserInfo(self, name, key, value):
        self.info[name].setValue(key, value)

    def showPopup(self, message):
        msgBox = QMessageBox()
        msgBox.setText(message)
        msgBox.show()

    def closeChatWindow(self, index):
        self.chatWindow.widget(index).closeWindow()
        print('Close Window')
        self.chatWindow.removeTab(index)


class FriendsWindow(QtWidgets.QListView):

    def __init__(self, main):

        super(FriendsWindow, self).__init__()
        self.view = QtWidgets.QListView()
        label = QtWidgets.QLabel("Friends")
        vbox = QtWidgets.QVBoxLayout()

        vbox.addWidget(label)
        vbox.addWidget(self.view)
        self.setLayout(vbox)

        proxyModel = UserFilter(onlyFriends = True)
        proxyModel.setSourceModel(main.commandHandler.userList)
        self.view.setModel(proxyModel)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.setItemDelegate(CharacterDelegate())
        self.show()
        self.view.doubleClicked.connect(self.showInfo)

    def showInfo(self, index):
        user = self.view.model().getName(index)
        print(user)
        #self.openInfoWindow.emit(user)


class StatusWindow(QtWidgets.QWidget):
    def __init__(self, chat):
        super(StatusWindow, self).__init__()
        self.tabs = {}
        for key, val in self.tabs:
            val.hide()
        layout = QtWidgets.QVBoxLayout()
        for item in config.items('Characters'):
            if item[1] != "" and item[1] not in self.tabs:
                tab = StatusWindowTab(chat, item[1])
                layout.addWidget(tab)
                self.tabs[item[1]] = tab
            if item[1] in self.tabs:
                self.tabs[item[1]].show()
        self.setLayout(layout)


class StatusWindowTab(QtWidgets.QGroupBox):
    def __init__(self, chat, character):
        super(StatusWindowTab, self).__init__()
        self.chat = chat

        self.character = QtWidgets.QLabel(character)
        self.statusSelect = QtWidgets.QComboBox()
        self.statusSelect.addItem(QIcon('resources/online.png'), "Online")
        self.statusSelect.addItem(QIcon('resources/online.png'), "Looking")
        self.statusSelect.addItem(QIcon('resources/away.png'), "Busy", )
        self.statusSelect.addItem(QIcon('resources/away.png'), "Away", )
        self.statusSelect.addItem(QIcon('resources/dnd.png'), "Do not disturb")

        self.loginButton = QtWidgets.QPushButton('Offline')
        self.loginButton.setCheckable(True)
        self.loginButton.setMinimumWidth(100)

        self.statusLine =  QtWidgets.QPlainTextEdit()
        self.statusLine.installEventFilter(self)
        self.statusLine.setMaximumSize(QSize(200, 60))

        util.imageLoader.loadImage(character)
        icon = QtWidgets.QLabel()
        icon.setPixmap(QIcon('icons/' + character.lower() +'.png').pixmap(100, 100))

        layout = QtWidgets.QGridLayout()
        layout.addWidget(icon, 0, 0, 3, 1)
        layout.addWidget(self.character, 0, 1)
        layout.addWidget(self.loginButton, 0, 2)
        layout.addWidget(self.statusSelect, 1, 1)
        #layout.addWidget(self.connectionStatus, 1, 2)
        layout.addWidget(self.statusLine, 2, 1)

        self.chat.client[character] = ClientSocket(character, self.loginButton)

        self.setLayout(layout)
        self.loginButton.clicked.connect(self.onLogin)
        #self.activateWindow()

    def onLogin(self, isOn):
        if isOn:
            self.chat.loginCharacter(self.character.text())
        else:
            self.chat.logoutCharacter(self.character.text())

    def setStatus(self):
        self.chat.commandHandler.updateUserStatus(self.character.text(), self.statusSelect.currentText(), self.statusLine.toPlainText())

    def eventFilter(self, widget, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            widget is self.statusLine):
            key = event.key()
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if key == Qt.Key_Return and not modifiers == Qt.AltModifier:
                self.setStatus()
                return True
        return QtWidgets.QWidget.eventFilter(self, widget, event)


class ChannelsWindow(QtWidgets.QWidget):
    def __init__(self, main):
        super(ChannelsWindow, self).__init__()
        layout = QtWidgets.QGridLayout()
        self.main = main
        self.public = QtWidgets.QListWidget()
        self.public.doubleClicked.connect(self.onJoinPublicChannel)
        self.private = QtWidgets.QListWidget()
        self.private.doubleClicked.connect(self.onJoinPrivateChannel)
        self.name = QtWidgets.QLineEdit()
        self.create = QtWidgets.QPushButton("Create New Channel")
        self.create.clicked.connect(self.onCreateChannel)
        self.selector = QtWidgets.QComboBox()
        proxyModel = UserFilter(onlyOwn = True)
        proxyModel.setSourceModel(self.main.commandHandler.userList)
        self.selector.setModel(proxyModel)


        layout.addWidget(QtWidgets.QLabel('Public Channels'), 0, 0)
        layout.addWidget(self.public, 1, 0)
        layout.addWidget(QtWidgets.QLabel('Private Channels'), 0, 1)
        layout.addWidget(self.private, 1, 1)
        layout.addWidget(self.selector, 2, 0, 1, 2)
        layout.addWidget(self.name, 3, 0)
        layout.addWidget(self.create, 3, 1)


        self.setLayout(layout)
        self.show()
        self.activateWindow()

        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimeout)
        self.timer.start(60000)

        self.onTimeout()

    def onTimeout(self):
        for key in self.main.client:
            if self.main.client[key].state.text() == "Connected":
                self.main.commandHandler.getPrivateChannels(key)
                self.main.commandHandler.getPublicChannels(key)
                break
        for key in self.main.client:
            if key not in [self.selector.itemText(i) for i in range(self.selector.count())]:
                self.selector.addItem(str(key))

    def update(self):
        self.public.clear()
        for chan in self.main.publicChannels:
            self.public.addItem("{} : {}".format(self.main.publicChannels[chan], chan))
        self.private.clear()
        for chan in self.main.privateChannels:
            self.private.addItem("{} : {}".format(self.main.privateChannels[chan][1], chan))
        self.public.sortItems(Qt.DescendingOrder)

        self.private.sortItems()

    def onCreateChannel(self):
        key = self.selector.currentText()
        if self.main.client[key].state.text() == "Connected":
            self.main.commandHandler.createChannel(key, self.name.text())
        self.main.tempName = self.name.text()

    def onJoinPublicChannel(self, index):
        #print(self.public.item(index.row()).text().split(' : '))
        chan = self.public.item(index.row()).text().split(' : ')[1]
        key = self.selector.currentText()
        if self.main.client[key].state.text() == "Connected":
            self.main.commandHandler.joinChannel(key, chan)
            logging.info("Trying to join "+chan)

    def onJoinPrivateChannel(self, index):
        #print(self.public.item(index.row()).text().split(' : '))
        chan = self.private.item(index.row()).text().split(' : ')[1]
        key = self.selector.currentText()
        if self.main.client[key].state.text() == "Connected":
            self.main.commandHandler.joinChannel(key, self.main.privateChannels[chan][0])
            logging.info("Trying to join "+chan)

    def closeEvent(self, *args, **kwargs):
        self.timer.stop()
        #super(QtWidgets.QWidget, self).closeEvent(*args, **kwargs)


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, errormsg):
        super(LoginDialog, self).__init__()


        layout = QtWidgets.QGridLayout()

        layout.addWidget(QtWidgets.QLabel('Login Name'), 0, 0)
        self.userName = QtWidgets.QLineEdit()

        layout.addWidget(self.userName,0, 1)
        layout.addWidget(QtWidgets.QLabel('Password'), 1, 0)
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setInputMethodHints(Qt.ImhHiddenText| Qt.ImhNoPredictiveText|Qt.ImhNoAutoUppercase)

        layout.addWidget(self.password, 1, 1)

        layout.addWidget(QtWidgets.QLabel(errormsg), 2, 1)

        self.userName.setText(config.get('LoginData', 'username'))
        self.password.setText(config.get('LoginData', 'password'))


        confirm = QtWidgets.QPushButton("Login")

        confirm.clicked.connect(self.close)
        confirm.setDefault(True)

        layout.addWidget(confirm, 3, 1, 1, 2)
        self.setLayout(layout)
        self.setWindowTitle("Login")
        self.setWindowModality(Qt.ApplicationModal)
        self.exec_()


    def close(self):
        config.set('LoginData', 'username', self.userName.text())
        config.set('LoginData', 'password', self.password.text())
        with open('settings.cfg',  'w') as configfile:
            config.write(configfile)
        super(LoginDialog, self).close()


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, characters, clients):
        super(SettingsDialog, self).__init__()

        layout = QtWidgets.QGridLayout()

        layout.addWidget(QtWidgets.QLabel('Characters'), 2, 0)

        self.characters = QtWidgets.QListWidget()

        old_chars = [char for i, char in config.items('Characters')]
        for char in characters:
            item = QtWidgets.QListWidgetItem(char)

            flag = char in old_chars
            if flag and char in clients and not clients[char].state.text() == 'Offline':
                item.setFlags(item.flags () & ~Qt.ItemIsUserCheckable)
                print(char)
            item.setFlags(item.flags () & ~Qt.ItemIsAutoTristate)
            item.setCheckState(2*int(flag))
            self.characters.addItem(item)

        layout.addWidget(self.characters, 2, 1, 1, 2)

        confirm = QtWidgets.QPushButton("Login")

        confirm.clicked.connect(self.close)
        confirm.setDefault(True)

        layout.addWidget(confirm, 5, 1, 1, 2)
        self.setLayout(layout)
        self.setWindowTitle("Configuration")
        self.setWindowModality(Qt.ApplicationModal)
        self.exec_()


    def close(self):
        for i in range(self.characters.count()):
            if self.characters.item(i).checkState() == Qt.Checked:
                config.set('Characters', 'name'+str(i), self.characters.item(i).text())
            else:
                config.remove_option('Characters', 'name'+str(i))
        with open('settings.cfg',  'w') as configfile:
            config.write(configfile)
        super(SettingsDialog, self).close()


def excepthook(type_, value, traceback_):
    traceback.print_exception(type_, value, traceback_)
    QtCore.qFatal('')
sys.excepthook = excepthook

if __name__ == '__main__':

    logging.basicConfig(filename='chat.log')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logger.info('Start')
    #global imageLoader

    app = QtWidgets.QApplication(sys.argv)
    setTheme('dark')
    ex = ChatClient()

    sys.exit(app.exec_())
