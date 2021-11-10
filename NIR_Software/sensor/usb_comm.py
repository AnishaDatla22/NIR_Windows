#!/usr/bin/env python3.6

import hid
import time
from ctypes import *
from Sensor.commands import *
from Sensor.scan import *
import matplotlib.pyplot as plt
import math
import datetime

TIMEOUT = 1000
READ_FILE_SIZE = 0
FILE = []
h = 0
scan_interpret_done = 0
device_busy = 1
scanresults =scanResults()

#Open Devices
def setup(VID,PID):
    global h

    device_list = hid.enumerate(VID,PID)
    print (device_list)
    h = hid.device()
    h.open(VID,PID)

    set_date()
    get_sleep_mode()
    set_sleep_mode(0)     # Turn off hibernation

#Sends commands to device and waits for read data back from device
def send_info(cmd_name,cmd,ret_len):
     global h

     h.write(cmd)
     time.sleep(0.05)
     if ret_len != 0:
         data = h.read(ret_len)
         process_data(data,cmd_name)

#Decodes the Flag byte
def extract_flags(flag_byte):
    global FLG_STATUS

    FLG_STATUS["ERR"] = (flag_byte & 0x30) >> 4
    FLG_STATUS["R/W"] = (flag_byte & 0x80) >> 7
    FLG_STATUS["RDY"] = (flag_byte & 0x40) >> 6
    print("R/W: " + str(FLG_STATUS["R/W"]) +
          " Rdy: " + str(FLG_STATUS["RDY"]) +
          " Err: " + str(FLG_STATUS["ERR"]) )
    return FLG_STATUS

#Decodes read message from device
def process_data(data,cmd_name):

    status = extract_flags(data[0])

    if status["ERR"] == 1:
        #get error status
        send_info(CMD_ERR_STAT[0],CMD_ERR_STAT[1:8],CMD_ERR_STAT[8])
        #Clear the error status
        #send_info(CMD_ERR_CLER[0],CMD_ERR_CLER[1:8],CMD_ERR_CLER[8])
    elif status["R/W"] == 0 and len(data)>1:
        read_data_process(data[1:],cmd_name)
    elif status["R/W"] == 1:                      # read  transaction
        seq_no = data[1]
        print("Seq_no: " + str(seq_no))
        length = data[2] + (data[3] << 8)
        print("Packet_Len: " + str(length))
        read_data_process(data[4:],cmd_name)
    else:
        print("\n")

# cmd specific decode of data
def read_data_process(rd_data,cmd_name):

    if cmd_name == cmd.RED_FSZE or cmd_name == cmd.SIZ_LIST:
        global READ_FILE_SIZE
        size = 0
        for i in range(len(rd_data)):
            size += rd_data[i] << (i*8)
        READ_FILE_SIZE = size
        print("READ FILE SIZE: " + str(READ_FILE_SIZE) + "\n")

    elif (cmd_name == cmd.CFG_APPY) or (cmd_name == cmd.ERR_STAT) or (cmd_name == cmd.GET_HIBM):
        for i in rd_data:
            print(hex(i))

    elif cmd_name == cmd.GET_TDAT:
        print("{}-{}-{}  {}:{}:{}\n".format(rd_data[2],rd_data[1],
                                            rd_data[0],rd_data[4],
                                            rd_data[5],rd_data[6]))

    elif cmd_name == cmd.LED_TEST:
        if rd_data[0] == 0:
            print("LED TEST PASSED\n")
        else:
            print("LED TEST FAIL\n")

    elif cmd_name == cmd.NUM_CONF:
        print("NUM OF STORED SCAN CONFIGS: " + str(rd_data[0]) + "\n")

    elif cmd_name == cmd.GET_SCON:
        print("ACTIVE SCAN CONFIG: " + str(rd_data[0]) + "\n")

    elif cmd_name == cmd.GET_GAIN:
        print("PGA GAIN SET AT: " + str(rd_data[0]) + "\n")

    elif cmd_name == cmd.DEV_STAT:
        global device_busy
        print("Device Status: "+str(rd_data[0]) + "\n")
        if rd_data[0] == 1:
            device_busy = 0

    elif cmd_name == cmd.SCN_TIME:
        time = 0
        for i in range(len(rd_data)):
           time += rd_data[i] << (i*8)
        print("SCAN_TIME: " + str(time)+ "\n")

    elif cmd_name == cmd.INT_STAT:
        global scan_interpret_done
        scan_interpret_done = rd_data[0]
        print("Scan Interpret Done:" +str(rd_data[0])+"\n")

    elif cmd_name == cmd.TIV_VERS:
        print("Tiva SW version: " + str(rd_data[0:4]))
        print("DLPC SW version: " + str(rd_data[4:8]))
        print("DLPC Flash version: " + str(rd_data[8:12]))
        print("DLP Spectrum Library version: " + str(rd_data[12:16]))
        print("EEPROM Calibration version: " + str(rd_data[16:20]))
        print("EEPROM Reference version: " + str(rd_data[20:24]))
        print("EEPROM Scan Configuration version: " + str(rd_data[24:28]))


# Gets scan/ref data
def read_burst_data(cmd_name,cmd,ret_len):

    global FILE
    global h
    rfile = []
    while len(rfile) < ret_len:
        h.write(cmd)
        time.sleep(0.03)
        data = 1
        extra = []
        while data:
            data = 0
            data = h.read(64,10)
            extra.extend(data)
        process_data(extra[0:4],cmd_name)
        rfile.extend(extra[4:516])
    FILE = rfile
    return FILE



#Write to file

