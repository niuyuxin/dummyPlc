#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *

class TcpServer(QObject):
    MaxBufferSize = 2000
    receivedData = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def init(self):
        self.tcpServer = QTcpServer(self) # should have parent
        self.acceptSocket = None
        self.tcpSocketBuffer = []
        if not self.tcpServer.listen(QHostAddress.AnyIPv4, 2000):
            print("listen error")
            return
        else:
            self.tcpServer.newConnection.connect(self.onNewConnection)
            print("listen successful")

    @pyqtSlot()
    def onNewConnection(self):
        try:
            while self.tcpServer.hasPendingConnections():
                self.acceptSocket = self.tcpServer.nextPendingConnection()
                self.acceptSocket.readyRead.connect(self.onReadyToRead)
                self.acceptSocket.disconnected.connect(self.onSocketDisconnect)
                print("new socket", self.acceptSocket)
        except Exception as e:
            print("on new connection", str(e))
    @pyqtSlot()
    def onSocketDisconnect(self):
        self.acceptSocket.deleteLater()
        self.acceptSocket = None

    @pyqtSlot()
    def onReadyToRead(self):
        try:
            temp = self.acceptSocket.readAll()
            if len(self.tcpSocketBuffer) < TcpServer.MaxBufferSize:
                b = temp.data()
                self.tcpSocketBuffer.extend(b)
            else:
                self.tcpSocketBuffer = []
                self.tcpSocketBuffer.extend(temp.data())

            if len(self.tcpSocketBuffer) != TcpServer.MaxBufferSize:
                print(len(self.tcpSocketBuffer))
                return
            self.receivedData.emit(self.tcpSocketBuffer)
        except Exception as e:
            print("on Ready to read ", str(e))

    def onDataToSend(self, data):
        if self.acceptSocket == None: return
        try:
            self.acceptSocket.write(data)
            self.acceptSocket.waitForBytesWritten()
        except Exception as e:
            print(str(e), "onCycleDataSending")