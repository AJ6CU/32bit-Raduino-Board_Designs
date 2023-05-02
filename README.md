# An uBitx Raduino for Next Generation Nano, Teensy and PICO


![theheard](https://user-images.githubusercontent.com/70183884/213938608-a9790997-cc9b-42be-b50f-ee695d674e6e.png)


The current release of the Raduino board sold by HF Signals only supports the "classic" Arduino nano. This device only has 32kb (actually 30kb with bootloader) of flash, 2kb of sram, and runs at 16mhz. The Classic Nano does have 1kb of EEPROM and is 5V signal compatible which prevents a "drop in replacement" by the new generation of Nano compatible footprint processors. 

The constraint of the "classic" Nano has limited the amount of features that can be implement in firmware. In fact, the popular firmware by Ian Lee (KD8CEC) barely squeezes into the flash memory of the Nano and any new features require tradeoffs of what features are going to be eliminated. It also caused KD8CEC to make some architectural decisions that makes the his software difficult to extend and debug. 

The purpose of these boards, are to remove this contraint. Currently the following chips are supported:
  1. Nano
  2. Nano Every
  3. Arduino BLE
  4. Arduino IOT
  5. Arduino RP2040
  6. Teensy 4.0 and Teensy 4.1
  7. Raspberry Pi Pico
  

There are two designs for each processor family:
- Compatible with the original "shorter" Raduino (v3,v4,v5,v6)
- Compatible with the newer "taller" Raduino that was introduced in v6.

73
Mark
AJ6CU 
