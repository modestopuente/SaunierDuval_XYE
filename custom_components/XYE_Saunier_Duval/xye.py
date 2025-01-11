#-------------------------------------------------------------------------------
# Name:        xye
# Purpose:
#
# Author:      mpuenten
#
# Created:     15/11/2021
# Copyright:   (c) mpuenten 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from time import sleep
from binascii import hexlify
import socket, select
import select
from .const import xye_const,xye_cmd, xye_mode, xye_fan_speed, mode_flag, oper_flag


class xye:

    def __init__(self,ip,port,device,source):
        self.ip = ip
        self.port = port
        self.device = device
        self.source = source
        self.sock = None

    def conecta(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))

    def desconecta(self):
        try:
            self.sock.shutdown(1)
            sleep(2)
            self.sock.close()
            sleep(2)
            return True
        except:
            return False

    def send(self,_payload,command):
        CRC = 0x00
        sum = 0

        CHECK = 0xFF - command # command Check
        C = [  xye_const.PREAMBLE, command , self.device , self.source, xye_const.FROMMASTER , self.source, CHECK , CRC, xye_const.PROLOGUE  ]
        C[6:6] = _payload
        for byte in C:
            sum += int(byte)
        C[14] =  0xFF - (sum % 0x100)   #Checksum
        Chex=b''
        for entero in C:
            Chex = Chex + entero.to_bytes(1,'little')
        i=0
        while i<3:
            i+=1
            try:
                self.sock.sendall(Chex)
                ready = select.select([self.sock], [], [], 1)
                sleep(0.2)
                if self.sock in ready[0]:
                    s=self.sock.recv(1024)
                    #if validate_response(s):
                    return s
            except:
                return False
        return False

    def validate_response(r):
        if len(r)==33 and r[1]==xye_const.PREAMBLE and r[32]==xye_const.PROLOGUE:
            chk=r[14]
            for byte in r:
                sum += int(byte)
            if (sum-chk)==chk:
                return True
        return False


        C = [  xye_const.PREAMBLE, command , self.device , self.source, xye_const.FROMMASTER , self.source, CHECK , CRC, xye_const.PROLOGUE  ]


    def query_device(self):
        return xye.send(self,xye_const.PAYLOAD,xye_cmd.QUERY)

    def lock_device(self):
        return xye.send(self,xye_const.PAYLOAD,xye_cmd.LOCK)

    def unlock_device(self):
        return xye.send(self,xye_const.PAYLOAD,xye_cmd.UNLOCK)

    def set_mode(self,Payload,mode):
        Payload[0] = mode
        '''
        if mode == xye_mode.FAN :
            Payload[2] = 0xff
        '''
        return xye.send(self,Payload,xye_cmd.SET)

    def set_fanspeed(self,Payload,fanspeed):
        Payload[1] = fanspeed
        return xye.send(self,Payload,xye_cmd.SET)

    def set_temp(self,Payload,temp):
        Payload[2] = temp
        return xye.send(self,Payload,xye_cmd.SET)

    def set_modeflags(self,Payload,modeflag):
        Payload[5] = modeflag
        return xye.send(self,Payload,xye_cmd.SET)

    def set_hvac_mode(self,Payload,mode):
        xyemode = xye_mode.AUTO
        if mode == 'heat':
            xyemode = xye_mode.HEAT
        if mode == 'cool':
            xyemode = xye_mode.COOL
        if mode == 'fan_only':
            xyemode = xye_mode.FAN
        if mode == 'off':
            xyemode = xye_mode.OFF

        return xye.set_mode(self,Payload,xyemode)

    def set_fan_mode(self,Payload,fanspeed):
        xyefanspeed = xye_fan_speed.AUTO
        if fanspeed == 'low':
            xyefanspeed = xye_fan_speed.LOW
        if fanspeed == 'medium':
            xyefanspeed = xye_fan_speed.MEDIUM
        if fanspeed == 'high':
            xyefanspeed = xye_fan_speed.HIGH
        if fanspeed == 'off':
            xyefanspeed = xye_fan_speed.OFF

        return xye.set_fanspeed(self,Payload,xyefanspeed)

    def set_target_temp(self,Payload,temp):
        return xye.set_temp(self,Payload,int(temp))

    def set_swing_mode(self,Payload,swingmode):
        xyeswingmode= mode_flag.SWING
        if swingmode == 'off':
            xyeswingmode = mode_flag.NORM
        return xye.set_modeflags(self,Payload,xyeswingmode)


'''
class XYEsocket:

    def __init__(self,ip,port,send_buffer):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ip
        self.port = port
        self.send_buffer=send_buffer

    def connect(self):
        self.sock.connect((self.host,self.port))

    def disconnect(self):
        try:
            self.sock.shutdown(1)
            self.sock.close()
            return True
        except:
            return False

    def send(self):
        try:
            sent = self.sock.sendall(self.send_buffer)
        except socket.error:
            print('socket connection broken')

    def receive(self):
        while True:
            ready = select.select([self.sock], [], [], 1)
        if self.sock in ready[0]:
            return self.sock.recv(1024)
        else:
            return False
'''