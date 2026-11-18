# Pico Raduino: proposed next revision

Drafted November 2026 from Mark's choices:

- an **Adafruit Si5351 daughter board**;
- **two USB serial ports** on the Pico's own USB, one for CAT and one for uBITX CEC Desktop;
- a **separate Nextion socket**;
- **no LCD connector**.

The other decisions from the notes are folded in: digital paddles, a PWR/SWR input, and the S-meter taken from the SDR.

The picture is `next_rev_proposed_layout.png`, a top view. It's a **sketch**: positions are approximate, and the module's size and pinout must be checked against the actual part.

Background: `PICO_RADUINO_LAYOUT_REVIEW.md` covers the crosstalk and the clock placement, and `PICO_RADUINO_NEXT_REVISION_NOTES.md` covers the reasoning behind each choice.

## What changes from Rev 10

| Removed | Why |
| :--- | :--- |
| U2 Si5351 (MSOP-10), Y1, C1, C2 | replaced by the module, which carries its own crystal and decoupling |
| J1 LCD connector, R4 | no TFT; frees GP8/9 and GP16–19, and the backlight load on the Pico's 3.3 V |
| U3 LM358, D1, C3, R1, R2, P7 | S-meter from the SDR; also frees A1 |
| P2 (Nextion power) | power now comes on the Nextion socket |

