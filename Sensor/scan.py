#!/usr/bin/env python3.7


import ctypes
import os


class scanConfigHead(ctypes.Structure):
    _fields_ = [
                ("scan_type", ctypes.c_uint8),
                ("scanConfigIndex", ctypes.c_uint16),
                ("scanConfig_serial_number", ctypes.c_char * 8),
                ("config_name", ctypes.c_char * 40)
               ]

class scanConfigStub(ctypes.Structure):
    _fields_ = [
                ("wavelength_start_nm", ctypes.c_uint16),
                ("wavelength_end_nm", ctypes.c_uint16),
                ("width_px", ctypes.c_uint8),
                ("num_patterns", ctypes.c_uint16),
                ("num_repeats", ctypes.c_uint16)
               ]

class scanConfig(ctypes.Structure):
    _fields_ = [
                ("head",scanConfigHead),
                ("stub",scanConfigStub)
               ]


class calibCoeffs(ctypes.Structure):
    _fields_  = [
                 ("ShiftVectorCoeffs",       ctypes.c_double *3),
                 ("PixelToWavelengthCoeffs", ctypes.c_double *3)
                ]

class slewScanSection(ctypes.Structure):
    _fields_ = [
                ("section_scan_type",ctypes.c_uint8),
                ("width_px", ctypes.c_uint8),
                ("wavelength_start_nm",  ctypes.c_uint16),
                ("wavelength_end_nm", ctypes.c_uint16),
                ("num_patterns", ctypes.c_uint16),
                ("exposure_time", ctypes.c_uint16)
              ]

class slewScanConfigHead(ctypes.Structure):
    _fields_ = [
                ("scan_type", ctypes.c_uint8),
                ("scanConfigIndex",ctypes.c_uint16),
                ("scanConfig_serial_number",ctypes.c_char * 8),
                ("config_name",ctypes.c_char*40),
                ("num_repeats",ctypes.c_uint16),
                ("num_sections",ctypes.c_uint8)
               ]

class slewScanConfig(ctypes.Structure):
    _fields_=[
              ("head",slewScanConfigHead),
              ("section", slewScanSection)
             ]

class slewScanConfigR(ctypes.Structure):
    _fields_=[
              ("head",slewScanConfigHead),
              ("section", slewScanSection * 5)
             ]


class scanResults(ctypes.Structure):

    _fields_ = [
                ("header_version",   ctypes.c_uint32),
                ("scan_name",        ctypes.c_char * 20),
                ("year",             ctypes.c_uint8),
                ("month",            ctypes.c_uint8),
                ("day",              ctypes.c_uint8),
                ("day_of_week",      ctypes.c_uint8),
                ("hour",             ctypes.c_uint8),
                ("minute",           ctypes.c_uint8),
                ("second",           ctypes.c_uint8),
                ("system_temp_100",  ctypes.c_uint16),
                ("detector_temp_100",ctypes.c_uint16),
                ("humidity_100",     ctypes.c_uint16),
                ("lamp_pd",          ctypes.c_uint16),
                ("scanDataIndex",    ctypes.c_uint32),
                ("calib_coeffs",     calibCoeffs),
                ("Serial_number",    ctypes.c_char *8),
                ("adc_data_length",  ctypes.c_uint16),
                ("black_ptrn_first", ctypes.c_uint8),
                ("black_ptrn_period",ctypes.c_uint8),
                ("pga",              ctypes.c_uint8),
                ("cfg",              slewScanConfigR),
                ("wavelength",       ctypes.c_double * 864),
                ("intensity",        ctypes.c_int * 864),
                ("length",           ctypes.c_int)
               ]

dlp_nano_lib = ctypes.CDLL("Sensor/src/libdlpspec.dll")
#dlp_nano_lib = ctypes.CDLL("libdlpspec.dll")

def unpack_ref(input):
    dict = {}
    for field_name, field_type in input._fields_:
        if field_name == "wavelength" or field_name == "intensity":
            value = getattr(input, field_name)
            if type(value) == type(bytes()):
                value = value.decode("utf-8")
            newval = []
            for i in value:
                newval.append(i)
            dict[field_name] = newval
    return dict

