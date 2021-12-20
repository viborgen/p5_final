"""Denne fil anvendes til at logge roll, pitch og yaw værdier til videre brug i pitch_roll_test.py"""
#Generelle Crazyflie imports
import logging
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

#Opsætning af log
logging.basicConfig(level=logging.ERROR)

#Logging opsættes, som også set på https://github.com/bitcraze/crazyflie-lib-python under logging examples.
class LoggerClass():
    def __init__(self):
        self.lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
        self.lg_stab.add_variable('stabilizer.roll', 'float')
        self.lg_stab.add_variable('stabilizer.pitch', 'float')
        self.lg_stab.add_variable('stabilizer.yaw', 'float')
        self.TimeStampBuffer = None
        self.DataBuffer = None
        self.logconfBuffer = None
        self.DataStreamIsActive = False
        

    def log_stab_callback(self, timestamp, data, logconf):
        self.DataStreamIsActive = True
        self.TimeStampBuffer = timestamp
        self.DataBuffer = data
        self.logconfBuffer = logconf

    def logValAsync(self, scf, logconf):
        cf = scf.cf
        cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(self.log_stab_callback)
        logconf.start()

    def getData(self):
        return self.TimeStampBuffer, self.DataBuffer, self.logconfBuffer