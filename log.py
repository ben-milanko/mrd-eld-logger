import argparse
import serial
import serial.rs485
import serial.tools
import time
import binascii

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--port', default='/dev/ttyUSB0', type=str,
                help='Manually set port')
parser.add_argument('--noterminal', action='store_true',
                help='Flag to output to terminal')
parser.add_argument('--log', action='store_true',
                help='Flag to start logging to file')
parser.add_argument('--file', default='log.txt', type=str, 
                help='File to log queries to')
parser.add_argument('--id', default=1, type=int, 
                help='ID of ELD to address')
parser.add_argument('--poll', default=1, type=float, 
                help='Polls the ELD every n seconds')
args = parser.parse_args()

ser = serial.Serial()
#command = {'id_query':'D','edit_id':'EDID ','trip_point':'TP','bus_mode':'BM',''}
class bus_mode:
    command = 'BM'
    def response(val):
        global args
        rKey = ['DC','AC']
        if args.noterminal:
            print(f'The ELD bus operating mode is {rKey[val]}')
        return rKey[val]

class id_query:
    command = 'D'
    def response(val):
        if args.noterminal:
            print(f'The ELD ID is {val}')
        return val
# def encode(message):
    
#     return 

# def decode(message):
#     return

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
    global args
    print(args.noterminal)
    id_query.response(0)
    bus_mode.response(0)
    
    x = b'\0100V2.0'
    x = binascii.hexlify(x)
    y = str(x,'ascii')
    print(ord('\a'))
    print(binascii.a2b_uu('H'))
    x = binascii.hexlify(b'\x01\x30\x30\x56\x32\x2E\x30')
    x2 = binascii.hexlify(b'\x0100V2.0')
    print(x==x2)
    y = binascii.unhexlify(x)
    print(x) # Outputs b'74657374' (hex encoding of "test")
    print(y) # Outputs 74657374
    c=y.decode('utf-8')
    print(c)
    print(c.encode('ascii'))
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