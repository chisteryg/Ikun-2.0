# 多线程池QThread线程
from PyQt5.QtCore import QThread, pyqtSignal
from concurrent.futures.thread import ThreadPoolExecutor

from time import sleep

from utils import Key


class KeyPressThread(QThread):
    playTimesSingal = pyqtSignal(float)
    playEnding = pyqtSignal()
    playWaiting = pyqtSignal()  # 等待中
    playWaitingEnd = pyqtSignal()  # 等待结束

    def __init__(self, parentObj):
        # keyList按键列表,使用多进程模拟按键
        super(KeyPressThread, self).__init__()
        self.parentObj = parentObj
        self.mode = self.parentObj.mode  # 演奏模式
        self.key = Key.KeyInput()  # 模拟按键类
        self.mid = self.parentObj.midiProcess  # midi处理类
        print('parentMid:', self.parentObj.midiProcess)
        self.pool = ThreadPoolExecutor(10)  # 线程池，最大线程数量
        self.index = 0  # 当前下标
        self.stop = False  # 退出标志
        self.pause = False  # 暂停标志
        self.waiting = False  # 是否进行等待

    def run(self) -> None:
        print('子线程准备就绪')
        print(self.pool)
        # 可调节等待时间功能

        self.playWaiting.emit()  # 进入等待
        sleep(self.parentObj.wait_spinBox.value())
        self.playWaitingEnd.emit()  # 等待结束

        while True:
            if self.index >= len(self.mid.event_tick) or self.stop:
                # 如果到达末尾或stop标志为True，退出循环
                print('end')
                break
            if not self.pause:
                if self.waiting:
                    # 如果需要等待
                    self.playWaiting.emit()  # 进入等待
                    sleep(self.parentObj.wait_spinBox.value())
                    self.playWaitingEnd.emit()  # 等待结束
                    self.waiting = False  # 等待结束后重置状态

                tick = str(self.mid.event_tick[self.index])  # 取出当前刻度
                for item in self.mid.event_dict[tick].values():
                    print(item)

                    if self.parentObj.mode == 1:
                        # 模式一
                        if item['type'] == 'note_on':
                            # print('模式一按压')
                            self.pool.submit(self.key.ys_press_key, item['val'])
                        elif item['type'] == 'note_off':
                            # print('模式一松开')
                            self.pool.submit(self.key.ys_relase_key, item['val'])
                    elif self.parentObj.mode == 2:
                        # 模式二
                        # print('模式二按压')
                        if item['type'] == 'note_on':
                            self.pool.submit(self.key.ys_press_key_mode2, item['val'])
                # 休眠
                wait = (self.mid.event_tick[self.index + 1] - self.mid.event_tick[self.index]) * self.mid.tick_s
                # 可调节倍速功能
                wait = wait * (1.0 / self.parentObj.speed_doubleSpinBox.value())
                sleep(
                    wait
                )
                self.playTimesSingal.emit(
                    int((100.0 * self.mid.event_tick[self.index]) / self.mid.event_tick[-1])
                )  # 发射进度
                self.index += 1

        self.playEnding.emit()  # 演奏完成，发射信号
        return


if __name__ == '__main__':
    # k = KeyPressThread(1, )
    # k.start()
    # k.wait()

    # k = Key.KeyInput()
    # pool = multiprocessing.Pool(10)
    # pool.apply_async(k.ys_press_key_mode2, (64, ))
    # pool.apply_async(k.ys_press_key_mode2, (65, ))
    # pool.close()
    # pool.join()

    pass
