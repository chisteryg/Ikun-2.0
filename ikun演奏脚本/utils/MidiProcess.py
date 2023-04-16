import os
import mido
import json


class MidiProcess:
    def __init__(self, midiPath=''):
        self.midipath = midiPath
        # 拼接json路径
        # self.jsonPath = '../midiJson/'
        self.jsonPath = 'midiJson/'
        self.jsonPath = self.jsonPath + midiPath.split('/')[-1] + '.txt'
        # 解析后的文件存在，直接读取
        if os.path.exists(self.jsonPath):
            self.load()
            return
        # 不存在则进行分析
        self.mid = mido.MidiFile(midiPath)  # 加载midi文件
        self.type = self.mid.type  # midi文件类型
        self.lenth = self.mid.length  # 总长度
        self.maxTime = -1  # 最大时间初始设置为-1
        self.C = 60  # 中央C
        self.event_dict, self.event_tick = self.event_Dict()
        self.tick_s = self.getTick_s()  # 每刻所对应的时间(s)
        self.save()  # 将处理结果作为json保存

    def getTime(self, s):
        # 取得一条消息中的时间
        time = ''
        for i in s:
            if str(i).isdigit():
                time += str(i)
        if time != '':
            return int(time)
        else:
            return 0

    def getTick_s(self):
        # 获取每一个刻对应的秒数
        s = 1.0 * self.lenth / self.maxTime
        return s

    def event_Dict(self):
        # 读取事件并合并音轨, 创建排序后的刻度列表
        event = {}
        tick = []

        for i, track in enumerate(self.mid.tracks):  # enumerate()：创建索引序列，索引初始为0
            # print('Track {}: {}'.format(i, track.name))
            time = 0  # 每个音轨初始时间设置为零
            for msg in track:  # 每个音轨的消息遍历
                # print(msg)
                t = str(msg).split(' ')  # 将一条消息拆开
                # print(t)
                val = -1
                if t[0] == 'note_on' or t[0] == 'note_off':
                    # 如果本条消息是按下或松开
                    # print(t, i)
                    time += self.getTime(str(t[4]).split('=')[-1])  # 增加time的时刻

                    # 取出当前键位值
                    val = self.getTime(str(t[2]).split('=')[-1])
                    # print('note:{}, time{}'.format(val, time))

                    # 将按键事件添加到字典中
                    if str(time) in event.keys():
                        # 如果event中包含了本time的键
                        event[str(time)][len(event[str(time)])] = {
                            'type': t[0],
                            'val': val,
                            'track': i
                        }
                    else:
                        event[str(time)] = {
                            0: {
                                'type': t[0],
                                'val': val,
                                'track': i
                            }
                        }
                    # 如果本刻度没有添加到刻度列表中, 进行添加
                    if time not in tick:
                        tick.append(time)

            tick.sort()  # 刻度列表排序

            if time > self.maxTime:
                self.maxTime = time  # 最大时间

        return event, tick

    def save(self):
        # 将数据保存为json
        if not os.path.exists(self.jsonPath):
            # json路径不存在，创建并保存数据
            self.data = {
                'lenth': self.lenth,
                'maxTime': self.maxTime,
                'event_dict': self.event_dict,
                'event_tick': self.event_tick,
                'tick_s': self.tick_s,
            }

            # if not os.path.exists('../midiJson/'):
            #     os.mkdir('../midiJson/')
            if not os.path.exists('midiJson/'):
                os.mkdir('midiJson/')
            # 将py字典转化为json
            self.data = json.dumps(self.data)
            # 写入文件
            # print('保存:', self.jsonPath)
            with open(self.jsonPath, 'w') as f:
                f.writelines(self.data)

    def load(self):
        # 加载json中的内容
        self.data = None
        with open(self.jsonPath, 'r') as f:
            self.data = f.readlines()
        # 将json转换为py字典
        self.data = json.loads(self.data[0])
        # print(self.data)
        self.lenth = self.data['lenth']
        self.maxTime = self.data['maxTime']
        self.event_dict = self.data['event_dict']
        self.event_tick = self.data['event_tick']
        self.tick_s = self.data['tick_s']

    def classInfo(self):
        print('event_tick:', end='\n\n')
        print(self.event_tick, end='\n\n')

        print('event_dict:', end='\n\n')
        print(self.event_dict, end='\n\n')

        print('tick_s:', end='\n\n')
        print(self.tick_s, end='\n\n')

        print('lenth:', end='\n\n')
        print(self.lenth, end='\n\n')
        print('maxTime:', end='\n\n')
        print(self.maxTime, end='\n\n')


if __name__ == '__main__':
    # path = r'../midi/卡农，简单 游戏演奏 原神.mid'
    # mid = MidiProcess(path)
    m = MidiProcess('../midi/原神璃月战斗音乐（风物之诗琴演奏用）.mid')
