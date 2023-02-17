# Using_Nuvoton_ISP_on_the_PC(Windows)

## Intro
You can ISP firmware update to Nuvoton MCU on the Windows (using UART) with this project. Protocol is follow to “NuMicro ISP Programming Tool version 4.03 for Windows OS” provided by Nuvoton. 

## Development environment
### Windwos PC 
|N|Name|Description|Note|
|---|---|---|---|
|1| Windwos 10 Home|Ver. 21H2 OS BUILD 19044.2486|OS|
|2|Visual Studio Code|Ver. 1.75|IDE|
|3|NuMicro ICP Programming Tool|Ver. 3.10||

### MCU
|N|Name|Description|Note|
|---|---|---|---|
|1|ARM MDK|Keil uVision Ver. 5.34.0.0|IDE|
|2|M0518 BSP|Ver. 3.00.005|[Link](https://github.com/OpenNuvoton/M0518BSP/tree/master/SampleCode/ISP)|
|3|NT-N0518S|Ver. 2.1|H/W Board|

### Python
|N|Name|Description|Note|
|---|---|---|---|
|1|Python|3.10.5||
|2|pyserial|3.5|module|

## System Overview(used Bridge firmware)
![image](https://user-images.githubusercontent.com/108905975/219515466-dbda522b-e471-443d-9ea2-126214637b1b.png)

## How to ISP Firmware update on the PC side(using UART)
1. Write the ld.bin file as shown in the picture below.
![image](https://user-images.githubusercontent.com/108905975/219517025-a392479e-1482-471d-90c5-71f258e03826.png)

2. Run the Python program as shown in the picture below.
![image](https://user-images.githubusercontent.com/108905975/219517644-8be4872a-8eaa-4d2c-8454-5d66f5d7f11f.png)

## Packet Description
Packet size is 64 Byte. There have 4 Byte of command list and 4 Byte of command index. You can ignore command index in the packet.<br />
![image](https://user-images.githubusercontent.com/99227045/187109385-1f5d628d-3b3e-4147-8a75-4212bc504247.png)

Please refer table below for command list.
|Command|Value(Hex/4 Byte)|Description|Note|
|---|---|---|---|
|CMD_UPDATE_APROM|0x000000A0|Update data to the internal flash of target board.||
|CMD_CONNECT|0x000000AE|Try connect to target board.||
|CMD_GET_DEVICEID|0x000000B1|Request device ID to target board.||
|CMD_SYNC_PACKNO|0x000000A4|Synchronize packet number with ISP device before a valid command send||
|CMD_GET_FWVER|0x000000A6|Get version information of ISP firmware.||
|CMD_READ_CONFIG|0x000000A2 |Get Config0 and Config1.||
|CMD_ERASE_ALL|0x000000A2 |Instruct ISP to erase APROM, Data Flash, and set Config0 and Config1 registers to 0xFFFFFF7F and 0x0001F000.||

## Ref Document
https://github.com/OpenNuvoton/Nuvoton_Tools/tree/master/doc<br />
http://forum.nuvoton.com/viewtopic.php?t=8521<br />
