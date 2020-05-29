# mrd-eld-logger
Queries and logs information for MRD - Earth Leakage Devices using RS-485 serial to USB interface

[This converter](https://www.jaycar.com.au/usb-port-to-rs-485-422-converter-with-automatic-detect-serial-signal-rate/p/XC4136) was used but any RS-485 to USB converter should work.

As this converter is full duplex and the ELD operates on half duplex the connection should be wired as below, with additional ELDs daisy chained rather star connected. If the connection is over a longer distance consider using twisted pair cable.

![ELD Wiring Diagram](https://github.com/bpmil3/mrd-eld-logger/blob/master/ELD%20Wiring.png)

## Quick Start

If everything has previously been set up, simply connect the ELD and run
`python3 log.py`

## Installation
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

By default logs are stored to Log{current timestamp}.csv

## Options
```
usage: log.py [-h] [--port PORT] [--noterminal] [--nolog] [--file FILE]
              [--id ID] [--poll POLL] [--edit_id EDIT_ID]

Communicate with MRD - Earth Leakage Device.

optional arguments:
  -h, --help         show this help message and exit
  --port PORT        Manually set port, default is /dev/ttyUSB0
  --noterminal       Flag to stop terminal output
  --nolog            Flag to stop logging to file
  --file FILE        File to log queries to, default is current
                     "date_time.csv"
  --id ID            ID(s) of ELD to address default is 01. Comma seperate
                     for multiple ELDs e.g. 01,02
  --poll POLL        Polls the ELD every n seconds, default is 1
  --edit_id EDIT_ID  Changes the ID of the ELD currently connected must be
                     between 1 and 98 inclusive. Only use while connected to
                     single ELD. Exits after completion.
```
## Additional Information

The main library used for serial communcations in this implementation is `pyserial`. More information can be found [here](https://pyserial.readthedocs.io/en/latest/pyserial_api.html)
