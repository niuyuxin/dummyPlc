#/usb/bin/eny python3

from PyQt5.QtCore import *

class DevAttr(QObject):
    SW_UpperLimit = (1<<8)
    SW_LowerLimit = (1<<9)
    CW_Partial = (1<<14)
    CW_Selected = (1<<13)
    CW_Raise = (1<<8)
    CW_Stop = (1<<9)
    CW_Drop = (1<<10)
    valueChanged = pyqtSignal(str, str)
    monitorSubDevDict = {} # 所有监视器内的设备
    devAttrList = []
    deviceStateList = {}  # 设备状态列表
    singleCtrlOperation = {} # 单控运行标志
    singleCtrlSpeed = {}
    def __init__(self, id, name, parent=None):
        super().__init__(parent)
        self.currentPos = 0
        self.devName = name
        self.devId = id
        self.ctrlWord = DevAttr.CW_Stop
        self.stateWord = 0
        self.upperLimitPos = 0
        self.lowerLimitPos = 0
        self.targetPos = 0
        self.zeroPos = 0
        self.section = -1
        self.targetSpeed = 0
        self.actualSpeed = 0
        self.inveterState = 0
        self.warningMessage = 0

    def getStateWord(self, pos):
        return bool(self.stateWord&pos)

    def setStateWord(self, pos):
        self.stateWord |= (pos)

    def clearStateWord(self, pos):
        self.stateWord &= (~pos)

    def setCtrlWord(self, pos):
        self.ctrlWord |= pos

    def clearCtrlWord(self, pos):
        self.ctrlWord &= (~pos)

