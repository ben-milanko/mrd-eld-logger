import argparse
import serial
import serial.rs485
import serial.tools
import time
import binascii

ser = serial.Serial()

def encode(message):
    
    return 

def decode(message):

def initArgs():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', default='/dev/ttyUSB0', type=str,
                    help='Manually set port')
    parser.add_argument('--log', action='store_true',
                    help='Flag to start logging to file')
    parser.add_argument('--file', default='log.txt', type=str, 
                    help='File to log queries to')
    return parser.parse_args()

def initSerial(args):
    global ser
    ser.baudrate = 9600
    ser.port = args.port
    #ser.port = 'COM7'
    #ser.timeout =0
    ser.stopbits = serial.STOPBITS_ONE
    ser.bytesize = 8
    ser.parity = serial.PARITY_NONE
    ser.rtscts = 0



def main():
    args = initArgs()
    print(args.log)
    # initSerial(args)
    # global ser
    # ser.open()
    # while True:
    #     mHex = ser.read()
    #     if len(mHex)!= 0:
    #         print("get",binascii.hexlify(bytearray(mHex)))
    #     time.sleep(0.1)


if __name__ == "__main__":
    main()