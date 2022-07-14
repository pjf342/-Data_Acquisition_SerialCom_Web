import time as t
start_time = t.perf_counter()
import numpy as np
import serial  # pyserial
import threading as th
from PyQt5.QtCore import *
print(f'Serial imports loaded in {t.perf_counter() - start_time} seconds')


class SerialCommunication(th.Thread):

    def __init__(self, com, baud):
        """

        :param str com: com port
        :param int baud: baud rate
        :param float or int time_interval: seconds
        """
        super().__init__()  # Allows to call on class with an inheritance
        # while True:
        #     print(t.perf_counter())
        self.serial_port = com
        self.serial_baud = baud

        self.delimiter = ';'
        self.start_time = 0

        self.pause_bool = False
        self.paused_time = 0
        self.paused_start_time = 0
        self.pause_time_arr = np.array([], dtype=float)
        self.total_time_paused = 0

        self.start_time_bool = False

        self.thread = None
        self.serial_data = None
        self.serial = None
        self.current_time = None
        self.elapsed_time = None

        self.thread_data_acquisition()

        t.sleep(5)
        print(f'Serial initialization + sleep ended after {t.perf_counter() - start_time} seconds')

    def data_acquisition(self):
        while True:
            self.serial_data = self.serial.readline().decode('utf-8').strip().split(self.delimiter)
            # self.serial_data = self.serial.read(self.serial.in_waiting).decode('utf-8').strip()
            if self.serial_data is not None and not self.start_time_bool:
                self.start_time = t.perf_counter()
                self.start_time_bool = True
            if self.pause_bool:
                self.pause_fun()
            self.current_time = t.perf_counter()
            self.elapsed_time = (self.current_time - self.start_time) - self.total_time_paused
            print(f'{self.serial_data}')

    def thread_data_acquisition(self):
        self.serial = serial.Serial(self.serial_port, self.serial_baud)
        self.thread = th.Thread(target=self.data_acquisition)
        self.thread.start()

    def pause_fun(self):
        current = t.perf_counter()
        self.paused_time = current - self.paused_start_time


