#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 18:41:27 2017

@author: Chaelya
"""
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtWebSockets import QWebSocket
#from PyQt5.QtNetwork import *


import sys

import json
import requests
import logging



#chat.f-list.net:9799 #Real Server
host = "wss://chat.f-list.net:8799" #Test Server

class ClientSocket(QThread):


    onSelfLogin = pyqtSignal(str, bool)
    onMessage = pyqtSignal(str, str, dict)


    def __init__(self, character, status):
        print("New Chat Client")
        super(ClientSocket, self).__init__()
        self.state = status
        self.registered = False

        self.client = QWebSocket()
        self.client.connected.connect(self.onConnected)
        self.client.textMessageReceived.connect(self.onReceiveMessage)

        self.client.stateChanged.connect(self.onState)
        self.client.error.connect(self.onError)

        self.character = character

        self.expectInfo = ""


    def onState(self, val):
        if val == 0:
            message = 'Offline'
            self.registered = False
        elif val == 1:
            message = 'Host Lookup'
        elif val == 2:
            message = 'Connecting...'
        elif val == 3:
            message = 'Connected'
        elif val == 6:
            message = 'Closing...'
            self.registered = False
        self.state.setText(str(message))

    def onConnected(self):
        logging.info('### Connected: {} {} ###'.format(self.client.peerName(), self.client.peerAddress().toIPv6Address()))
        #Immediately follow up and register with server
        self.sendMessage("IDN", self.login)
        self.registered = True
        self.onSelfLogin.emit(self.character, True)




    def onReceiveMessage(self, message):
        #logging.debug(message)
        code = message[:3]
        if len(message) > 3:
            payload = eval(message[message.index("{"):])
        else:
            payload = {}

        self.onMessage.emit(self.character, code, payload)



    def onError(self, error):
        print(error)
        logging.error(error)


    def logoutCharacter(self):
        #if self.chatBot != None:
            #self.chatBot.game.on_abort("None")
        self.client.close()
        logging.info("### connection closed ###")


    def openConnection(self, account, password):

        self.login = { "method": "ticket",
                       "account": account,
                       "ticket": "",
                       "character": self.character,
                       "cname": "ElfClient",
                       "cversion": "0.0.1"
                     }
        self.client.open(QUrl(host))
        #self.client.ping()
        loginPayload = {"account": account, "password": password}
        r = requests.post("https://www.f-list.net/json/getApiTicket.php", data=loginPayload)

        if r.json().get('error') == None:
            print(r.json().get('error'))
            return
        ticket = r.json().get('ticket')
        print("Ticket aquired: " + ticket)
        self.login['ticket'] = ticket



    def sendMessage(self, code, payload={}):
        if self.registered or code == "IDN":
            if payload == {}:
                self.client.sendTextMessage(code)
            else:
                self.client.sendTextMessage(code+" "+json.dumps(payload))



class Ticket():

    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.ticket = ""
        self.error = ""
        if not self.getTicket():
            logging.error("Could not get Ticket: Max retries exceeded")
            self.error = "Could not get Ticket: Max retries exceeded"
        else:
            self.error = self.data.get('error')
            self.ticket = self.data.get('ticket')





    def getTicket(self):

        loginPayload = {"account": self.account, "password": self.password}
        try:
            r = requests.post("https://www.f-list.net/json/getApiTicket.php", data=loginPayload)
        except requests.exceptions.ConnectionError:
            return False

        self.data = r.json()
        #ticket=self.data.get('ticket')
        #logging.debug("Ticket aquired: " + ticket)
        return True