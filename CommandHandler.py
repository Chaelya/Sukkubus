#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 21:14:41 2017

@author: Chaelya
"""

import logging
from UserModel import UserModel

class CommandHandler():

    """Take commands from the Socket Connection and push them to the gui,
       and receive user input and push it to the correct Connection
    """

    def __init__(self, gui, clients):
        self.clients = clients
        self.gui = gui

        self.userList = UserModel(clients, self.gui)

    def onMessage(self, source, code, payload):
        """Search correct action by its code"""

        logging.debug("Received {} : {}".format(code, payload))
        if code ==  "PIN":
            '''Reply to pings'''
            self.sendPing(source)
        elif code == "ADL":
            '''Sends the client the current list of chatops.'''
            pass
        elif code == "AOP":
            '''The given character has been promoted to chatop.'''
            pass
        elif code == "BRO":
            '''Incoming admin broadcast.'''
            self.showPopup(payload['message'])
        elif code == "CDS":
            '''Alerts the client that that the channel's description has changed.
               This is sent whenever a client sends a JCH to the server.'''
            self.gui.handleDescription(payload['channel'], payload['description'])
        elif code == "CHA":
            '''Sends the client a list of all public channels.'''
            self.gui.setChannels(True, payload['channels'])
        elif code == "CIU":
            '''Invites a user to a channel.'''
            self.gui.receiveChannelInvitation(payload["sender"], source,
                                              payload["title"], payload["name"])
        elif code == "CBU":
            '''Removes a user from a channel, and prevents them from re-entering.'''
            self.gui.displayPunishment(payload['channel'], payload['operator'],
                                       payload['character'], -1)
        elif code == "CKU":
            '''Kicks a user from a channel'''
            self.gui.displayPunishment(payload['channel'], payload['operator'],
                                       payload['character'], 0)
        elif code == "COA":
            '''Promotes a user to channel operator.'''
            self.userList.addChanOps(payload['channel'], [payload['character']])
        elif code == "COL":
            '''Gives a list of channel ops. Sent in response to JCH.'''
            self.userList.addChanOps(payload['channel'], payload['oplist'])
        elif code == "COR":
            '''Removes a channel operator.'''
            self.userList.removeChanOp(payload['channel'], payload['character'])
        elif code == "CSO":
            '''Sets the owner of the current channel to the character provided.'''
            pass

        elif code == "CTU":
            '''Temporarily bans a user from the channel for 1-90 minutes. A channel timeout.'''
            self.gui.displayPunishment(payload['channel'], payload['operator'],
                                       payload['character'], payload['length'])
        elif code == "DOP":
            '''The given character has been stripped of chatop status.'''
            pass
            #FKS
        elif code == "FLN":
            '''Sent by the server to inform the client a given character went offline.'''
            self.userList.removeUser(payload['character'])
        elif code == "HLO":
            '''Server hello command. Tells which server version is running and who wrote it.'''
            logging.info(payload['message'])
        elif code == "ICH":
            '''Initial channel data. Received in response to JCH, along with CDS.'''
            self.gui.enterChannel(payload['channel'], payload['users'], source)
            self.userList.addUsersToChannel(payload['channel'], payload['users'])
        elif code == "IDN":
            '''Used to inform the client their identification is successful,
               and handily sends their character name along with it.'''
            logging.info("Logged in" + str(payload))
        elif code == "JCH":
            '''Indicates the given user has joined the given channel.
               This may also be the client's character.'''
            self.userList.addUsersToChannel(payload['channel'], [payload['character']])
        #KID
        elif code == "LCH":
            '''An indicator that the given character has left the channel.
               This may also be the client's character.'''
            self.userList.removeUserFromChannel(payload['channel'], payload['character'])
        elif code == "LIS":
            '''Sends an array of all the online characters
            and their gender, status, and status message.'''
            self.userList.addUsers(payload)
        elif code == "NLN":
            '''A user connected.'''
            self.userList.addUser(payload)
        elif code == "IGN":
            '''Handles the ignore list.'''
            if payload['action'] == 'add':
                self.userList.addIgnore(payload['character'])
            elif payload['action'] == 'remove':
                self.userList.removeIgnore(payload['character'])
            else:
                for character in payload['characters']:
                    self.userList.addIgnore(character)

        elif code == "FRL":
            '''Initial friends list.'''
            self.userList.addFriends(payload['characters'])
        elif code == "ORS":
            '''Gives a list of open private rooms.'''
            self.gui.setChannels(False, payload['channels'])
        elif code == "PRD":
            '''Profile data commands sent in response to a PRO client command.'''
            if payload['type'] != 'start' and payload['type'] != 'end':
                self.gui.handleUserInfo(self.expectInfo, payload['key'], payload['value'] )
        elif code == "PRI":
            '''A private message is received from another user.'''
            self.gui.handlePrivateMessage(payload['character'], payload['message'])
        elif code == "MSG":
            '''A message is received from a user in a channel.'''
            self.gui.handleMessage(payload['character'], payload['message'],
                                   payload['channel'], False)
        elif code == "LRP":
            '''A roleplay ad is received from a user in a channel.'''
            self.gui.handleMessage(payload['character'], payload['message'],
                                   payload['channel'], True)
        elif code == "RLL":
            '''Rolls dice or spins the bottle.'''
            self.gui.handleMessage(payload['character'], payload['message'],
                                   payload['channel'], False)
        elif code == "RMO":
            '''Change room mode to accept chat, ads, or both.'''
            pass
        elif code == "RTB":
            '''Real-time bridge. Indicates the user received a note or message,
               right at the very moment this is received. '''
            print(code)
            print(payload)
        elif code == "STA":
            '''A user changed their status'''
            self.userList.changeStatus(payload['character'], payload['status'], payload['statusmsg'])
        elif code == "SYS":
            '''An informative autogenerated message from the server.
               This is also the way the server responds to some commands,
               such as RST, CIU, CBL, COL, and CUB.
               The server will sometimes send this in concert with a response command,
               such as with SFC, COA, and COR.'''
            print(code)
            print(payload)
        elif code == "TPN":
            '''A user informs you of his typing status.'''
            pass
        elif code == "UPT":
            '''Informs the client of the server's self-tracked online time,
               and a few other bits of information'''
            print(code)
            print(payload)
        elif code == "ERR":
            print("Error from server: {}".format(payload))
        else:
            print("Unhandled: {} : {}".format(code, payload))

    def updateUserList(self, users):
        pass

    def updateUserStatus(self, source, status, message):
        self.clients[source].sendMessage("STA", {'status': status, "statusmsg": message })

    def sendPing(self, source):
        self.clients[source].sendMessage("PIN")

    def getPublicChannels(self, source):
        self.clients[source].sendMessage("CHA")

    def getPrivateChannels(self, source):
        self.clients[source].sendMessage("ORS")

    def createChannel(self, source, name):
        self.clients[source].sendMessage("CCR", {'channel': name})

    def joinChannel(self, source, channel):
        self.clients[source].sendMessage("JCH", {'channel': channel})

    def rollBottle(self, source, channel):
        self.clients[source].sendMessage("RLL", {'channel': channel})

    def leaveChannel(self, source, channel):
        self.clients[source].sendMessage("LCH", {'channel': channel})

    def sendToChannel(self, source, channel, message ):
        self.clients[source].sendMessage("MSG", {'channel': channel, "message":message})

    def sendPrivateMessage(self, source, user, message):
        self.clients[source].sendMessage("PRI", {'recipient': user, "message":message})

    def getUserInfo(self, source, name):
        self.clients[source].sendMessage("PRO", {"character": name})
        self.expectInfo = name

    def setIgnore(self, source, target):
        self.clients[source].sendMessage("IGN", {"character":target,"action":"add"})

    def setUnignore(self, source, target):
        self.clients[source].sendMessage("IGN", {"character":target,"action":"delete"})
