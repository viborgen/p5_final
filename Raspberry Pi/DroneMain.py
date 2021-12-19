#Generelle imports
import threading
import time


#Imports til fra CrazyFlie - TJEK OP! Ikke alt bruges længere
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

#.py filer importeres
import Vicon_stream
import XYPID
import ZPID

#Der oprettes forbindelse til dronen
uri = uri_helper.uri_from_env(default='radio://0/44/2M/E7E7E7E7E7')

#anvendes til at bevæge dronen i XYZ
def LatestPoints():
    if XYZ[3] == 1:
        time.sleep(0.00000000000000000000000000000001)
    else:
        # XYZ.clear()
        XYZ[3] = 1
        x = 0
        return x

XYZ = [0, 0, 0, 1]

#Modtager koordianter fra terminalen
def GetPoint():
    global XYZ
    XYZ = list(map(float, input('\nindsæt koordinater:').strip().split()))[:4]
    XYZ[3] = 0
    return XYZ


def SendPoint(scf):
    cf = scf.cf
    # skal være her for at unlocke setpoint
    cf.commander.send_setpoint(0, 0, 0, 0)
    EK2 = 0
    EK1 = 0
    thrustk1 = 0
    RK1 = 0
    RK2 = 0
    rollK1 = 0
    PK1 = 0
    PK2 = 0
    pitchK1 = 0
    pos = []
    x = 0
    ref = []
    yaw = 0



    while(True):
        if x == 0:
            ref = threading.Thread(target=GetPoint).start()
            x = x+1
        x = LatestPoints()
        pos, rot = Vicon_stream.getData()
        #print(pos)
        # yaw = 0-rot[2] #tester yaw
        thrust, EK1, EK2, thrustk1 = ZPID.PID(
            XYZ[2], pos[2]/1000, EK1, EK2, thrustk1)  # Det her virker
        roll, RK1, RK2, rollK1 = XYPID.PID(
            XYZ[0], pos[0]/1000, RK1, RK2, rollK1)  # Det her virker
        pitch, PK1, PK2, pitchK1 = XYPID.PID(
            XYZ[1], pos[1]/1000, PK1, PK2, pitchK1)  # Det her virker
        
        # omdanner thrust til PWM sigal
        pwm = (4355.400697+1.161*10**6*(thrust)/9.82)
        if pwm > 50000:
            pwm = 50000
        if pwm < 0:
            pwm = 0
    
        print("roll: ",roll)
        print("pitch ", pitch)
        cf.commander.send_setpoint(roll,pitch,yaw,abs(round(pwm))) #Sender PWM til dronen
        #cf.commander.send_setpoint(0, 0, 0, abs(round(pwm)))


if __name__ == '__main__':
    cflib.crtp.init_drivers() #crazyflie drivere initialiseres
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf: #Der connectes til angivne Crazyflie
        SendPoint(scf) #Kalder funktion der modtager punkt dronen skal flyve til