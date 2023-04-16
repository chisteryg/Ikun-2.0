from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget


class MoveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.startPos = [0, 0]
        self.isMove = True

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        # 按下鼠标时的起始坐标
        self.startPos = [a0.x(), a0.y()]
        val = super(MoveWidget, self).mousePressEvent(a0)
        return val

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        # 移动的距离是老的位置 + 鼠标移动的长度
        newx = self.pos().x() + a0.x() - self.startPos[0]
        newy = self.pos().y() + a0.y() - self.startPos[1]
        if self.isMove:
            self.move(newx, newy)

        val = super(MoveWidget, self).mouseMoveEvent(a0)
        return val

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        # 释放鼠标时，使下一次进行移动
        self.isMove = True

        val = super(MoveWidget, self).mouseReleaseEvent(a0)
        return val
