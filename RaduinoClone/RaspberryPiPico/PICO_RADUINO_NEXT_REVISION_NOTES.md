# Pico Raduino: notes for the next revision

Ideas for the next board after Rev 6A: a CW key input of its own and a
power/SWR input. Collected November 2026 while working on uBITX CEC Desktop.
These are design notes, not a finished design. Nothing here has been built.

## Goals

1. **CW paddles on digital inputs**, not KD8CEC's analog resistor ladder.
2. **Forward and reflected power** (PWR/SWR) measured on the board.
3. Keep the board fitting **existing uBITX radios** with as little surgery as
   possible.
4. Keep the radio's settings in **KD8CEC's EEPROM**, so programs that set them
   (uBITX CEC Desktop's CW tab, the Settings Editor) keep working.

## Where the analog inputs stand today

From the Pico section of `ubitx.h` in KD8CEC-V2.0-for-uBITX:

| Pin | Use now |
| :--- | :--- |
| A0 (GP26) | `ANALOG_KEYER`, the paddles and straight key through the resistor ladder |
| A1 (GP27) | `ANALOG_SMETER` |
| A2 (GP28) | free |
| GP29 | not usable on a Pico or Pico 2: wired inside to measure the supply (VSYS/3) |

The encoder, F button and PTT are already digital (pins 14–17).

PWR/SWR needs two inputs (forward and reflected), and only one is free. Ways
round that:

1. **Move the keyer to digital inputs.** This frees A0. *Chosen; see below.*
2. Share A1 between the S-meter (receive) and reflected power (transmit) with
   an analog switch (74HC4053 or TS5A23157) driven by the TX line. Works, since
   the two are never needed at once, but adds a part.
3. An I2C ADC (ADS1115: 4 channels, 16 bits) on the existing I2C bus (GP20/21).
   Easy in software, and KD8CEC 2.0's I2C S-meter code is a model, but it's one
   more chip.
4. A different RP2 board: one that brings GP29 out, or the 48-pin RP2350B with
   8 ADC inputs.

With the keyer digital, the analog inputs become:

| Pin | Use |
| :--- | :--- |
| A0 (GP26) | **Forward** power |
| A1 (GP27) | S-meter (unchanged) |
| A2 (GP28) | **Reflected** power |

## CW key input

### The problem

The uBITX's key jack takes stereo plugs, but the radio combines tip and ring
into one analog line through a resistor ladder. The Raduino only ever sees one
wire (A0 on the Pico, A6 on the Nano). Analog paddle reading depends on
thresholds and is sensitive to RF.

### Recommended: a separate key jack, wired to its own connector

Add a **separate stereo 3.5 mm key jack**, for example on the rear panel, wired
straight to a **new connector on the Pico board**. The original jack and its
ladder are left alone: no cutting or rewiring on the main board, and undoing
the upgrade means unplugging one cable.

- **Connector:** 3-pin JST-XH (tip = dit, ring = dah, sleeve = ground), or
  4-pin with a spare.
- **Cable:** shielded, with the shield grounded at one end.
- **Inputs:** two GPIOs with pull-ups to **3.3 V** (never the radio's 5 V; the
  Pico's pins aren't 5 V tolerant). The internal pull-ups work, or 10 kΩ
  external.
- **RF and static, on each line:** about 1 kΩ in series, about 1 nF to ground
  right at the connector, and ideally a ferrite on the cable or a small
  TVS/ESD diode. A paddle lead is an antenna next to a 10 W transmitter, and
  unprotected inputs are the usual cause of "the keyer sends by itself on
  transmit".
- **Straight key with a mono plug:** a mono plug shorts the ring to the sleeve.
  If dah reads as held at power-up, treat the tip as a straight key.
- **The original jack:** either leave it disconnected (simplest, frees A0), or
  keep it on A0 as a legacy straight-key-only input. With two keying inputs
  live at once the firmware has to OR them, and a paddle forgotten in the old
  jack can surprise someone.

### Firmware

- A compile option, for example `USE_DIGITAL_PADDLE`, replaces the analog
  paddle read in `ubitx_keyer.ino` with two digital pin reads.
- Keep KD8CEC's iambic A/B logic and timing. The RP2040 is far faster than this
  needs, and PIO could even do the timing in hardware.
- Key type (straight / iambic A / iambic B), speed and the delays stay in
  KD8CEC's EEPROM, so uBITX CEC Desktop's CW tab (key type, speed, sidetone,
  delays) keeps controlling the keying.

### Not chosen: a dedicated keyer chip

PIC-based keyer chips such as K1EL's **K16** (a standalone keyer with a speed
pot and a key output) or the **WinKeyer** (WK3 family, with a serial host
interface for logging programs) are proven and have memories. The chip would
take the paddles and give one open-collector "key down" line, read by the Pico
as a straight key.

