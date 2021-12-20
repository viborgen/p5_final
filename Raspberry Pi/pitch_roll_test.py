
#Generelle imports
import logging
import time

#Crazyflie Imports
from cflib import crazyflie
from cflib.crazyflie import commander
from cflib.crazyflie import param
from cflib.crazyflie.commander import Commander
from cflib.crazyflie.log import Log
from cflib.crazyflie.param import Param
from cflib.crtp import crtpstack
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper

#Imports fra andre .py filerr
import rotationsController
import cflib.crtp
from Logger import LoggerClass

#Hvilken drone der skal connectes til
uri = uri_helper.uri_from_env(default='radio://0/30/2M/E7E7E7E7E7')

#Opsætning af logging
logging.basicConfig(level=logging.ERROR)

#Sender paramentre til drone
def ParamWrite(groupstr, namestr, Value):
    cf = scf.cf
    fullname = groupstr+"."+namestr
    cf.param.set_value(fullname, Value)
    time.sleep(10**(-6))

#Motor mixing algorithm
def MotorMixing(PWMThrust, PWMRoll, PWMPitch, PWMYaw):
    m4 = PWMThrust + PWMYaw + PWMPitch + PWMRoll
    m1 = PWMThrust - PWMYaw + PWMPitch - PWMRoll
    m3 = PWMThrust - PWMYaw - PWMPitch + PWMRoll
    m2 = PWMThrust + PWMYaw - PWMPitch - PWMRoll
    #Sætter limits så der aldrig overskrides max og min PWM
    if m4 > 65535: 
        m4 = 65535
    elif m4 < 0:
        m4 = 0

    if m1 > 65535:
        m1 = 65535
    elif m1 < 0:
        m1 = 0

    if m2 > 65535:
        m2 = 65535
    elif m2 < 0:
        m2 = 0

    if m3 > 65535:
        m3 = 65535
    elif m3 < 0:
        m3 = 0

    #PWM værdier sendes til motorer
    ParamWrite("motorPowerSet", "m1", round(m1))  # motor 1
    ParamWrite("motorPowerSet", "m3", round(m3))  # motor 3
    ParamWrite("motorPowerSet", "m2", round(m2))  # motor 2
    ParamWrite("motorPowerSet", "m4", round(m4))  # motor 4

#Main funktion
if __name__ == '__main__':
    #Initiere crarzyflie drivere
    cflib.crtp.init_drivers()
    #Opretter logg
    log = LoggerClass()
    #Connecter til crazyflie
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        connectionState = 0
        
        # bruges til at vente på at dronnen er kalibreret og kan modtage beskeder fra radioen
        while(connectionState != "1"):
            ParamWrite("motorPowerSet", "enable", 1) #Enabler muligheden for at kontrollere motorer
            connectionState = scf.cf.param.get_value("motorPowerSet.enable") #dobbelttjekker at motorerne er enabled.
            print(connectionState) #Så der kan følges med i om der er connectin eller ej
        log.logValAsync(scf, log.lg_stab) #logger
        
        #Pararmetre holder modtagne fejl fra forrige sample
        em1roll = 0
        em2roll = 0
        um1roll = 0

        em1pitch = 0
        em2pitch = 0
        um1pitch = 0

        Omegaroll = 0
        Omegapitch = 0


        PWM_bar = 46000 #Generel thrust omdrejningspunkt
        #Anvendes til at bestemme rotationshastighed
        stab_pitch_prev= 0
        stab_roll_prev = 0

        while True:
            if log.DataStreamIsActive: #Undersøger om der kommer data fra log
                DroneData = log.getData()[1]   #Henter logging data fra Logger.py      

                stab_pitch = DroneData["stabilizer.pitch"]
                gyro_y = (stab_pitch-stab_pitch_prev)/(1/50) #Vinkelhastighed udregnes
                stab_pitch_prev = stab_pitch  #Gemmes nuværende vinkel til næste kørsel
                
                stab_roll = DroneData["stabilizer.roll"]
                gyro_x = (stab_roll - stab_roll_prev)/(1/50)
                stab_roll_prev = stab_roll
                
                Omegapitch, em1pitch, um1pitch = rotationsController.PitchcontrollerOuterLoop(0, stab_pitch,em1pitch,um1pitch) #Regner ydre sløjfe for ønsket vinkelhastighed
                PWMdiffpitch=rotationsController.PitchcontrollerInnerLoop(Omegapitch, gyro_y) #bruger ønsket vinkelhastighed til at beregne PWM signal, således den ønskede vinkel holdes
                
                Omegaroll, em1roll, um1roll = rotationsController.RollcontrollerOuterLoop(0, stab_roll,em1roll,um1roll)
                PWMdiffroll=rotationsController.RollcontrollerInnerLoop(Omegaroll, gyro_x)

                #Begrænser output således den stadig kan flyve
                if PWMdiffroll > 10000:
                    PWMdiffroll = 10000
                elif PWMdiffroll < -10000:
                    PWMdiffroll = -10000
                
                if PWMdiffpitch > 10000:
                    PWMdiffpitch = 10000
                elif PWMdiffpitch < -10000:
                    PWMdiffpitch = -10000

                MotorMixing(PWM_bar, PWMdiffroll,PWMdiffpitch, 0) #Motormixing anvendes

                time.sleep(0.2) #holder kontrollykkehastighed
                
                """Mulighed for at gemme data i CSV fil
                with open('gemtData.txt','a') as gemFil:
                    gemFil.write('Pitch: ')
                    gemFil.write(str(DroneData["stabilizer.pitch"]))
                    gemFil.write('\n')"""