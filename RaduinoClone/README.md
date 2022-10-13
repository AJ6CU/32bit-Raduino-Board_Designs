# Raduino V5 and V6
# IMPORTANT THIS HAS NOT YET BEEN TESTED
# DO NOT USE
 
Each subdirectory is for a single MCU architecture:

- Nano-IOT-BLE-RPConnect-SingleBoard - A single board solution target at smaller systems (i.e. V6) where a second auxilary processor is not an option.
- Nano-IT-BLE-RPConnect with I2C - Design supporting a second processor for S-Meter, SWR, etc.
- Teensy 4 - Design for the Teensy 4.0 chip. Includes I2C connection.
- RaspberryPi Pico - Supports the Raspberry Pi Pico - This is an initial effort and requires significant software changes to the KD8CEC software.


Within each MCU directory, there are the following subdirectories:


- Gerbers - this directory includes a zip file that you should be able to upload to
            your favorite Fab house.
- PCBDesign - The designs are done with KiCad V6. You should be able to unzip this backup and directly use it with your tool.
- Images - conceptual 3D models of the board.

There is absolutely no warranty here. Use this at your own risk!


73
Mark Hatch
AJ6CU
