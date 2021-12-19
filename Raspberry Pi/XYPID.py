"""
Denne fil anvendes til XY-controlleren
"""
#Control variabler angives
k_p = 4
k_d = 4
k_i = 0.4

#Sampling hastighed angives
f=100
T = 1/f 

#kE værdier udregnes
KE_k = (k_p+k_i*T+k_d/T)
KE_k1 = (-k_p-2*k_d/T)
KE_k2 = k_d/T

#PID-controller implementation
def PID(r,y, EK1,EK2, angleK1):
    EK = r - y #Finder nuværende fejl
    angle = EK*KE_k+EK1*KE_k1+EK2*KE_k2 + angleK1 #beregner nyt output
    angleK1 = angle #nuværende output gemmes : U(k-1) = U(k)
    EK2 = EK1 #gammel fejl gemmes igen : E(k-2) = E(k-1)
    EK1 = EK #nuværende fejl gemmes : E(k-1) = E(k)
    return angle, EK1, EK2, angleK1