| Added | What for |
| :--- | :--- |
| **A1** Adafruit Si5351A breakout (#2045, or the STEMMA QT #5640) | the clocks; no fine-pitch soldering |
| **U7** low-noise 3.3 V LDO (LP5907 or MCP1700), with a ferrite and 10 µF | a clean supply for A1, away from the Pico's switching regulator |
| **R/C per clock** at P3 | 0 Ω series resistor (22–47 Ω optional), then the existing 0.1 µF DC block |
| **D2** Schottky (SS14 / 1N5819) | +5 V Reg to VSYS; stops the computer's USB powering the radio |
| **P5** Nextion socket, 4-pin JST-XH | power and data on one cable |
| **P8** paddle jack, 3-pin JST-XH | digital DIT/DAH |
| **P9** PWR/SWR, 4-pin JST-XH | forward and reflected from a detector |
| **P10** AUX UART, 4-pin (optional) | GP8/9 (UART1) for debugging, or a second Nextion later |
| JP1 solder jumper (optional) | A1 = forward power (default), or SMeter-In from P1-1 |

| Unchanged | |
| :--- | :--- |
| P3 (to the uBITX main board), P1 (controls), P4 + U6 + J2 (opto TX output), U1 7805, U4 EEPROM | U4 can become DIP-8 (24LC256-I/P) for the through-hole build; U6 can become the LTV-817 (DIP-4) |

## Placement

- **A1 sits directly above P3, between pins 14 and 8.**
  - Its CLK2, CLK1 and CLK0 outputs drop straight down to P3-14, P3-11 and P3-8, on top copper, about 10 mm each.
  - There are no vias on the clocks. Ground guard traces run between them, with vias to the In1 ground plane.
  - P3's ground pins (7, 9, 10, 12, 13) already sit between the clock pins.
  - If the module's clock pads don't line up with P3, fan them out. Keep each clock 3 mm or more from its neighbour and away from the 12 V (P3-15/16) and PTT traces.
- **U7 goes right beside A1's Vin.**
- **I2C (SDA/SCL, GP20/21)** is the only thing running from the Pico to A1. It's slow, so vias are fine.
- **The Pico stays where it is** (bottom side), with its **micro-USB at the right-hand end**. With J1 gone, the board's right edge is clear for the plug and a panel-mount USB extension.
- **D2** goes beside VSYS (Pico pin 39).
- **P8 and P9 go along the top edge**, right of P1, near the Pico's ADC pins (31–34). Keep their protection parts at the connector.
- **P5 goes on the left edge**, where P5/P2 are now.
- **The 12 V line** from P3-15/16 to U1 stays on the left, away from the clocks.

## Si5351 module wiring

| A1 pin | Goes to | Notes |
| :--- | :--- | :--- |
| Vin | U7's clean 3.3 V | **not +5 V**: see the I2C level warning below |
| GND | ground plane | several vias, close to the module |
| SDA / SCL | GP20 / GP21 (with U4) | the module has 10 kΩ pull-ups; R13/R14 (2.2 kΩ) may be left unfitted or kept, as both are in parallel |
| CLK0 | R, then C, then P3-8 | BFO |
| CLK1 | R, then C, then P3-11 | second LO |
| CLK2 | R, then C, then P3-14 | VFO |
| 3Vo | not connected | |

**I2C level warning, to verify on Adafruit's schematic.** The module's SDA/SCL level shifting probably pulls the host side up to **Vin**. Adafruit's usual design is a BSS138 shifter with pull-ups to Vin, but the guide doesn't say. With Vin = 5 V, the Pico's I2C pins would be pulled to 5 V, and RP2040 pins are not 5 V tolerant. **Feed Vin from 3.3 V.** U7 keeps that 3.3 V clean. The module's own LDO then runs with very little headroom, but the Si5351 is happy from about 2.5 V.

**Crystal:** 25 MHz on the module, which is what KD8CEC expects. Calibrate as usual.

**Mounting:** use a header socket so the module can be swapped. Check its height behind the front panel, and use a right-angle header if needed.

## Pico pin map

| Pico pin | GPIO | Rev 10 | Proposed |
| :--- | :--- | :--- | :--- |
| 1 | GP0 | Nextion TX | **P5-3 Nextion TX** (UART0) |
| 2 | GP1 | Nextion RX | **P5-4 Nextion RX** |
| 4–7, 9 | GP2–6 | P3-6 … P3-2 | unchanged |
| 10 | GP7 | T/R | unchanged (P3-1, J2 to the opto) |
| 11 | GP8 | LCD D/C | **P10 AUX UART1 TX** (optional) |
| 12 | GP9 | LCD touch | **P10 AUX UART1 RX** (optional) |
| 14 | GP10 | free | **FBUTTON** (moved from GP28) |
| 15 | GP11 | free | **DIT** (P8-1) |
| 16 | GP12 | free | **DAH** (P8-2) |
| 17 | GP13 | free | spare |
| 19 / 20 | GP14 / 15 | ENC-B / ENC-A | unchanged |
| 21, 22, 24, 25 | GP16–19 | LCD SPI | spare |
| 26 / 27 | GP20 / 21 | SDA / SCL | unchanged, to A1 and U4 |
| 29 | GP22 | PTT | unchanged |
| 31 | GP26 / A0 | Keyer (ladder) | unchanged: the **front-panel key jack keeps working** |
| 32 | GP27 / A1 | S-meter | **FWD power** (P9-1); JP1 can select SMeter-In instead |
| 34 | GP28 / A2 | FBUTTON | **REF power** (P9-2) |
| 33 | AGND | open | **to ground** |
| 35 | ADC_VREF | open | open, or an LM4040 3.0 V for accurate PWR/SWR |
| 36 | 3V3 out | +3.3 V | +3.3 V for the logic (U4, opto, pull-ups) |
| 39 | VSYS | +5 V Reg | **through D2** from +5 V Reg |
| 40 | VBUS | open | open |
| (internal) | GP23 | -- | firmware: drive high, so the Pico's regulator runs in PWM mode |

**Analog inputs:** A0 is the legacy keyer, A1 forward power, A2 reflected power. All three are used, the S-meter comes from the SDR, and the front-panel key jack still works. If someone wants the on-board S-meter path instead, JP1 puts SMeter-In on A1, and PWR/SWR is then forward only.

## Connectors

| Ref | Type | Pins |
| :--- | :--- | :--- |
| P5 Nextion | JST-XH 4 | 1 +5 V, 2 GND, 3 TX (GP0), 4 RX (GP1) |
| P8 Paddle | JST-XH 3 | 1 DIT (GP11), 2 DAH (GP12), 3 GND. On each line: 1 kΩ series, 1 nF to ground, TVS/ESD. Pull-ups to 3.3 V (internal or 10 kΩ) |
| P9 PWR/SWR | JST-XH 4 | 1 FWD (A1), 2 REF (A2), 3 GND, 4 +5 V. On each line: a divider for under 3.0 V full scale, 1 kΩ, Schottky clamps to 3.3 V/ground, 10 nF |
| P10 AUX (opt.) | 4-pin 2.54 | 1 +3.3 V, 2 GND, 3 TX (GP8), 4 RX (GP9) |
| USB | the Pico's micro-USB | to a panel-mount extension |

## The two USB serial ports (firmware)

- **No board parts needed.** It's one cable, and the computer sees two serial ports.
- **KD8CEC 2.0 changes:**
  - Build with the **Adafruit TinyUSB** stack (an arduino-pico build option). Create **two CDC interfaces** with distinct names, for example "uBITX CAT" and "uBITX App", so the app's port list and WSJT-X can tell them apart.
  - CAT moves from `Serial` to CDC #1. It's unchanged otherwise (the FT-817 emulation plus KD8CEC's EEPROM commands, which the Settings Editor uses).
  - **The Nextion protocol goes to both UART0 (P5) and CDC #2.** Each display message is sent to both, and commands are taken from either. The Nextion and the app then work side by side, as in KD8CEC's multi-Nextion setup but without shared wires.
  - Optional: also send it to UART1 (P10).
- **Check the baud rates.** CDC ports ignore baud rate, so the app's 57600 setting does no harm. P5 runs at whatever the Nextion is set to.
- **Later:** USB audio for FT8 transmit (QDX method) can be added as a third interface on the same cable. See the notes.

## Other firmware changes

- `USE_DIGITAL_PADDLE`: DIT/DAH on GP11/12, OR'd with the legacy A0 ladder.
- FBUTTON moves to GP10.
- PWR/SWR: read A1/A2 while transmitting, average or hold the peak, calibrate, and report to the Nextion and the app.
- Drive GP23 high (Pico regulator in PWM mode).
- Optional: lower the Si5351 drive strength (`si5351bx_drive`) to 4–6 mA after testing.

## To check before layout

1. **The Adafruit module:** its exact outline, header pin order, where the clock pins and their grounds are, and the **I2C pull-up voltage** (from Adafruit's schematic files). Also choose between #2045 and #5640.
2. **The module's height** behind the uBITX front panel.
3. **The micro-USB plug's reach** to the board edge or panel with the Pico on the bottom side, and the panel position for the USB extension.
4. **The front panel** for V6 owners without the TFT: a Nextion size and bezel.
5. **KD8CEC 2.0 with TinyUSB:** that it builds and runs, with two CDC ports on Mac, Windows and Linux.
6. **App:** port selection that shows the two ports by name.
