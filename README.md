# An uBitx Raduino for the New Generations of Nanos

The current release of the Raduino board sold by HF Signals only supports the "classic" Arduino nano. This device only has 32kb (actually 30kb with bootloader) of flash, 2kb of sram, and runs at 16mhz. The Classic Nano does have 1kb of EEPROM and is 5V signal compatible which prevents a "drop in replacement" by the new generation of Nano compatible footprint processors. 

The constraint of the "classic" Nano has limited the amount of features that can be implement in firmware. In fact, the popular firmware by Ian Lee (KD8CEC) barely squeezes into the flash memory of the Nano and any new features require tradeoffs of what features are going to be eliminated. It also caused KD8CEC to make some architectural decisions where the UX is implemented on the Nextion screen using some features (i.e. timers) that are difficult to extend and debug. Although I have not looked at the V6 touchscreen software provided by HF Signals, I can reasonably believe that they face a similar contraint as well anybody that wants to hack the software.

The purpose of this board, is to remove this contraint. I have added a common I2C EEPROM (24C256) and made it possible to select the input voltage from the regulated 5V line (for 5V compatible boards, the 5V goes into the +5 pin, for 3.3V, the 5V regulated goes into the VIN pin where the onboard 3.3v regulator does it job). I have made the design decision that the 5V regulation will be done off the Raduino. This allows the possibility of separating the 5V rails for the power hungry and RF noisey Nextion from the 5V needed by the rest of the system. (A future effort includes creation of a power supply board with polarity protection that might also support the extra Nano used for S-meter by the KD8CEC software. - Stay tuned).

The initial release is targeted at V5 and below boards (i.e., those without the touch screen provided with the V6 product from HF Signals). Once I get this working (that means that  KD8CEC 1.2 is working on the system), I will respin a new board for the V6 that provides both the OEM touchscreen as well as support for the KD8CEC Nextion combo.

73
Mark
AJ6CU 
