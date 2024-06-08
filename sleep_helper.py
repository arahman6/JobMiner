import random
import time

class SleepHelper:
    @staticmethod
    def random_sleep(mean, sd):
        sleep_time = random.gauss(mean, sd)
        print('sleep time:', sleep_time)
        # Ensure that sleep time is non-negative
        if sleep_time < 0:
            sleep_time = 0
        time.sleep(sleep_time)

# from sleep_helper import SleepHelper
# SleepHelper.random_sleep(20, 2)