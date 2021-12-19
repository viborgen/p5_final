"""
Denne fil anvendes til at hente data fra Vicon-systemet.
"""
#Generelle imports
import socket
import struct as s
import time

#Angivet IP og port i Vicon systemet angives
UDP_IP = "0.0.0.0" #læser alle IP addresser
UDP_PORT = 4800   # sætter port nr. 

#UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

#Dataen modtages og sorteres for at kunne returneres som XYZ-koordianter og rotationer.
def getData():
    data, addr = sock.recvfrom(4096) #henter data med en bite rate på 4096 bit/s
    posXYZ = []
    for k in range(3): posXYZ.append(s.unpack_from('d', data, 32+k*8)[0]) #Udpakker data struct og henter posisitons data  
    rot = []
    for j in range(3): rot.append(s.unpack_from('d', data, 56+j*8)[0])  #Udpakker data struct og henter rotations data

    return posXYZ, rot