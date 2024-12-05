#! /usr/bin/env python3
# coding=utf-8

# 导入必要的库
import os
import sys
import time
import serial
import serial.tools.list_ports

# 设置QT_API环境变量，以便使用PyQt5
os.environ["QT_API"] = "pyqt5"
import qtpy

# 从qtpy模块导入QtCore, QtWidgets, QtGui
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

# 导入Xeryon类和Stage枚举
from Xeryon import *

class XeryonController(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化Xeryon控制器，指定COM端口和波特率
        self.controller = Xeryon("/dev/ttyACM0", 115200)
        # 添加Z轴，并指定使用XLA_1250_3N阶段
        self.axisX = self.controller.addAxis(Stage.XLA_1250_3N, "Z")
        # 初始化用户界面
        self.initUI()
        # 启动控制器
        self.controller.start()
        # 重置控制器
        self.controller.reset()

    def initUI(self):
        # 初始化用户界面组件和布局
        self.position1 = -19
        self.position2 = 19

        self.setWindowTitle('Xeryon Controller')
        self.setGeometry(100, 100, 1000, 400)

        layout = QVBoxLayout()

        self.logText = QTextEdit(self)
        self.logText.setReadOnly(True)
        layout.addWidget(self.logText)

        controlLayout = QHBoxLayout()

        self.stopButton = QPushButton('Stop Scan', self)
        # 连接停止扫描按钮的点击事件到stopScan方法
        self.stopButton.clicked.connect(self.stopScan)
        controlLayout.addWidget(self.stopButton)

        self.homeButton = QPushButton('Homing', self)
        # 连接归零按钮的点击事件到homing方法
        self.homeButton.clicked.connect(self.homing)
        controlLayout.addWidget(self.homeButton)

        self.position1Edit = QLineEdit(self)
        self.position1Edit.setText(str(self.position1))
        self.position1Edit.setPlaceholderText("Enter Position 1")
        # 连接位置1输入框的编辑完成事件到setPosition1方法
        self.position1Edit.editingFinished.connect(self.setPosition1)
        controlLayout.addWidget(self.position1Edit)

        self.position2Edit = QLineEdit(self)
        self.position2Edit.setText(str(self.position2))
        self.position2Edit.setPlaceholderText("Enter Position 2")
        # 连接位置2输入框的编辑完成事件到setPosition2方法
        self.position2Edit.editingFinished.connect(self.setPosition2)
        controlLayout.addWidget(self.position2Edit)

        self.position1Button = QPushButton('Position 1', self)
        # 连接位置1按钮的点击事件到moveToPosition方法
        self.position1Button.clicked.connect(lambda: self.moveToPosition(self.position1))
        controlLayout.addWidget(self.position1Button)

        self.position2Button = QPushButton('Position 2', self)
        # 连接位置2按钮的点击事件到moveToPosition方法
        self.position2Button.clicked.connect(lambda: self.moveToPosition(self.position2))
        controlLayout.addWidget(self.position2Button)

        self.positionLabel = QLabel('Position: 0 mm')
        controlLayout.addWidget(self.positionLabel)

        self.speedLabel = QLabel('Speed:')
        controlLayout.addWidget(self.speedLabel)

        self.speedSlider = QSlider(Qt.Horizontal)
        self.speedSlider.setRange(1, 100)
        self.speedSlider.setValue(80)  # 默认速度基于数据表
        # 连接速度滑块的值改变事件到setSpeed方法
        self.speedSlider.valueChanged.connect(self.setSpeed)
        controlLayout.addWidget(self.speedSlider)

        layout.addLayout(controlLayout)

        self.statusLabel = QLabel('Status: Idle')
        layout.addWidget(self.statusLabel)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def stopScan(self):
        # 停止扫描并更新日志和状态标签
        self.axisX.stopScan()
        self.updateLog('Scan stopped')
        self.statusLabel.setText('Status: Idle')

    def homing(self):
        # 执行归零操作并更新日志和状态标签
        self.axisX.findIndex()
        self.updateLog('Homing')
        self.statusLabel.setText('Status: Homing')
        self.axisX.stopScan()

    def moveToPosition(self, position):
        # 移动到指定位置并更新日志和状态标签
        self.axisX.setDPOS(position)
        self.updateLog(f'Moving to position {position} mm')
        self.statusLabel.setText(f'Status: Moving to {position} mm')

    def setSpeed(self, value):
        # 设置速度并更新日志
        self.axisX.setSpeed(value)
        self.updateLog(f'Speed set to {value} mm/s')

    def updateLog(self, message):
        # 更新日志文本框和位置标签
        self.logText.append(message)
        self.positionLabel.setText(f'Position: {self.axisX.getEPOS()} mm')

    def setPosition1(self):
        try:
            # 设置位置1并更新日志
            self.position1 = float(self.position1Edit.text())
            self.updateLog(f'Position 1 set to {self.position1} mm')
        except ValueError:
            self.updateLog('Invalid input for Position 1. Please enter a valid number.')

    def setPosition2(self):
        try:
            # 设置位置2并更新日志
            self.position2 = float(self.position2Edit.text())
            self.updateLog(f'Position 2 set to {self.position2} mm')
        except ValueError:
            self.updateLog('Invalid input for Position 2. Please enter a valid number.')

    def closeEvent(self, event):
        # 在关闭事件中停止扫描和控制器
        self.axisX.stopScan()
        self.controller.stop()
        super().closeEvent(event)

if __name__ == '__main__':
    # 创建QApplication实例并运行
    app = QApplication(sys.argv)
    controller = XeryonController()
    controller.show()
    sys.exit(app.exec_())
