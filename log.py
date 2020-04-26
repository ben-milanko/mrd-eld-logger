import argparse
import serial
import serial.rs485
import serial.tools
import time
import binascii
import datetime

prepend = bytearray(b'\x01')
append = bytearray(b'\x03\x04')
bus_mode_list = ['DC','AC']

ser = serial.Serial()

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--port', default='/dev/ttyUSB0', type=str,
                help='Manually set port')
parser.add_argument('--noterminal', action='store_true',
                help='Flag to stop terminal output')
parser.add_argument('--nolog', action='store_true',
                help='Flag to stop logging to file')
parser.add_argument('--file', type=str, 
                help='File to log queries to, default is current "date_time.csv"')
parser.add_argument('--id', default='01', type=str, 
                help='ID of ELD to address')
parser.add_argument('--poll', default=5, type=float, 
                help='Polls the ELD every n seconds')
args = parser.parse_args()


def eldEncode(message):

    try:
        sendEncode = bytearray(message.encode())

        sendEncode = prepend + sendEncode

        sendSum = sum(sendEncode)
        sendChecksumBytes = bytearray(sendSum.to_bytes(5,'big'))
        sendChecksum = sendChecksumBytes[-1].to_bytes(1,'big')

        sendEncode = sendEncode + sendChecksum + append

        return sendEncode

    except:
        print('Encoding error')
        return 0
    

def eldDecode(receive_hex):
    try:
        receive_hex = receive_hex[0:-2]
        receiveChecksum = receive_hex[-1].to_bytes(1,'big')
        receive_hex = receive_hex[0:-1]

        receiveSum = sum(receive_hex)
        receiveChecksumBytes = bytearray(receiveSum.to_bytes(5,'big'))
        testReceiveChecksum = receiveChecksumBytes[-1].to_bytes(1,'big')

        receive_hex = receive_hex[1:].decode()

        if receiveChecksum == testReceiveChecksum:
            return receive_hex
        else:
            return 1

    except:
        print('Decoding error')
        return 0

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

def poll(commands):
    global args
    results = []
    for i in range(len(commands)):
        results.append(query(args.id+commands[i])[2:])
    
    return results

def pollFake(commands):
    results = ['0','0','0','1000']
    return results

def query(message):

    ser.write(eldEncode(message))
    response = ''
    c = 0
    while response == False:
        time.sleep(0.1)
        read = ser.read()
        if len(read) != 0:
            response = eldDecode(read)
        if c == 10:
            response = 'timeout'
            break
        c += 1

    return response

def initFile(fileName):
    print('\n')
    try:
        f = open(fileName)
        fileSet = False
        while not fileSet:
            overwrite = input(f'File "{fileName}" already exists, would you like to overwrite it? (Y/n):')
            if (overwrite == 'Y'):
                f = open(fileName,'w')
                f.write('')
                f.close()
                fileSet = True
            elif (overwrite == 'n'):
                fileName = input('Enter new filename: ')
                fileSet = True

    except IOError:
        f = open(fileName,'w')
        print(f'Log file "{fileName}" created')
    finally:
        f.close()

    return fileName

def saveData(fileName, array):
    f = open(fileName,'a')
    f.write('\n'+','.join(array))
    f.close()

def main():
    global args
    initSerial(args)
    global ser
    ser.open()

    if not args.noterminal:
        print(f'Querying ELD of ID:\t\t{args.id}')

    software_version = query(args.id+'SW?')[2:]
    print(f'ELD software version is:\t\t{software_version}')

    trip_point = query(args.id+'TP')[2:]
    print(f'ELD trip point is:\t\t{trip_point} kOhm')

    time_delay = query(args.id+'TD')[2:]
    print(f'ELD time delay is:\t\t{time_delay} seconds')

    bus_mode = int(query(args.id+'BM')[2:])
    print(f'ELD is operating in:\t\t{bus_mode_list[bus_mode]} mode')
    if bus_mode:
        header = ['Bus Leakage Status','AC Fault Time','AC Fault Level','Resistor Leakage']
        commands = ['BL','ACFT','ACFL','RLE']
    else:
        header = ['Bus Leakage Status','DC Fault Time Bus1','DC Fault Time Bus2','DC Fault Level Bus1','DC Fault Level Bus2','DC Voltage','Resistor Leakage']
        commands = ['BL','DCFT1','DCFT2','DCFL1','DCFL2','V','RLE']

    header = ['Date','Time'] + header


    if not args.nolog:
        if args.file:
            file = args.file
        else:
            now = datetime.datetime.now()
            file = now.strftime("Logfile_%Y-%m-%d_%H:%M:%S.csv")
        logFile = initFile(file)

    if not args.noterminal:
        print('\nBEGIN POLL\n')
        printHeader = [e+'        ' for e in header]
        widthPrintHeader = [len(e) for e in printHeader]
        print(''.join(printHeader))

    if not args.nolog:
        saveData(logFile,header)

    while True:
        now = datetime.datetime.now()

        results = poll(commands)
        #results = pollFake(commands) #Demonstrates the output
        results = [now.strftime('%Y-%m-%d'),now.strftime('%H:%M:%S')] + results

        if not args.nolog:
            saveData(logFile,results)

        if not args.noterminal:
            for i in range(len(results)):
                results[i] = results[i].ljust(widthPrintHeader[i])
            print(''.join(results))

        time.sleep(args.poll)

if __name__ == "__main__":
    main()