#!/usr/bin/env python

from PyQt5.QtWidgets import *
from tcpserver import *
from DevAttr import *


class DummyPlc(QWidget):
    dataToSend = pyqtSignal(QByteArray)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dummy Plc")
        self.devAttrList = []
        self.tcpServer = TcpServer()
        self.tcpServerThread = QThread()
        self.tcpServer.moveToThread(self.tcpServerThread)
        self.tcpServer.receivedData.connect(self.onReceivedServerData)
        self.dataToSend.connect(self.tcpServer.onDataToSend)
        self.tcpServerThread.started.connect(self.tcpServer.init)
        self.tcpServerThread.start()
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.onUpdateTimerTimeout)
        self.updateTimer.start(1000)
        self.analogTimer = QTimer(self)
        self.analogTimer.timeout.connect(self.onAnalogTimerTimeout)
        self.analogTimer.start(1000)

    def onReceivedServerData(self, data):
        try:
            for i in range(0, len(data), 20):
                devData = data[i:i+20]
                devAttr = None
                isHave = False
                for dev in self.devAttrList:
                    if dev.devId == devData[1]:
                        isHave = True
                        devAttr = dev
                        break
                if not devAttr:
                    devAttr = DevAttr(devData[1], "")   # 0, 1 -> id
                                                        # 2, 3 -> 命令
                devAttr.targetSpeed = (devData[4]<<8) | devData[5]    # 4, 5 -> 速度
                # 6, 7, 8, 9 -> 目标位置
                devAttr.targetPos = (devData[6]<<24) |\
                                    (devData[7]<<16) |\
                                    (devData[8]<<8)|\
                                    (devData[9])
                devAttr.ctrlWord = (devData[10]<<8)|(devData[11]) # 10, 11 -> 控制字
                devAttr.upperLimitPos = (devData[12]<<24)| \
                                        (devData[13] << 16) | \
                                        (devData[14] << 8) | \
                                        (devData[15])
                devAttr.lowerLimitPos = (devData[16]<<24)| \
                                        (devData[17] << 16) | \
                                        (devData[18] << 8) | \
                                        (devData[19])
                if not isHave:
                    self.devAttrList.append(devAttr)
        except Exception as e:
            print(str(e))

    def onUpdateTimerTimeout(self):
        data = []
        for devAttr in self.devAttrList:
            data.extend(self.packageDevInfo(devAttr))
        self.dataToSend.emit(QByteArray(bytes(data)))

    def packageDevInfo(self, dev):
        id = dev.devId
        order = 0
        actualSpeed = dev.actualSpeed
        inveterState = dev.inveterState
        warningMessage = dev.warningMessage
        currentPos = dev.currentPos
        stateWord = dev.stateWord
        temp = [(id>>8) & 0xff, id &0xff, (order>>8)&0xff, order&0xff, (actualSpeed>>8)&0xff, actualSpeed&0xff,
                (inveterState >> 8) & 0xff, inveterState & 0xff, (warningMessage>>8)&0xff, warningMessage&0xff,
                (currentPos >> 24) & 0xff, (currentPos >>16)&0xff, (currentPos >> 8) & 0xff, currentPos & 0xff,
                (stateWord >> 24) & 0xff, (stateWord >> 16)&0xff, (stateWord >> 8) & 0xff, stateWord & 0xff
                ]
        while len(temp) < 20:
            temp.append(0)
        return temp

    def onAnalogTimerTimeout(self):
        for devAttr in self.devAttrList:
            if devAttr.ctrlWord&DevAttr.CW_Raise:
                if devAttr.currentPos < devAttr.upperLimitPos:
                    devAttr.currentPos += devAttr.targetSpeed
                    if devAttr.currentPos > devAttr.upperLimitPos:
                        devAttr.currentPos = devAttr.upperLimitPos
            elif devAttr.ctrlWord&DevAttr.CW_Drop:
                if devAttr.currentPos > devAttr.lowerLimitPos:
                    devAttr.currentPos -= devAttr.targetSpeed
                    if devAttr.currentPos < devAttr.lowerLimitPos:
                        devAttr.currentPos = devAttr.lowerLimitPos
            devAttr.actualSpeed = devAttr.targetSpeed

