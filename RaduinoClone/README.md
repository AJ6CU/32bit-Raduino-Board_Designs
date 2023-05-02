# Raduino Clones
Rev 6.A - May 2, 2023


This directory contains a subdirectory for each processor architecture:

- Nano Family Nano-Every-IOT-BLE-RP2040
- RaspberryPi Pico  
- Teensy 4.0 
- Teensy 4.1


Within each processor directory, there are two subdirectories:

- uBitx V6Specific - this design matches the mechanical and electrial design of the V6 board. The traditional 2x16 LCD header, like in the V6 OEM design, is not on this board. Rather, it includes the TFT LCD design and electrical connections of the V6 TFT LCD.

- uBITX V3456 - this design is compatible with the original Raduino physical characterisics with an LCD header compatible with 2x16. V6 can be supported by using a larger pin header on the bottom and adding the pullup resister. However, this design is likely to have mechanical compatibility problems and so is not recommended for V6 systems using the original V6 case.

And finally each of these directories include:

- BOM basic bill of materials
- Gerbers - this directory includes a zip file that you should be able to upload to
            your favorite Fab house.
- Images - conceptual 3D models of the board.
- PCBDesign - The designs are done with KiCad V7. You should be able to unzip this backup and directly use it with your tool.
- Schematic - pdf version of the design.


There is absolutely no warranty here. Use this at your own risk!


73
Mark Hatch
AJ6CU

