#!/user/bin/env python
# -*- coding: utf-8 -*-
import struct
from AccelBrainBeat.brain_beat import BrainBeat


class MonauralBeat(BrainBeat):
    '''
    具象クラス
    バイノーラルビートとモノラルビートの具象的差異を下位クラスで記述する
    Template Method Patternの構成

    '''

    def write_stream(self, stream, left_chunk, right_chunk, volume):
        '''
        具象メソッド
        モノラルビートを生成する

        Args:
            stream:         PyAudioのストリーム
            left_chunk:     左音源に対応するチャンク
            right_chunk:    右音源に対応するチャンク
            volume:         音量

        Returns:
            void
        '''
        if len(left_chunk) != len(right_chunk):
            raise ValueError()

        for i in range(len(left_chunk)):
            chunk = (left_chunk[i] + right_chunk[i]) * volume
            data = struct.pack("2f", chunk, chunk)
            stream.write(data)

    def read_stream(self, left_chunk, right_chunk, volume, bit16=32767.0):
        '''
        具象メソッド
        wavファイルに保存するモノラルビートを読み込む

        Args:
            left_chunk:     左音源に対応するチャンク
            right_chunk:    右音源に対応するチャンク
            volume:         音量
            bit16:          整数化の条件

        Returns:
            フレームのlist
        '''
        if len(left_chunk) != len(right_chunk):
            raise ValueError()

        frame_list = []
        for i in range(len(left_chunk)):
            chunk = int((left_chunk[i] + right_chunk[i]) * bit16 * volume)
            data = struct.pack("2h", chunk, chunk)
            frame_list.append(data)

        return frame_list
