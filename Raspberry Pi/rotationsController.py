#parametere for roll 
#Inner loop Parametere
kv = 14.27
#Outer loop Parametere
kp = 8.3
ki = 2.4 
T = 1/50


def RollcontrollerInnerLoop(r,y): #Roll regulator indresløjfe
    e = r-y
    u = kv*e
    return u
def RollcontrollerOuterLoop(r,y,em1,um1): #Roll regulator ydresløjfe
    e = r-y
    u = kp*e-kp*em1+ki*em1*T+um1
    em1 = e
    um1 = u
    return u, em1, um1


#Pararmetre for pitch
#Inner loop Parametere
kv_p = 14.27

#Outer loop Parametere
kp_p = 9.2
ki_p = 2.5


def PitchcontrollerInnerLoop(r,y): #Pitch regulator indresløjfe
    e = r-y
    u = kv_p*e
    return u


def PitchcontrollerOuterLoop(r,y,em1,um1): #Pitch regulator ydresløjfe
    e = r-y
    u = kp_p*e-kp_p*em1+ki_p*em1*T+um1
    em1 = e
    um1 = u
    return u, em1, um1