#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *

class TcpServer(QObject):
    MaxBufferSize = 2000
    def __init__(self):
        super().__init__()
        self.tcpServer = QTcpServer(self) # should have parent
        self.acceptSocket = None
        self.tcpSocketBuffer = []
        self.sendCount = 0
        self.sendTimer = QTimer(self)
        self.sendTimer.timeout.connect(self.onCycleDataSending)
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
                self.sendTimer.start(1000)
                print("new socket", self.acceptSocket)
        except Exception as e:
            print("on new connection", str(e))
    @pyqtSlot()
    def onSocketDisconnect(self):
        socket = self.sender()
        self.sendTimer.stop()
        socket.deleteLater()

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
            time = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
            print("Read data, size = {}:{}".
                  format(len(self.tcpSocketBuffer), self.tcpSocketBuffer), time)
        except Exception as e:
            print("on Ready to read ", str(e))

    def onCycleDataSending(self):
        try:
            data = bytearray()
            for i in range(2000):
                data.append(0xff)
            self.acceptSocket.write(QByteArray(data))
            self.acceptSocket.waitForBytesWritten()
        except Exception as e:
            print(str(e), "onCycleDataSending")