def write_to_file(fname,data):

    f1 = open(fname,'w')
    for key in data:
        f1.write(key + " ")
        f1.write(str(data[key]))
        f1.write("\n\n")
    f1.close()



#Get Version Numbers
def get_ver():
    send_info (CMD_TIV_VERS[0], CMD_TIV_VERS[1:8], CMD_TIV_VERS[8])

#Set Date and Time
def set_date():
    cur_tdat = CMD_SET_TDAT[1:8]
    now = datetime.datetime.now()
    year = int(str(now.year)[2:])
    weekday = datetime.date(now.year,now.month,now.day).weekday()
    cur_tdat.extend([year,now.month,now.day,weekday,now.hour,now.minute,now.second])

    send_info (CMD_SET_TDAT[0], cur_tdat, CMD_SET_TDAT[8]) # Set time and date

#Get Date and Time
def get_date():
    send_info (CMD_GET_TDAT[0], CMD_GET_TDAT[1:8], CMD_GET_TDAT[8]) # Get time and date

def get_sleep_mode():
     send_info (CMD_GET_HIBM[0], CMD_GET_HIBM[1:8], CMD_GET_HIBM[8]) # Get sleep mode flag

def set_sleep_mode(flag):
     sleep_mode = CMD_SET_HIBM[1:8]
     sleep_mode.append(flag)
     send_info (CMD_SET_HIBM[0], sleep_mode, CMD_SET_HIBM[8])  # Set sleep mode flag

#Start LED Test
def led_test(start):
    led_start = CMD_LED_TEST[1:8]
    led_start.append(start)
    send_info (CMD_LED_TEST[0], led_start, CMD_LED_TEST[8])  #start led Test

# Get number of scan configs available and current active config
def get_scan_config_id():
    send_info (CMD_NUM_CONF[0], CMD_NUM_CONF[1:8], CMD_NUM_CONF[8]) #Num of scan config
    send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8]) #Current active config


# Pick Active config
def set_active_config(index):
    set_scan_config = CMD_SET_SCON[1:8]
    set_scan_config.append(index)             # Select config by user
    send_info (CMD_SET_SCON[0], set_scan_config, CMD_SET_SCON[8])

    send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8])

#Set PGA Gain
def set_gain(pga_gain):

    isFixed =   1                   # isFixed during scan or not
    gain_value = (2**int(pga_gain))
    set_pga_gain = CMD_SET_GAIN[1:8]
    set_pga_gain.append(isFixed)
    set_pga_gain.append(gain_value)
    print(set_pga_gain)
    send_info (CMD_SET_GAIN[0], set_pga_gain, CMD_SET_GAIN[8])

    send_info (CMD_GET_GAIN[0], CMD_GET_GAIN[1:8], CMD_GET_GAIN[8])

#Start the scan
def start_scan(store_in_sd):
    global scan_interpret_done
    global device_busy

    #Scan Time
    send_info (CMD_SCN_TIME[0], CMD_SCN_TIME[1:8], CMD_SCN_TIME[8])


    #Start Scan
    start_scan = CMD_STR_SCAN[1:8]
    start_scan.append(store_in_sd)
    send_info (CMD_STR_SCAN[0], start_scan, CMD_STR_SCAN[8])

    #Device Status, wait until scan is done
    while device_busy != 0:
        send_info (CMD_DEV_STAT[0], CMD_DEV_STAT[1:8], CMD_DEV_STAT[8])
        time.sleep(0.5) #check after 500msec
    device_busy = 1

    send_info (CMD_GET_GAIN[0], CMD_GET_GAIN[1:8], CMD_GET_GAIN[8])
""" #Scan Interpret
    while scan_interpret_done != 1:
        send_info (CMD_INT_STAT[0], CMD_INT_STAT[1:8], CMD_INT_STAT[8])
        time.sleep(0.5) #check after 500msec
    scan_interpret_done = 0
"""


#read scan data
def read_data(type):
    # get file size of  data
    read_file_size = CMD_RED_FSZE[1:8]
    read_file_size.append(type)
    send_info (CMD_RED_FSZE[0], read_file_size, CMD_RED_FSZE[8])

    # Read  data
    Data = read_burst_data (CMD_RED_FDAT[0], CMD_RED_FDAT[1:8],READ_FILE_SIZE+4)

    return Data

#convert scan raw data to python dict
def get_results():
    global scanresults


    scanData = read_data(0)   # 0: scan_data, 8: scan_interpret_data
    # Interpret Results
    scanresults = scan_interpret(scanData,0)  # 0: interpret and format, 1: only format
    results = unpack_fields(scanresults)


    #write results to txt file
    write_to_file("scanResults.txt",results)

    return results

#Get ref raw data
def get_ref_data():
    global scanresults
    refData   = read_data(2)
    refMatrix = read_data(3)

    #Interpret ref data
    scan_ref = scan_Ref_interpret(refData,refMatrix,scanresults)
    #Unpack to python dict
    ref_results = unpack_fields(scan_ref)
    write_to_file("refResults.txt",ref_results)

    return ref_results


#Set custom Scan Config
def set_scan_config(scan_name,start,end,repeats,res,patterns):

    #patterns = (end - start)/res
    serial_scan_config = set_config(scan_name, int(start), int(end), int(repeats), int(patterns), int(res))
    buf_len = len(serial_scan_config)
    data = []
    data = CMD_CFG_APPY[1:8]
    data[3] = buf_len + 2


    data.extend(serial_scan_config)
    send_info(CMD_CFG_APPY[0], data, CMD_CFG_APPY[8])
