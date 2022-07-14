import time as t
start_time = t.perf_counter()
import threading as th
from selenium import webdriver  # manually install "selenium"
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # manually install "webdriver-manager"
from selenium.webdriver.common.by import By
import numpy as np
print(f'Web imports loaded in {t.perf_counter() - start_time} seconds')

class MPU6050WebScrapper(th.Thread):
    def __init__(self, url):
        super().__init__()

        # Initialize
        self.url = url
        self.web_data = None
        self.thread = None
        self.chromedriver = None
        self.start_time = 0
        self.start_time_bool = False
        self.current_time = None
        self.elapsed_time = None

        self.pause_bool = False
        self.paused_time = 0
        self.paused_start_time = 0
        self.pause_time_arr = np.array([], dtype=float)
        self.total_time_paused = 0

        self.thread_web_scrap()
        t.sleep(5)
        print(f'Web initialization + sleep ended after {t.perf_counter() - start_time} seconds')

    def web_scrap(self):
        while True:
            accX = self.chromedriver.find_element(By.ID, 'aX').text
            accY = self.chromedriver.find_element(By.ID, 'aY').text
            accZ = self.chromedriver.find_element(By.ID, 'aZ').text
            gyroX = self.chromedriver.find_element(By.ID, 'gX').text
            gyroY = self.chromedriver.find_element(By.ID, 'gY').text
            gyroZ = self.chromedriver.find_element(By.ID, 'gZ').text
            self.web_data = [accX, accY, accZ, gyroX, gyroY, gyroZ]
            if self.pause_bool:
                self.pause_fun()
            self.current_time = t.perf_counter()
            self.elapsed_time = (self.current_time - self.start_time) - self.total_time_paused

    def thread_web_scrap(self):
        self.chromedriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # Chrome browser for python to use
        self.chromedriver.minimize_window()  # Minimizes browser to screen
        self.chromedriver.get(self.url)  # Opens url in browser

        self.chrome_options = Options()
        self.chrome_options.add_argument("--incognito")  # Incognito mode

        self.thread = th.Thread(target=self.web_scrap)
        self.start_time = t.perf_counter()
        self.thread.start()

    def pause_fun(self):
        current = t.perf_counter()
        self.paused_time = current - self.paused_start_time
