import io
import struct
import serial
import sys
import time

#Global Definition
AP_FILE = []
AP_CHECKSUM = 0
com=None
packet_number=0

#Functions
def error_return():
 com.close()
 sys.exit()

def uart_transfer(thelist, pn):
    # Fill the packet number
    thelist[4:8] = pn.to_bytes(4, byteorder='little')

    # Transmit package
    com.write(thelist)

    # Read ACK packet
    return_str = com.read(64)
    return_buffer = bytearray(return_str)

    # Compute and check checksum
    checksum = sum(thelist) % 2**16
    package_checksum = return_buffer[1] << 8 | return_buffer[0]
    if checksum != package_checksum:
        print("Checksum error")
        error_return()

    # Check ACK packet number
    rpn = int.from_bytes(return_buffer[4:8], byteorder='little')
    if rpn != pn + 1:
        print("Package number error")
        error_return()

    return return_buffer

def uart_transfer_auto(thelist, pn):
    # Fill the packet number
    thelist[4:8] = pn.to_bytes(4, byteorder='little')

    while True:
        com.flushInput()
        com.timeout = 0.025
        com.flushOutput()
        com.write(thelist)
        time.sleep(0.01)
        return_str = com.read(64)
        return_buffer = bytearray(return_str)

        # Check return length and checksum
        if len(return_buffer) != 0:
            checksum = sum(thelist) % (2 ** 16)
            package_checksum = (return_buffer[1] << 8) | return_buffer[0]

            if checksum != package_checksum:
                print("Checksum error")
                # error_return()

            # Check ACK packet number
            rpn = int.from_bytes(return_buffer[4:8], byteorder='little')

            if rpn != (pn + 1):
                print("Package number error")
            else:
                break

    return return_buffer



def uart_auto_detect():
    global packet_number
    link = bytearray(64)
    packet_number = 0x01
    link[0] = 0xae
    uart_transfer_auto(link, packet_number)


def link_fun():
    global packet_number
    link = bytearray(64)
    packet_number = 0x01
    link[0] = 0xAE
    uart_transfer(link, packet_number)
  
 
def sn_fun():
    global packet_number
    packet_number += 2
    SN_PACKAGE = [0] * 64
    SN_PACKAGE[0] = 0xa4
    SN_PACKAGE[8] = packet_number& 0xff
    SN_PACKAGE[9] = packet_number >> 8 & 0xff
    SN_PACKAGE[10] = packet_number >> 16 & 0xff
    SN_PACKAGE[11] = packet_number >> 24 & 0xff
    uart_transfer(SN_PACKAGE, packet_number)

def read_fw_fun():
    global packet_number
    packet_number += 2
    read_fw_version = [0] * 64
    read_fw_version[0] = 0xa6
    buf = uart_transfer(read_fw_version, packet_number)
    fw_version = buf[8]
    print("FW_VERSION=0x{:08x}".format(fw_version))
    
def read_pid_fun():
    global packet_number
    packet_number += 2
    read_pid = [0] * 64
    read_pid[0] = 0xb1
    buf = uart_transfer(read_pid, packet_number)
    pid = buf[8] | buf[9] << 8 | buf[10] << 16 | buf[11] << 24
    print("PID=0x{:08X}".format(pid))

def read_config_fun():
    global packet_number
    packet_number += 2
    read_config = [0] * 64
    read_config[0] = 0xa2
    buf = uart_transfer(read_config, packet_number)
    config0 = buf[8] | buf[9] << 8 | buf[10] << 16 | buf[11] << 24
    config1 = buf[12] | buf[13] << 8 | buf[14] << 16 | buf[15] << 24
    print("CONFIG0=0x{:08X}".format(config0))
    print("CONFIG1=0x{:08X}".format(config1))

def read_aprom_bin_file(filename):
    # Open file and read contents into a list
    try:
        with open(filename, 'rb') as f:
            global AP_FILE, AP_CHECKSUM
            AP_CHECKSUM = 0
            AP_FILE = list(f.read())
            for byte in AP_FILE:
                AP_CHECKSUM += byte
    except:
        print("APROM File load error")
        error_return
    # print('[{}]'.format(', '.join(hex(x) for x in AP_FILE)))
    # print(len(AP_FILE))
    
def read_ldrom_bin_file(filename):
    # Open file and read contents into a list
    try:
        with open(filename, 'rb') as f:
            global LD_FILE, LD_CHECKSUM
            LD_CHECKSUM = 0
            LD_FILE = list(f.read())
            for byte in LD_FILE:
                LD_CHECKSUM += byte
    except:
        print("APROM File load error")
        error_return
    # print('[{}]'.format(', '.join(hex(x) for x in AP_FILE)))
    # print(len(AP_FILE))
    
def update_aprom():
    global AP_FILE, AP_CHECKSUM, packet_number
    packet_number += 2
    ap_address = 0
    ap_size = len(AP_FILE)  # get .bin file size
    pap_command = [0] * 64
    pap_command[0] = 0xa0

    # Set APROM START ADDRESS 
    pap_command[8] = ap_address & 0xff
    pap_command[9] = ap_address >> 8 & 0xff
    pap_command[10] = ap_address >> 16 & 0xff
    pap_command[11] = ap_address >> 24 & 0xff

    # Set APROM SIZE
    pap_command[12] = ap_size & 0xff  
    pap_command[13] = ap_size >> 8 & 0xff
    pap_command[14] = ap_size >> 16 & 0xff
    pap_command[15] = ap_size >> 24 & 0xff
    pap_command[16:64] = AP_FILE[0:48]  # first data fragment to copy
    uart_transfer(pap_command, packet_number)  # start first packet transfer

    # continue to transfer remaining data fragment
    for i in range(48, ap_size, 56):
        packet_number += 2
        pap1_command = [0] * 64
        pap1_command[8:64] = AP_FILE[i:(i+56)]

        # short or last data fragment handling
        if len(pap1_command) < 64:
            pap1_command.extend([0xFF] * (64 - len(pap1_command)))

        if ((ap_size - i) < 56) or ((ap_size - i) == 56):
            buf = uart_transfer(pap1_command, packet_number)
            d_checksum = buf[8] | buf[9] << 8
            if d_checksum == (AP_CHECKSUM & 0xffff):
                print("checksum pass")
        else:
            uart_transfer(pap1_command, packet_number)
            
def erase_all_fun():
    global packet_number
    packet_number += 2
    erase_all = [0] * 64
    erase_all[0] = 0xa3
    buf = uart_transfer(erase_all, packet_number)
    #fw_version = buf[8]
    #print("FW_VERSION=0x{:08x}".format(fw_version))         
            

if __name__ == '__main__':
    
    #check parameter
    if len(sys.argv)!=3:
     print("Usage  : py3isp [COM port number] [.bin path]")
     print("Example: python py3isp COM0 c:\\test.bin")
     sys.exit("Wrong Parameter!")
    
    #initialize serial port for .bin file downloading
    com=serial.Serial(sys.argv[1],115200)
    
    #connect to ISP application
    print("*Press Reset Button on Evaluation Board")
    uart_auto_detect()
    com.timeout=None
    
    #download .bin file
    link_fun()
    sn_fun()
    read_pid_fun()
    read_fw_fun()
    read_config_fun()
    erase_all_fun()
    read_aprom_bin_file(sys.argv[2])
    update_aprom() 
    #erase_all_fun()

    com.close()
    print("Download complete.")
    


