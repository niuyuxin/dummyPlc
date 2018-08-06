#!/usr/bin/env python

from PyQt5.QtWidgets import *
import sys
from dummyplc import *


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dummyPlc = DummyPlc()
    dummyPlc.show()
    sys.exit(app.exec_())