def unpack_fields(input):
    dict = {}
    for field_name, field_type in input._fields_:
        try:
            dict[field_name] = unpack_fields(getattr(input, field_name))
        except Exception as error:
            value = getattr(input, field_name)
            if type(value) == type(bytes()):
                value = value.decode("utf-8")
            elif type(value) not in [type(int()), type(float)]:
                newval = []
                for i in value:
                    try:
                        newval.append(unpack_fields(i))
                    except Exception as error:
                        newval.append(i)
                value = newval
            dict[field_name] = value

    return dict

def scan_interpret(file,interpret):

    buffer0 =  ctypes.create_string_buffer(len(file))

    for counter, byte in enumerate(file):
        buffer0[counter] = byte

    buffer_pointer = ctypes.pointer(buffer0)

    size_number = ctypes.c_size_t(len(file))

    results = scanResults()

    res_pointer = ctypes.byref(results)

    if interpret == 0:
        #raw data to be interpreted and formatted
        err = dlp_nano_lib.dlpspec_scan_interpret(buffer_pointer,size_number,res_pointer)
        print("Scan result interpret Error" + str(err))
    else:
        #raw data already interpreted by sensor, just format
        err = dlp_nano_lib.format_scan_interpret(buffer_pointer,res_pointer)
        print("Format Scan interpret Error" + str(err))

    return results

def scan_Ref_interpret(refData, refMatrix, scanData):

    buffer1 =  ctypes.create_string_buffer(len(refData))
    matrix =  ctypes.create_string_buffer(len(refMatrix))

    for counter, byte in enumerate(refData):
        buffer1[counter] = byte
    for counter, byte in enumerate(refMatrix):
        matrix[counter] = byte

    buffer_pointer = ctypes.pointer(buffer1)
    size_number = ctypes.c_size_t(len(refData))

    matrix_pointer = ctypes.pointer(matrix)
    matrix_size = ctypes.c_size_t(len(matrix))


    ref_results = scanResults()
    ref_pointer = ctypes.byref(ref_results)

    res_ptr = ctypes.byref(scanData)

    err = dlp_nano_lib.dlpspec_scan_interpReference(buffer_pointer,size_number,matrix_pointer,matrix_size,
 res_ptr, ref_pointer)

    print("Ref interpret Error" + str(err))

    return ref_results

def set_config(scan_name,start,end,repeats,patterns,res):

    config = scanConfig()

    for field_name, field_type in config._fields_:
        if field_name == "head":
            for fname, ftype in field_type._fields_:
                if fname == "scan_type":
                    value = 0
                elif fname == "scanConfigIndex":
                    value = 4
                elif fname == "scanConfig_serial_number":
                    value = str.encode("6110022")
                elif fname == "config_name":
                    value = str.encode(scan_name)
                setattr(config.head,fname,value)
        if field_name == "stub":
            for fname, ftype in field_type._fields_:
                if fname == "wavelength_start_nm":
                    value = start
                elif fname == "wavelength_end_nm":
                    value = end
                elif fname == "width_px":
                    value = res
                elif fname == "num_patterns":
                    value = patterns
                elif fname == "num_repeats":
                    value = repeats
                setattr(config.stub,fname,value)


    config_ptr = ctypes.byref(config)

    BufSize = ctypes.c_int()
    BufSizeptr = ctypes.byref(BufSize)

    err = dlp_nano_lib.dlpspec_get_scan_config_dump_size(config_ptr, BufSizeptr)
    print("Config size ERROR: " + str(err))


    config_serial = ctypes.create_string_buffer(BufSize.value)
    config_serial_ptr = ctypes.pointer(config_serial)
    config_len = ctypes.c_size_t(len(config_serial))

    err = dlp_nano_lib.dlpspec_scan_write_configuration(config_ptr, config_serial_ptr, config_len)

    print("Config serialize ERROR: " + str(err))


    serial_data = []
    for i in range(BufSize.value):
        serial_data.append(ord(config_serial[i]))
    return serial_data
