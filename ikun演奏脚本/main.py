# 主进程
import os

from PyQt5 import QtGui
from PyQt5.Qt import *
from PyQt5.QtCore import pyqtSlot

from utils.MidiProcess import MidiProcess
from utils.CreateQtThread2 import KeyPressThread
from utils.MoveWidget import MoveWidget
from qt.ui import midiForm, errorDialog


class Window(MoveWidget, midiForm.Ui_midiForm):
    def __init__(self, title="No Title"):
        super().__init__()

        self.move(400, 250)  # 窗口位置
        QtGui.QFontDatabase.addApplicationFont("qt/static/font/优设标题圆.otf")  # 加载字体
        self.setStyleSheet("font-family: YouSheBiaoTiYuan;")
        self.setupUi(self)  #
        self.setWindowTitle(title)  # 标题
        self.setWindowFlags(Qt.FramelessWindowHint)  # 置顶并隐藏标题栏
        self.create_ui()  # 控件操作
        self.show()

    def create_ui(self):
        self.init_Val()  # 初始化变量
        self.loadMidiFile()  # 将mid文件添加到listwidget中
        self.connectSingal()  # 连接信号

    def init_Val(self):
        # 初始化变量
        self.midiProcess = None  # midi处理类
        self.mode = 1  # 演奏模式
        self.playing = self.STOP  # 当前演奏状态为未演奏
        self.playThread = None  # 演奏线程
        self.playingName = None  # 当前正在演奏音乐的名称

    def loadMidiFile(self):
        # 添加midi项到listwidget中
        midifiles = os.listdir("midi/")
        self.midiSelect_listWidget.addItems(midifiles)

    def connectSingal(self):
        # 连接信号
        self.midiSelect_listWidget.currentTextChanged.connect(
            # 当前mid改变时，修改标签
            self.changeText
        )

    def changeText(self):
        # listWidget切换条目时，切换label和按钮的文本
        # 修改标签文本
        self.mid_label.setText(
            self.midiSelect_listWidget.currentItem().text()
        )

        # 修改按钮文本
        if self.playing == self.PAUSE:
            print('暂停中')
            if self.mid_label.text() == self.playingName:
                self.play_pushButton.setText('继续')
            else:
                self.play_pushButton.setText('开始')
        elif self.playing == self.PLAYING:
            print('演奏中')
            if self.mid_label.text() == self.playingName:
                self.play_pushButton.setText('暂停')
            else:
                self.play_pushButton.setText('开始')

    def stopPlay(self):
        # 终止演奏并初始化状态
        if self.playThread != None:
            # 线程退出
            self.playThread.stop = True
            self.playThread.terminate()
            self.playThread.deleteLater()
        self.init_Val()  # 初始化变量
        self.progressBar.setValue(0)  # 进度条置零
        self.play_pushButton.setText('开始')

    def disableButton(self):
        # 禁用按钮
        self.play_pushButton.setDisabled(True)
        self.stop_pushButton.setDisabled(True)

    def enableButton(self):
        # 启用按钮
        self.play_pushButton.setEnabled(True)
        self.stop_pushButton.setEnabled(True)

    def notMove(self):
        # 本次不进行移动
        self.isMove = False

    @pyqtSlot()
    def on_close_pushButton_clicked(self):
        # 关闭窗口，销毁窗体
        self.close()
        self.destroy()

    def on_close_pushButton_pressed(self):
        self.notMove()

    @pyqtSlot()
    def on_play_pushButton_clicked(self):
        # 开始按钮，分析midi并准备演奏
        if self.mid_label.text() != None and self.mid_label.text() != self.playingName:
            # 当前有演奏线程，且本次执行音乐与线程不一致
            # 停止线程音乐
            self.stopPlay()

        if self.playing == self.PLAYING:
            if self.playThread:
                # 当前正在演奏，暂停
                self.playing = self.PAUSE
                self.playThread.pause = True
                self.play_pushButton.setText('继续')
        elif self.playing == self.PAUSE:
            if self.playThread:
                # 处于演奏暂停状态
                # 解除暂停
                self.playing = self.PLAYING
                self.play_pushButton.setText('暂停')
                msg = '单击确定后' + str(self.wait_spinBox.value()) + 's，将从断点继续演奏'
                self.e = errorDialog.ErrorDialog(self, msg)
                self.playThread.waiting = True  # 需要暂停
                self.playThread.pause = False
        elif self.playing == self.STOP:
            # 当前未演奏
            # 状态修改为进行演奏
            self.playing = self.PLAYING
            try:
                # 加载midi
                path = 'midi/' + self.midiSelect_listWidget.currentItem().text()
                self.midiProcess = MidiProcess(path)
                print('midiProcess', self.midiProcess)
                # self.midiProcess.classInfo()    # midi信息
            except Exception as e:
                print(e)
                msg = 'midi处理异常\n'
                msg += str(e)
                self.e = errorDialog.ErrorDialog(self, msg)
                return

            msg = '单击确定后' + str(self.wait_spinBox.value()) + 's，将开始演奏'
            self.e = errorDialog.ErrorDialog(self, msg)

            '''创建演奏线程'''
            try:
                self.play_pushButton.setText('暂停')
                # 当前演奏曲目的名称
                self.playingName = self.mid_label.text()
                self.playThread = KeyPressThread(parentObj=self)
                self.playThread.playTimesSingal[float].connect(
                    # 实时进度
                    lambda val: self.progressBar.setValue(val)
                )
                self.playThread.playEnding.connect(self.stopPlay)  # 线程退出后，初始化状态
                self.playThread.playWaiting.connect(self.disableButton)  # 线程处于等待状态，禁用按键
                self.playThread.playWaitingEnd.connect(self.enableButton)  # 线程等待状态结束，启用用按键
                self.playThread.start()
                # self.playThread.exec()

            except Exception as e:
                print(e)
                self.stopPlay()
                msg = '子线程异常\n'
                msg += str(e)
                self.e = errorDialog.ErrorDialog(self, msg)
                return

    def on_play_pushButton_pressed(self):
        self.notMove()

    @pyqtSlot()
    def on_stop_pushButton_clicked(self):
        # 停止按钮
        self.stopPlay()

    def on_stop_pushButton_pressed(self):
        self.notMove()

    @pyqtSlot()
    def on_mode1_radioButton_clicked(self):
        # 切换模式
        self.mode = 1

    @pyqtSlot()
    def on_mode2_radioButton_clicked(self):
        # 切换模式
        self.mode = 2

    PLAYING = 1
    PAUSE = 2
    STOP = 3


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)  # 加入参数
    window = Window(title="原神IKUN演奏脚本(By:Mr_yg)")
    sys.exit(app.exec_())  # 循环执行
