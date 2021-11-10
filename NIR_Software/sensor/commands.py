#!/usr/bin/env python3.7
from enum import Enum


USB_HDR    = 0x00
FLG_SEQ0   = 0x00
FLG_LEN0   = 0x00
FLG_READ   = 0xC0   # read ready
FLG_WRITE  = 0x40   # write ready

FLG_STATUS = {"R/W" : 0, "RDY" : 0, "ERR": 0}

class cmd(Enum):
    PRF_CSUM = 1
    WRT_DATA = 2
    RED_FSZE = 3
    RED_FDAT = 4
    TIV_VERS = 5
    STR_SCAN = 6
    SCN_STAT = 7
    STR_CONF = 8
    NUM_CONF = 9
    GET_SCON = 10
    SET_SCON = 11
    GET_TDAT = 12
    DEV_STAT = 13
    LED_TEST = 14
    SCN_TIME = 15
    CFG_APPY = 16
    ERR_STAT = 17
    ERR_CLER = 18
    SIZ_LIST = 19
    RED_LIST = 20
    STR_SINT = 21
    INT_STAT = 22
    SET_TDAT = 23
    LMP_CTRL = 24
    DLP_PWUP = 25
    SET_GAIN = 26
    GET_GAIN = 27
    SET_HIBM = 28
    GET_HIBM = 29

################################################################################
#Command Bytes :
#[name,usb_hdr, flags:r/w, seq_no,length,Command_byte,group_byte,output_bytes+ack bytes]
#
# * for variable size output_bytes value of 0 is assigned and later changed to
#   actual value.
# * for reads the return data size is output_bytes + 4.
# * for writes the return data size is output bytes + 1.
################################################################################

CMD_SIZ_LIST = [cmd.SIZ_LIST, USB_HDR, FLG_READ,  FLG_SEQ0, 0x03, 0x00, 0x2B, 0x00, 4+4]        # Read file list size
CMD_RED_LIST = [cmd.RED_LIST, USB_HDR, FLG_READ,  FLG_SEQ0, 0x03, 0x00, 0x2C, 0x00, 0+4]        # Read file list
CMD_WRT_DATA = [cmd.WRT_DATA, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x02, 0x00, 0x25, 0x00, 0+1]        # Write file data
CMD_RED_FSZE = [cmd.RED_FSZE, USB_HDR, FLG_READ,  FLG_SEQ0, 0x03, 0x00, 0x2D, 0x00, 4+4]        # Read file size
CMD_RED_FDAT = [cmd.RED_FDAT, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x2E, 0x00, 0]          # Read file data

CMD_DLP_PWUP = [cmd.DLP_PWUP, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x04, 0x00, 0x05, 0x01, 0+1]        # Enable DLP subsystem and turn on lamp

CMD_LED_TEST = [cmd.LED_TEST, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x03, 0x00, 0x0B, 0x01, 1+1]        # LED Test
CMD_TIV_VERS = [cmd.TIV_VERS, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x16, 0x02,28+4]        # Read version info
CMD_STR_SCAN = [cmd.STR_SCAN, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x03, 0x00, 0x18, 0x02, 0+1]        # Start scan
CMD_SCN_STAT = [cmd.SCN_STAT, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x19, 0x02, 1+4]        # Scan status-> 0:in progress
                                                                                                #               1:complete
CMD_SET_GAIN = [cmd.SET_GAIN, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x04, 0x00, 0x0C, 0x04, 0+1]        # Set PGA Gain
CMD_CFG_APPY = [cmd.CFG_APPY, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x00, 0x00, 0x1E, 0x02, 4+1]        # Write custom config
CMD_STR_CONF = [cmd.STR_CONF, USB_HDR, FLG_READ,  FLG_SEQ0, 0x04, 0x00, 0x20, 0x02, 95+4]       # Read stored scan configs
CMD_NUM_CONF = [cmd.NUM_CONF, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x22, 0x02, 1+4]        # Read num of stored configs
CMD_GET_SCON = [cmd.GET_SCON, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x23, 0x02, 1+4]        # Read active scan config
CMD_SET_SCON = [cmd.SET_SCON, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x03, 0x00, 0x24, 0x02, 0+1]        # Set Active scan config
CMD_LMP_CTRL = [cmd.LMP_CTRL, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x03, 0x00, 0x25, 0x02, 0+1]        # Keep lamp on after scan
CMD_GET_GAIN = [cmd.GET_GAIN, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x28, 0x02, 1+4]        # Get PGA Gain

CMD_SCN_TIME = [cmd.SCN_TIME, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x37, 0x02, 4+4]        # Get Scan time
CMD_STR_SINT = [cmd.STR_SINT, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x02, 0x00, 0x39, 0x02, 0+1]        # Start scan interpret
CMD_INT_STAT = [cmd.INT_STAT, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x3A, 0x02, 1+4]        # Scan interpret status



CMD_SET_TDAT = [cmd.SET_TDAT, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x09, 0x00, 0x09, 0x03, 0+1]        # set time and date
CMD_GET_TDAT = [cmd.GET_TDAT, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x0C, 0x03, 7+4]        # Get time and date
CMD_SET_HIBM = [cmd.SET_HIBM, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x03, 0x00, 0x0E, 0x03, 0+1]        # Set Hibernation Mode
CMD_GET_HIBM = [cmd.GET_HIBM, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x0F, 0x03, 1+4]        # Get Hibernation Mode

CMD_DEV_STAT = [cmd.DEV_STAT, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x03, 0x04, 4+4]        # Read device status
CMD_ERR_STAT = [cmd.ERR_STAT, USB_HDR, FLG_READ,  FLG_SEQ0, 0x02, 0x00, 0x04, 0x04, 20+4]       # Get Error Status
CMD_ERR_CLER = [cmd.ERR_CLER, USB_HDR, FLG_WRITE, FLG_SEQ0, 0x02, 0x00, 0x05, 0x04, 0+1]        # Clear Error Status