Drawbacks: an extra part and board space, and **the firmware and the app no
longer control the keyer**. Speed would come from the chip's pot, and the CW
tab's speed and key type would silently do nothing. WinKeyer could be driven
over its serial link, but that's a whole extra interface for the app.

**Option:** leave an unpopulated footprint for a K16-style chip, so a builder
who wants a hardware keyer can fit one.

## Power and SWR input

### Connector

4-pin JST-XH:

1. **FWD**: forward voltage from the detector, to A0 (GP26)
2. **REF**: reflected voltage, to A2 (GP28)
3. **GND**
4. **+5 V or +3.3 V** for an active detector (a log detector such as the
   AD8307 needs power; a diode bridge doesn't)

### Protecting the ADC inputs, on each line

- **Scale:** a resistor divider, so that full power plus margin for a high SWR
  stays under about 3.0 V. Set it for the detector chosen.
- **Clamp:** about 1 kΩ in series, then Schottky diodes to 3.3 V and to ground,
  or a 3.3 V TVS.
- **Filter:** about 10 nF to ground at the pin. With the series resistor it
  makes an RC low-pass that smooths RF and keying noise, and gives the ADC a
  low-impedance source.

### The detector

Fitted on the RF side at the antenna output, joined to the board with a short
shielded lead.

- **Diode tandem match or Stockton bridge:** the classic. Cheap, no power
  needed. Non-linear at low power (the diode drop), so it reads poorly below
  about a watt. Acceptable at the uBITX's power, with a calibration curve in
  the firmware.
- **Log detector (AD8307), one per direction:** accurate over a wide range,
  low power included, but needs power and costs more.

### Firmware

- Read FWD and REF only while transmitting.
- Average them, or hold the peak for SSB and CW, since speech and keying jump
  around a lot.
- SWR from the ratio. Power needs a calibration factor, or a small table for a
  diode detector.
- Report both to the host as KD8CEC does, so the app's meter can show them.

### uBITX CEC Desktop

The app already has the matching settings: **Machine settings has a PWR/SWR
switch and PWR and SWR factors**, greyed out until a board reports power. The
meter's PWR/SWR half is drawn and empty, waiting for this.

## Already on Rev 6A, for reference

- **Opto-isolated, open-collector PTT/TX output.** Planned use: switching an
  antenna relay that protects an SDR on the same antenna while the uBITX
  transmits. The relay leads the RF by construction and works with no computer
  attached, which is better than anything the app can do over USB. The
  standard Raduino has no PTT output, which is why the app's help points
  owners of standard radios to RF-sensing T/R switches.
- **Needs KD8CEC 2.0** (the Pico builds in KD8CEC-V2.0-for-uBITX). uBITX CEC
  Desktop's help covers only KD8CEC 1.2 on the Nano so far; this board will
  need its own section there.

## Open items

- Choose the detector (diode bridge or AD8307) and work out the divider for it.
- Decide what happens to the original key jack: disconnected, or a legacy
  straight-key input on A0.
- Choose the connector types and positions on the board; the panel position of
  the new key jack.
- Firmware: `USE_DIGITAL_PADDLE`; PWR/SWR reading and reporting; calibration.
- Optional: a footprint for a K16-style keyer chip.
- uBITX CEC Desktop: enable the PWR/SWR meter and settings when the firmware
  reports power; a help section for the Pico board and KD8CEC 2.0.
