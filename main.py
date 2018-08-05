#!/usr/bin/env python

from PyQt5.QtWidgets import *
import sys
from tcpserver import  *


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tcpServer = TcpServer()
    sys.exit(app.exec_())


