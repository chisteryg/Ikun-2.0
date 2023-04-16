from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog, QApplication
from qt.ui.dialog import Ui_Form
from utils.MoveWidget import MoveWidget

class ErrorDialog(QDialog, Ui_Form, MoveWidget):
    def __init__(self, parent, msg, title = '错误'):
        super().__init__()
        # self.setParent(parent)
        self.setWindowModality(Qt.ApplicationModal)  # 设置模态框
        self.setWindowFlags(Qt.FramelessWindowHint)  # 置顶并隐藏标题栏
        self.setWindowTitle(title)  # 标题
        self.resize(500, 500)  # 窗口大小
        self.move(400, 250)  # 窗口位置
        self.create_ui()    # 控件操作
        self.setupUi(self)
        self.set_message(msg)
        self.exec_()

    def create_ui(self):
        QtGui.QFontDatabase.addApplicationFont("qt/static/font/优设标题圆.otf")  # 加载字体
        self.setStyleSheet("font-family: YouSheBiaoTiYuan;")
        pass

    def set_message(self, msg):
        # 设置提示信息
        self.dialog_label.setText(msg)

    @pyqtSlot()
    def on_close_button_clicked(self):
        # print(1)
        self.close()
        self.destroy()

from PyQt5.Qt import *

class Window(QWidget):
    def __init__(self, title="No Title"):
        super().__init__()
        self.setWindowTitle(title)  # 标题
        self.resize(500, 500)  # 窗口大小
        self.move(400, 250)  # 窗口位置
        self.create_ui()    # 控件操作
        self.show()

    def create_ui(self):
        self.p = QPushButton(self)
        self.p.setText('jntm')

        self.errlog = ErrorDialog(self, 'ngm,ay')
        self.errlog.setWindowModality(Qt.ApplicationModal)



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)  # 加入参数
    window = Window()
    sys.exit(app.exec_())   # 循环执行