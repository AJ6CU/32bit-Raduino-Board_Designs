# Raduino V5 and V6
# IMPORTANT ALTHOUGH THESE BOARDS ARE ELECTRICALLY COMPATIBLE WITH v6, and they mechanically fit when you are using a Nextion, they sit too low to the tradional 16x2 LCD (the power switch and the LCD collide. If you want to use this board with an LCD, then you will to install an additional header between the Raduino and the motherboard (see photo below). This is not very practical and I will create a set of Raduinos that are higher and that will not have this problem in the future.

![headerpinsreqruied](https://user-images.githubusercontent.com/70183884/205141453-11581cf2-e115-446f-8bd5-954d1fc6ecee.jpg)

 
Each subdirectory is for a single MCU architecture:

- Nano-IOT-BLE-RPConnect-SingleBoard - A single board solution target at smaller systems (i.e. V6) where a second auxilary processor is not an option. The S-meter function has not been checked. V6 compatibility appears to work.
- Nano-IT-BLE-RPConnect with I2C - Design supporting a second processor for S-Meter, SWR, etc. This design appears to work but the I2C and the onboard S-meter not checked. V6 compatibility appears to work.
- Teensy 4 - Design for the Teensy 4.0 chip. Includes I2C connection. Teensu appears to work but requires more testing. The I2C and onboard S-meter has not yet been tested.
- RaspberryPi Pico - Supports the Raspberry Pi Pico - This is an initial effort and requires significant software changes to the KD8CEC software. This will not work until I get around to moving the encoder off of the analog pins. (Pico does not have enough Analog pins)/


Within each MCU directory, there are the following subdirectories:


- Gerbers - this directory includes a zip file that you should be able to upload to
            your favorite Fab house.
- PCBDesign - The designs are done with KiCad V6. You should be able to unzip this backup and directly use it with your tool.
- Images - conceptual 3D models of the board.

There is absolutely no warranty here. Use this at your own risk!


73
Mark Hatch
AJ6CU

