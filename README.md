# mrd-eld-logger
Queries and logs information for MRD - Earth Leakage Devices using RS-485 serial to USB interface

[This converter](https://www.jaycar.com.au/usb-port-to-rs-485-422-converter-with-automatic-detect-serial-signal-rate/p/XC4136) was used but any RS-485 to USB converter should work.

As this converter is full duplex and the ELD operates on half duplex the connection should be wired as below, with additional ELDs daisy chained rather star connected. If the connection is over a longer distance consider using twisted pair cable.

!(https://github.com/bpmil3/mrd-eld-logger/raw/master/RS485HalfDuplex.JPG)

## Quick Start
Create a python 3 virtual environment

`python3 -m venv mrd-eld`

Activate the virtual environment

`source mrd-eld/bin/activate`

Install required packages

`pip3 install requirements.txt`

Make sure serial folder is owned by user
`sudo chmod 666 /dev/ttyUSB0`

Run logger

`python3 log.py`

By default logs are stored to Log{current timestamp}.log
