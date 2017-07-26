#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 12:07:48 2017

@author: Chaelya
"""

from PyQt5.QtCore import Qt, QAbstractListModel, QSortFilterProxyModel, QModelIndex, QVariant, QSize
from PyQt5.QtGui import QBrush, QColor, QPalette, QPen, QIcon
from PyQt5.QtWidgets import QStyle, QStyledItemDelegate


import Utility as util

colorDict = {'None': '#FFFFBB',
             'Female': '#FF6699',
             'Male':'#6699FF',
             'Herm':'#9B30FF',
             'Male-Herm':'#007FFF',
             'Shemale':'#CC66FF',
             'Cunt-Boy':'#00CC66',
             'Transgender':'#EE8822' }



class CharacterDelegate (QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)

    def paint (self, painter, option, index ):
        #if option.state == QStyle.State_Selected:
        #    painter.fillRect(option.rect, option.palette.color(QPalette.Highlight))

        icon = index.data(Qt.DecorationRole)

        title = index.data(Qt.DisplayRole)
        description = index.data(Qt.UserRole + 1)
        iconStatus = index.data(Qt.UserRole + 2)
        iconFriend = index.data(Qt.UserRole + 3)


        if index.data(Qt.UserRole + 4):
            iconMod = QIcon('resources/chanop.png')
            r = option.rect
            icon.paint(painter, r, Qt.AlignLeft)
            r = option.rect.adjusted(32, 0, 0, -15)
            iconMod.paint(painter, r, Qt.AlignLeft)

        #paint status icon

        r = option.rect
        icon.paint(painter, r, Qt.AlignLeft)
        r = option.rect.adjusted(34, 2, 0, -17)
        iconStatus.paint(painter, r, Qt.AlignLeft)

        #paint friend icon

        r = option.rect
        icon.paint(painter, r, Qt.AlignLeft)
        r = option.rect.adjusted(34, 17, 0, -2)
        iconFriend.paint(painter, r, Qt.AlignLeft)

        color = index.data(Qt.ForegroundRole)
        pen = painter.pen()
        painter.setPen(color)
        r = option.rect.adjusted(50, 0, 0, -15)
        painter.drawText(r, Qt.AlignBottom|Qt.AlignLeft|Qt.TextWordWrap, title)

        painter.setPen(pen)
        r = option.rect.adjusted(50, 15, 0, 0);
        painter.drawText(r, Qt.AlignLeft|Qt.TextWordWrap, description)


    def sizeHint (self, option, index ):
        return QSize(200, 30)


class UserModel(QAbstractListModel):
    def __init__(self, clients, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.users = []
        self.ownCharacters = clients

        self.globalOps = []
        self.friendList = []
        self.ignoreList = []

    def rowCount(self, parent = QModelIndex()) :
        return len(self.users)

    def flags(self, index):
        return Qt.ItemIsEnabled


    def data(self, index, role = Qt.DisplayRole ):
        if index.isValid():
            char = self.users[index.row()]
            if (role == Qt.DisplayRole):
                return QVariant('{}'.format(char.name) )
            elif (role == Qt.UserRole + 1):
                return QVariant('({}) {}'.format(char.status, char.statmsg) )
            elif (role == Qt.UserRole + 2):
                return QVariant(QIcon('resources/{}.png'.format(char.status)) )
            elif (role == Qt.UserRole + 3):
                if char.isFriend():
                    return QVariant(QIcon('resources/friend.png') )
                else:
                    return QVariant(QIcon('resources/blank.png') )
            elif (role == Qt.DecorationRole):
                util.imageLoader.loadImage(char.name)
                return QVariant(util.imageLoader.getIcon(char.name) )
            elif (role == Qt.ForegroundRole ):
                color = colorDict[char.gender]
                qcolor = QColor()
                qcolor.setNamedColor(color)
                return QVariant(QPen(qcolor))
            return self.addedData(char, role)
        return None

    def addedData(self, char, role):
        return None

    def addUsers(self, payload):
        l = len(self.users)
        self.beginInsertRows(QModelIndex(), l, l+len(payload)-1)
        for item in payload['characters']:
            j = 0
            for i, user in enumerate(self.users):
                j = i
                if user.name == item[0]:
                    break
            user = User(self, item[0], item[1], item[2], item[3])
            if j == len(self.users):
                self.users.append(user)
            else:
                self.users[i] = user
        self.endInsertRows()
        self.dataChanged.emit(self.index(0, 0), self.index(l, 0))


    def addUser(self, payload):
        if payload['identity'] in [x.name for x in self.users]:
            return
        user = User(self, payload['identity'], payload['gender'], payload['status'], '')
        l = len(self.users)
        self.beginInsertRows(QModelIndex(), l, l)
        self.users.append(user)
        self.endInsertRows()

    def changeStatus(self, character, status, message):
        for i, user in enumerate(self.users):
            if user.name == character:
                user.setStatus(status, message)
                self.dataChanged.emit(self.index(i, 0), self.index(i, 0))
                break

    def removeUser(self, character):
        for i, user in enumerate(self.users):
            if user.name == character:
                self.beginRemoveRows(QModelIndex(), i, i)
                del self.users[i]
                self.endRemoveRows()
                break

    def addFriends(self, friends):
        self.friendList.extend(friends)

    def addIgnore(self, ignore):
        self.ignoreList.append(ignore)

    def removeIgnore(self, ignore):
        self.ignoreList.remove(ignore)

    def addUsersToChannel(self, ID, users):
        for user in self.users:
            if user.name in [x['identity'] for x in users]:
                user.addChannel(ID)
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount()-1, 0))

    def removeUserFromChannel(self, ID, character):
        for i, user in enumerate(self.users):
            if user.name == character:
                user.removeChannel(ID)
                self.dataChanged.emit(self.index(i, 0), self.index(i, 0))
                break
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount()-1, 0))

    def addChanOps(self, ID, characters):
        for user in self.users:
            if user.name in characters:
                user.addChanOp(ID)
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount()-1, 0))

    def removeChanOp(self, ID, character):
        for i, user in enumerate(self.users):
            if user.name == character:
                user.removeChanOp(ID)
                self.dataChanged.emit(self.index(i, 0), self.index(i, 0))

class UserFilter(QSortFilterProxyModel):
    def __init__(self, ID = None, onlyOwn = False, onlyFriends = False):
        super(UserFilter, self).__init__()
        self.ID = ID
        self.setDynamicSortFilter(True)
        self.onlyOwn = onlyOwn
        self.onlyFriends = onlyFriends

    def getName(self, index):
        newIndex = self.mapToSource(index)
        return self.sourceModel().users[newIndex.row()].name;

    def getObject(self, index):
        newIndex = self.mapToSource(index)
        return self.sourceModel().users[newIndex.row()];

    def addedData(self, char, role):
        if (role == Qt.UserRole + 4):
                return QVariant(char.isChanOp(self.ID) )

        return None

    def filterAcceptsRow(self, index, parent):
        test1 = True
        test2 = True
        test3 = True
        if self.onlyOwn:
            test1 = self.sourceModel().users[index].name in self.sourceModel().ownCharacters.keys()
        if self.ID != None:
            test2 = self.ID in self.sourceModel().users[index].channels
        if self.onlyFriends:
            test3 = self.sourceModel().users[index].isFriend()
        return test1 and test2 and test3

class User():
    def __init__(self, userlist, name, gender, status, statmsg):
        self.name = name
        self.gender = gender
        self.status = status
        self.statmsg = statmsg
        self.channels = []
        self.opInChannel = []
        self.ownerChannel = []

        self.userlist = userlist


    def setStatus(self, status, message):
        self.status = status
        self.statmsg = message

    def addChannel(self, channel):
        if channel not in self.channels:
            self.channels.append(channel)

    def addChanOp(self, channel):
        if channel not in self.opInChannel:
            self.opInChannel.append(channel)

    def removeChannel(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)

    def removeChanOp (self, channel):
        if channel in self.opInChannel:
            self.opInChannel.remove(channel)

    def isChanOp(self, ID):
        return ID in self.opInChannel

    def isFriend(self):
        return self.name in self.userlist.friendList

    def isIgnored(self):
        return self.name in self.userlist.ignoreList




def testUserModel(qtmodeltester):
    model = UserModel()
    items = {'characters':[[str(i),"","",""] for i in range(4)]}
    model.addUsers(items)
    qtmodeltester.check(model)
    assert model.rowCount()==4