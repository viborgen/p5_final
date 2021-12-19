#Control variabler angives
k_p = 1
k_i = 0.1
k_d =0.5

#Sampling hastighed angives
f=30
T = 1/f

#KE vrædier udregnes
KE_k = (k_p+k_i*T+k_d/T)
KE_k1 = (-k_p-2*k_d/T)
KE_k2 = k_d/T

#PID-controller implementation
def PID(r,y, EK1,EK2, thrustK1):
    EK = r - y
    thrust = EK*KE_k+EK1*KE_k1+EK2*KE_k2 + thrustK1
    thrustK1 = thrust
    EK2 = EK1
    EK1 = EK
    #print(EK,EK1,EK2,thrust)
    return thrust, EK1, EK2, thrustK1


