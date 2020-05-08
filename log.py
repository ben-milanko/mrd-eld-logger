import argparse
import serial
import serial.rs485
import serial.tools
import time
import binascii
import datetime
import sys

prepend = bytearray(b'\x01')
append = bytearray(b'\x03\x04')
bus_mode_list = ['DC','AC']

ser = serial.Serial()

parser = argparse.ArgumentParser(description='Communicate with MRD - Earth Leakage Device.')
parser.add_argument('--port', default='/dev/ttyUSB0', type=str,
                help='Manually set port, default is /dev/ttyUSB0')
parser.add_argument('--noterminal', action='store_true',
                help='Flag to stop terminal output')
parser.add_argument('--nolog', action='store_true',
                help='Flag to stop logging to file')
parser.add_argument('--file', type=str, 
                help='File to log queries to, default is current "date_time.csv"')
parser.add_argument('--id', default='01', type=str, 
                help='ID(s) of ELD to address default is 01. Comma seperate for multiple ELDs e.g. 01,02')
parser.add_argument('--poll', default=1, type=float, 
                help='Polls the ELD every n seconds, default is 1')
parser.add_argument('--edit_id', type=str, 
                help='Changes the ID of the ELD currently connected must be between 1 and 98 inclusive. Only use while connected to single ELD. Exits after completion.')
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
            print('Checksum error')
            return 1

    except:
        print('Decoding error')
        return 0

def initSerial(args):
    global ser
    ser.baudrate = 9600
    ser.port = args.port
    #ser.port = 'COM7'
    #ser.timeout =0.1
    ser.stopbits = serial.STOPBITS_ONE
    ser.bytesize = serial.EIGHTBITS
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

    m = eldEncode(message)
    # print(m)
    ser.write(m)
    response = ''
    c = 0

    while response == '':
        time.sleep(0.1)
        read = ser.read_until(append)
        # print(read)
        if len(read) != 0:

            response = eldDecode(read)
            break
        if c == 10:
            response = '  timeout'
            break
        c += 1
       
    print(f'Response: {response}')
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

def editID(oldID,newID):

    response = query(oldID+'EDID '+str(int(newID)))

    if response == '00':
        return 1
    else:
        return 0

def main():
    global args
    global ser
    initSerial(args)
    ser.open()

    if args.edit_id:
        success = editID('01',args.edit_id)
        if success:
            print('ID successfully changed')
        else:
            print('Error ID not changed')
        sys.exit()


    ids = args.id.split(',')

    numELD = len(ids)

    header = ['']*numELD
    commands = ['']*numELD

    for i in range(numELD):
        if not args.noterminal:
            print(f'Querying ELD of ID:\t\t{ids[i]}')

            software_version = query(ids[i]+'SW?')[2:]
            print(f'ELD software version is:\t\t{software_version}')

            trip_point = query(ids[i]+'TP')[2:]
            print(f'ELD trip point is:\t\t{trip_point} kOhm')

            time_delay = query(ids[i]+'TD')[2:]
            print(f'ELD time delay is:\t\t{time_delay} seconds')


        bus_mode = int(query(ids[i]+'BM')[2:])
        if not args.noterminal:
            print(f'ELD is operating in:\t\t{bus_mode_list[bus_mode]} mode')
        
        if bus_mode:
            header[i] = ['Bus Leakage Status','AC Fault Time','AC Fault Level','Resistor Leakage']
            commands[i] = ['BL','ACFT','ACFL','RLE']
        else:
            header[i] = ['Bus Leakage Status','DC Fault Time Bus1','DC Fault Time Bus2','DC Fault Level Bus1','DC Fault Level Bus2','DC Voltage','Resistor Leakage']
            commands[i] = ['BL','DCFT1','DCFT2','DCFL1','DCFL2','V','RLE']

        header[i] = ['ELD ID','Date','Time'] + header

    if not args.nolog:
        if args.file:
            file = args.file
        else:
            now = datetime.datetime.now()
            file = now.strftime("Logfile_%Y-%m-%d_%H:%M:%S.csv")
        logFile = initFile(file)

    if not args.noterminal:
        print(f'\nBEGIN POLL, polling every {args.poll} seconds\n')
        printHeader = [e+'        ' for e in header]
        widthPrintHeader = [len(e) for e in printHeader]
        print(''.join(printHeader))

    if not args.nolog:
        saveData(logFile,header)

    while True:

        for i in range(numELD):
            now = datetime.datetime.now()

            results = poll(commands[i])
            #results = pollFake(commands) #Demonstrates the output
            results = [ids[i],now.strftime('%Y-%m-%d'),now.strftime('%H:%M:%S')] + results

            if not args.nolog:
                saveData(logFile,results)

            if not args.noterminal:
                for i in range(len(results)):
                    results[i] = results[i].ljust(widthPrintHeader[i])
                print(''.join(results))
            
            #time.sleep(0.5) #Might be required?

        time.sleep(args.poll)

if __name__ == "__main__":
    main()
