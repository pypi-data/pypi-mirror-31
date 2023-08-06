# Purpose
ABB, amongst other things, supply weather stations for Solar plants. The purpose of this project is to collect data from ABB VSN800 Weather stations and send the data to your cloud using Ardexa. Data from ABB weather stations is read using an Ethernet connection using Modbus RTU (over Ethernet) and a Linux device such as a Raspberry Pi, or an X86 intel powered computer. 

## How does it work
This application is written in Python. This application will query 1 or more connected stations at regular intervals. Data will be written to log files on disk in a directory specified by the user. Usage and command line parameters are shown below. This application currently reads from the ABB VSN800-12 Weather Stations. See https://library.e.abb.com/public/62ef065e9c9b450c8ab1a2a109216b0c/VSN800%20WEATHER%20STATION_BCD.00392_EN_RevG.pdf. According to this documnent, the "... VSN800-12 includes a basic sensor set: ambient temperature, solar irradiance, and back of module temperature ..."

## Install
On a raspberry Pi, or other Linux machines (arm, intel, mips or whetever), make sure Python is installed (which it should be). Then install the package as follows:
```
sudo pip install vsn800_ardexa
```

You also need to install the `modpoll` tool
```
cd
mkdir modpoll
cd modpoll
wget http://www.modbusdriver.com/downloads/modpoll.3.4.zip
unzip modpoll.3.4.zip 
cd linux/
chmod 755 modpoll 
sudo cp modpoll /usr/local/bin
modpoll -h
```

## Usage
- This script can query many ethernet connected VSN800 weather stations.
- To discover RS485 address range and print out the station metadata
```
Usage: vsn800_ardexa discover ip_address port rs485_addresses
Eg; vsn800_ardexa discover 192.168.1.2 502 10-20
```

Send production data to a file on disk 
```
Usage: vsn800_ardexa get ip_address port rs485_addresses log_directory
Eg; vsn800_ardexa get 192.168.1.2 502 14-21 /opt/ardexa
```
{IP Address} = IP address of the weather stations combiner, eg; 192.168.1.2
{Port} = Modbus port, eg; 502
{RS485 Address(es)} = RS485 address or range of addresses, eg; 1-5 or 1,2,3 or 4 (for example)
{log directory} = logging directory, eg; /opt/ardexa/

To view debug output, increase the verbosity using the `-v` flag.
- standard (no messages, except errors), `-v` (discovery messages) or `-vv` (all messages)


## Collecting to the Ardexa cloud
Collecting to the Ardexa cloud is free for up to 3 x Raspberry Pis (or equivalent). Ardexa provides free agents for ARM, Intel x86 and MIPS based processors. To collect the data to the Ardexa cloud do the following:
- Create a `RUN` scenario to schedule the Ardexa ABB VSN800 script to run at regular intervals (say every 300 seconds/5 minutes).
- Then use a `CAPTURE` scenario to collect the csv (comma separated) data from the filename (say) `/opt/ardexa/logs/`. This file contains a header entry (as the first line) that describes the CSV elements of the file.

## Help
Contact Ardexa at support@ardexa.com, and we'll do our best efforts to help.
