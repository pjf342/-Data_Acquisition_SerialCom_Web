import time as t
start_time = t.perf_counter()
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import sys
import numpy as np
import pandas as pd

import serial_communication as sc
import MPU6050_web_scrapper as ws

print(f'Main imports loaded in {t.perf_counter() - start_time} seconds')


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.show()
        self.setWindowTitle('Data Acquisition')
        self.setGeometry(100, 100, 1280, 720)
        self.menu_bar()

        self.main = QWidget()
        self.main_layout = QGridLayout()
        self.main.setLayout(self.main_layout)

        self.setCentralWidget(self.main)

        # ----- Initialize -----
        self.stop_bool = False
        self.serial_thread_start = False
        self.web_thread_start = False

        self.file_name = None
        self.com = None
        self.baud = None
        self.serial_com = None
        self.web_scrap = None
        self.com_type = None

        self.time_arr = np.array([], dtype=float)
        self.data_arr_1 = np.array([], dtype=float)
        self.data_arr_2 = np.array([], dtype=float)
        self.data_arr_3 = np.array([], dtype=float)
        self.data_arr_4 = np.array([], dtype=float)
        self.data_arr_5 = np.array([], dtype=float)
        self.data_arr_6 = np.array([], dtype=float)

        # ----- Communication selection section -----
        self.communication_type_section = QHBoxLayout()
        self.main_layout.addLayout(self.communication_type_section, 0, 0)

        self.communication_type_label = QLabel('Communication Type:')
        self.communication_type_dropbox = QComboBox()
        self.communication_type_dropbox.addItems([' ', 'Serial Monitor', 'Web Server'])
        self.communication_type_dropbox.currentIndexChanged.connect(self.com_type_dropbox_fun)

        self.communication_type_section.addWidget(self.communication_type_label)
        self.communication_type_section.addWidget(self.communication_type_dropbox)

        # ----- Com port section -----
        self.com_section = QHBoxLayout()
        self.main_layout.addLayout(self.com_section, 1, 0)

        self.com_label = QLabel('COM Port:')
        self.com_dropbox = QComboBox()
        self.com_dropbox.addItems([' ', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9'])
        self.com_dropbox.currentIndexChanged.connect(self.com_dropbox_fun)

        self.com_section.addWidget(self.com_label)
        self.com_section.addWidget(self.com_dropbox)
        self.com_label.hide()
        self.com_dropbox.hide()

        # ----- Baud rate section -----
        self.baud_section = QHBoxLayout()
        self.main_layout.addLayout(self.baud_section, 2, 0)

        self.baud_label = QLabel('Baud Rate:')
        self.baud_dropbox = QComboBox()
        self.baud_dropbox.addItems([' ', '300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '74880',
                                    '115200', '230400', '250000', '500000', '1000000', '2000000'])
        self.baud_dropbox.currentIndexChanged.connect(self.baud_dropbox_fun)

        self.baud_section.addWidget(self.baud_label)
        self.baud_section.addWidget(self.baud_dropbox)
        self.baud_label.hide()
        self.baud_dropbox.hide()

        # ----- Start/stop buttons section -----
        self.button_section = QVBoxLayout()
        self.main_layout.addLayout(self.button_section, 4, 0)

        self.start_btn = QPushButton('Start')
        self.start_btn.clicked.connect(self.start_btn_fun)

        self.stop_btn = QPushButton('Stop')
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_btn_fun)

        self.button_section.addWidget(self.start_btn)
        self.button_section.addWidget(self.stop_btn)

        # ----- Graphs section-----
        self.graph_section = QGridLayout()
        self.main_layout.addLayout(self.graph_section, 5, 0, 5, 10)

        self.pen_red = pg.mkPen(color=(255, 0, 0))
        self.pen_green = pg.mkPen(color=(0, 255, 0))
        self.pen_blue = pg.mkPen(color=(0, 0, 255))
        self.graph_1 = pg.PlotWidget()
        self.graph_2 = pg.PlotWidget()
        self.graph_3 = pg.PlotWidget()
        self.graph_4 = pg.PlotWidget()
        self.graph_5 = pg.PlotWidget()
        self.graph_6 = pg.PlotWidget()
        self.graph_section.addWidget(self.graph_1, 0, 0)
        self.graph_section.addWidget(self.graph_2, 0, 1)
        self.graph_section.addWidget(self.graph_3, 0, 2)
        self.graph_section.addWidget(self.graph_4, 1, 0)
        self.graph_section.addWidget(self.graph_5, 1, 1)
        self.graph_section.addWidget(self.graph_6, 1, 2)
        self.plot_1 = self.graph_1.plot(self.time_arr, self.data_arr_1, pen=self.pen_red)
        self.plot_2 = self.graph_2.plot(self.time_arr, self.data_arr_2, pen=self.pen_green)
        self.plot_3 = self.graph_3.plot(self.time_arr, self.data_arr_3, pen=self.pen_blue)
        self.plot_4 = self.graph_4.plot(self.time_arr, self.data_arr_4, pen=self.pen_red)
        self.plot_5 = self.graph_5.plot(self.time_arr, self.data_arr_5, pen=self.pen_green)
        self.plot_6 = self.graph_6.plot(self.time_arr, self.data_arr_6, pen=self.pen_blue)

        # How fast the data updates
        self.timer = QTimer()
        self.timer_time = int(time_interval * 1000)
        self.timer.setInterval(self.timer_time)  # milliseconds

        # How fast the graph updates
        self.plot_timer = QTimer()
        self.plot_timer_time = int(plot_time_interval * 1000)
        self.plot_timer.setInterval(self.plot_timer_time)  # milliseconds

        print(f'Main initialized in {t.perf_counter() - start_time} seconds')

    def stop_messagebox_fun(self):
        stop_messagebox = QMessageBox(self)
        stop_messagebox.setIcon(QMessageBox.Question)
        stop_messagebox.setWindowTitle('Save Data?')
        stop_messagebox.setText('Save recorded data as a csv file?')
        stop_messagebox.setDetailedText(f'Time Array: {self.time_arr}\n'
                                        f'\n'
                                        f'Data Array 1: {self.data_arr_1}\n'
                                        f'\n'
                                        f'Data Array 2: {self.data_arr_2}\n'
                                        f'\n'
                                        f'Data Array 3: {self.data_arr_3}\n'
                                        f'\n'
                                        f'Data Array 4: {self.data_arr_4}\n'
                                        f'\n'
                                        f'Data Array 5: {self.data_arr_5}\n'
                                        f'\n'
                                        f'Data Array 6: {self.data_arr_6}\n'
                                        f'\n')
        stop_messagebox.setStandardButtons(QMessageBox.Save | QMessageBox.Close)
        stop_messagebox.setDefaultButton(QMessageBox.Save)
        button_clicked = stop_messagebox.exec_()
        if button_clicked == QMessageBox.Save:
            self.save_csv_fun()

    def menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Create menus
        file_menu = QMenu('File', self)
        edit_menu = QMenu('Edit', self)
        help_menu = QMenu('Help', self)

        # File sub-menus
        save_menu = QAction('&Save', self)
        save_menu.setShortcut("Ctrl+S")
        save_menu.triggered.connect(self.save_csv_fun)
        file_menu.addAction(save_menu)

        clear_data_menu = QAction('Clear recorded data', self)
        clear_data_menu.triggered.connect(self.clear_data_warning)
        file_menu.addAction(clear_data_menu)

        # Add menus
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(help_menu)

    def start_btn_fun(self):
        if self.com_type == 'Serial Monitor' and not self.serial_thread_start:
            self.serial_com = sc.SerialCommunication(self.com, int(self.baud))
            self.serial_thread_start = True
        if self.com_type == 'Web Server' and not self.web_thread_start:
            self.web_scrap = ws.MPU6050WebScrapper(url)
            self.web_thread_start = True
        self.stop_bool = False
        self.stop_btn.setEnabled(True)
        self.start_btn.setDisabled(True)
        if self.com_type == 'Serial Monitor':
            self.serial_pause_fun()
        if self.com_type == 'Web Server':
            self.web_pause_fun()
        self.plot_timer.start()
        self.timer.start()

    def stop_btn_fun(self):
        self.stop_bool = True
        self.stop_btn.setDisabled(True)
        self.start_btn.setEnabled(True)
        if self.com_type == 'Serial Monitor':
            self.serial_continue_fun()
        if self.com_type == 'Web Server':
            self.web_continue_fun()
        self.stop_messagebox_fun()

    def com_dropbox_fun(self):
        self.com = self.com_dropbox.currentText()

    def baud_dropbox_fun(self):
        self.baud = self.baud_dropbox.currentText()

    def com_type_dropbox_fun(self):
        self.com_type = self.communication_type_dropbox.currentText()
        self.show_hide_serial_widgets()

    def serial_pause_fun(self):
        self.serial_com.pause_bool = False
        self.serial_com.pause_time_arr = np.append(self.serial_com.pause_time_arr, self.serial_com.paused_time)
        self.serial_com.total_time_paused = np.sum(self.serial_com.pause_time_arr)

    def serial_continue_fun(self):
        self.serial_com.pause_bool = True
        self.serial_com.paused_start_time = t.perf_counter()

    def web_pause_fun(self):
        self.web_scrap.pause_bool = False
        self.web_scrap.pause_time_arr = np.append(self.web_scrap.pause_time_arr, self.web_scrap.paused_time)
        self.web_scrap.total_time_paused = np.sum(self.web_scrap.pause_time_arr)

    def web_continue_fun(self):
        self.web_scrap.pause_bool = True
        self.web_scrap.paused_start_time = t.perf_counter()

    def update_serial_data(self):
        if not self.stop_bool and self.com_type == 'Serial Monitor' and self.serial_com.serial_data is not None:
            self.time_arr = np.append(self.time_arr, float(self.serial_com.elapsed_time))
            self.data_arr_1 = np.append(self.data_arr_1, float(self.serial_com.serial_data[0]))
            self.data_arr_2 = np.append(self.data_arr_2, float(self.serial_com.serial_data[1]))
            self.data_arr_3 = np.append(self.data_arr_3, float(self.serial_com.serial_data[2]))
            self.data_arr_4 = np.append(self.data_arr_4, float(self.serial_com.serial_data[3]))
            self.data_arr_5 = np.append(self.data_arr_5, float(self.serial_com.serial_data[4]))
            self.data_arr_6 = np.append(self.data_arr_6, float(self.serial_com.serial_data[5]))
            # print(t.perf_counter())

    def update_web_server_data(self):
        if not self.stop_bool and self.com_type == 'Web Server' and self.web_scrap.web_data is not None:
            self.time_arr = np.append(self.time_arr, float(self.web_scrap.elapsed_time))
            self.data_arr_1 = np.append(self.data_arr_1, float(self.web_scrap.web_data[0]))
            self.data_arr_2 = np.append(self.data_arr_2, float(self.web_scrap.web_data[1]))
            self.data_arr_3 = np.append(self.data_arr_3, float(self.web_scrap.web_data[2]))
            self.data_arr_4 = np.append(self.data_arr_4, float(self.web_scrap.web_data[3]))
            self.data_arr_5 = np.append(self.data_arr_5, float(self.web_scrap.web_data[4]))
            self.data_arr_6 = np.append(self.data_arr_6, float(self.web_scrap.web_data[5]))

    def update_plot(self):
        # Updates graphs on a timer
        self.plot_1.setData(self.time_arr[-1000:], self.data_arr_1[-1000:])
        self.plot_2.setData(self.time_arr[-1000:], self.data_arr_2[-1000:])
        self.plot_3.setData(self.time_arr[-1000:], self.data_arr_3[-1000:])
        self.plot_4.setData(self.time_arr[-1000:], self.data_arr_4[-1000:])
        self.plot_5.setData(self.time_arr[-1000:], self.data_arr_5[-1000:])
        self.plot_6.setData(self.time_arr[-1000:], self.data_arr_6[-1000:])

    def show_hide_serial_widgets(self):
        self.plot_timer.timeout.connect(self.update_plot)
        if self.com_type == 'Serial Monitor':
            self.timer.timeout.connect(self.update_serial_data)
            self.com_label.show()
            self.com_dropbox.show()
            self.baud_label.show()
            self.baud_dropbox.show()
        if self.com_type == 'Web Server':
            self.timer.timeout.connect(self.update_web_server_data)
            self.com_label.hide()
            self.com_dropbox.hide()
            self.baud_label.hide()
            self.baud_dropbox.hide()

    def save_csv_fun(self):
        data = np.array([self.time_arr, self.data_arr_1, self.data_arr_2, self.data_arr_3,
                         self.data_arr_4, self.data_arr_5, self.data_arr_6])
        data_csv = pd.DataFrame(data)
        data_csv = data_csv.T
        data_csv.columns = ['Time (s)', 'Acceleration X (g)', 'Acceleration Y (g)', 'Acceleration Z (g)',
                            'Gyroscope X (deg/s)', 'Gyroscope Y (deg/s)', 'Gyroscope Z (deg/s)']
        filename = QFileDialog.getSaveFileName(self, 'Save File', filter='All Files (.);;CSV (*.csv);;Excel (*.xls);; '
                                                                         'Text (*.txt)')
        if filename[0] == '':
            pass
        else:
            data_csv.to_csv(filename[0], index=False, float_format='%.3f')

    def clear_data(self):
        self.time_arr = np.array([], dtype=float)
        self.data_arr_1 = np.array([], dtype=float)
        self.data_arr_2 = np.array([], dtype=float)
        self.data_arr_3 = np.array([], dtype=float)
        self.data_arr_4 = np.array([], dtype=float)
        self.data_arr_5 = np.array([], dtype=float)
        self.data_arr_6 = np.array([], dtype=float)

    def clear_data_warning(self):
        clear_data_warning_messagebox = QMessageBox(self)
        clear_data_warning_messagebox.setIcon(QMessageBox.Warning)
        clear_data_warning_messagebox.setWindowTitle('Clear data?')
        clear_data_warning_messagebox.setText('Do you want to clear recorded data? ')
        clear_data_warning_messagebox.setDetailedText(f'Time Array: {self.time_arr}\n'
                                                      f'\n'
                                                      f'Data Array 1: {self.data_arr_1}\n'
                                                      f'\n'
                                                      f'Data Array 2: {self.data_arr_2}\n'
                                                      f'\n'
                                                      f'Data Array 3: {self.data_arr_3}\n'
                                                      f'\n'
                                                      f'Data Array 4: {self.data_arr_4}\n'
                                                      f'\n'
                                                      f'Data Array 5: {self.data_arr_5}\n'
                                                      f'\n'
                                                      f'Data Array 6: {self.data_arr_6}\n'
                                                      f'\n')
        clear_data_warning_messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        clear_data_warning_messagebox.setDefaultButton(QMessageBox.Cancel)
        button_clicked = clear_data_warning_messagebox.exec_()
        if button_clicked == QMessageBox.Yes:
            self.clear_data()


if __name__ == '__main__':
    url = 
    time_interval = .104  # Data record rate (s) - should match microcontroller output rate
    plot_time_interval = .1  # Plot update rate (s)
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())

    # Data Acq: .01 second = .015 seconds average (~65.965 data/second)
    #         : .005 second = .011 seconds average (~87.204 data/second)

    # serial read = .09 - .10 second delay (90 - 100 milliseconds) (90000 - 100000 microseconds) (~10-11 data/second)
