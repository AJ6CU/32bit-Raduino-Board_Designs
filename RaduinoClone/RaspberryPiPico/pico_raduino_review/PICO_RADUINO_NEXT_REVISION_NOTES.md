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
| A2 (GP28) | free in `ubitx.h`, but **wired to FBUTTON on Rev 10** (Pico pin 34); move the F button to a free GPIO (GP10–13) to use A2 |
| GP29 | not usable on a Pico or Pico 2: wired inside to measure the supply (VSYS/3) |

The encoder and PTT are already digital. On the Rev 10 board, GP10–GP13 (Pico pins 14–17) are unused: a good home for the paddles and the F button (see PICO_RADUINO_LAYOUT_REVIEW.md).

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

## Clock section (from the layout review)

See `PICO_RADUINO_LAYOUT_REVIEW.md`. In short:

- Move the Si5351 next to P3, with short clock traces on top copper (`rev10_proposed_placement.png`).
- Give the Si5351 its own LDO.
- Add series-resistor footprints on the clock outputs.
- Option: an Si5351 module (Adafruit/QRP Labs), or board-house assembly, to avoid soldering the MSOP-10 chip.

## Through-hole build (idea, November 2026)

Aim: make the board solderable by hand, with no fine-pitch SMD parts.

| Part | Now | Through-hole |
| :--- | :--- | :--- |
| U4 EEPROM | CAT24C256, SOIC-8 | a DIP-8 version with the same pinout (CAT24C256 in PDIP-8, or 24LC256-I/P). Check stock. |
| U6 opto | LTV-817S, SMD-4 | LTV-817, DIP-4 (same part, the S is the SMD version) |
| U2 Si5351 | MSOP-10 | no DIP exists: a module (see the clock section), or board-house assembly |
| R, C | 1206 SMD | axial or radial, or keep 1206: it is hand-solderable, and combo footprints like R6's allow either |
| U1, Pico, connectors | already through-hole | -- |

### Dropping the on-board S-meter (use the SDR's instead)

The "Optional Onboard S-Meter" block can be left off: **U3 (LM358), D1, C3, R1, R2 and P7 (VolHi input)**. That's six parts, including the LM358 that clips on 3.3 V.

- **Keep the SMeter-In line from P1-1 to A1 (GP27).** An external S-meter board can still use it.
- **Or take A1 for the PWR/SWR input instead.** With the keyer on digital pins, that gives A0 = forward, A1 = reflected, and the F button can stay on GP28.
- **Without an SDR, the radio has no S-meter.** That affects the Nextion/LCD and the CAT report. Fine if the SDR is always part of the station.
- **The app needs to read the S-meter from the SDR.** Check whether uBITX CEC Desktop's meter can take the SDR's level (rigctl `l STRENGTH`, or SDRangel's channel power). If it can't yet, that's a change in the app.
- **The SDR's reading is not the uBITX receiver's.** It's measured at the SDR's own input, after the T/R switch. It reads the same antenna, but with a different calibration.
- Options: remove the footprints, or keep them and leave them unfitted.

### Dropping the LCD connector (Nextion or the app only)

If the only displays are a Nextion (P5) or uBITX CEC Desktop, **J1 (the 14-pin TFT connector), R4 (22 Ω backlight), and possibly C9/C10/C11** can go.

**What it gains:**

- **Six GPIOs freed:** GP8 (D/C), GP9 (touch), and GP16–19 (the SPI bus).
  - That's room for the digital paddles and the F button.
  - Taken with the S-meter block gone, the ADC plan becomes clean.
- **The longest switching traces leave the board.** Each SPI line runs about 65–75 mm across the board. Removing them also clears space for the new Si5351 placement.
- **Less load on the Pico's 3.3 V regulator.** The TFT's backlight runs through R4 from +3.3 V, the same rail as the Si5351. It's quieter without it.

**Before deciding, check:**

- **The front panel.** The stock uBITX V6 has the 2.8" TFT in its cutout. Without J1, V6 owners must fit a Nextion, and probably need a new panel or bezel. Alternatively, offer it as a build option: footprint kept, connector not fitted.
- **Standalone use.** With no Nextion, the radio has no display without a computer.
- **Nextion and the app at the same time.** See the next section.
- **C9–C11.** These also decouple the Pico's 3.3 V output. Keep a 10 µF and a 0.1 µF somewhere on +3.3 V.

### Two displays at once: a Nextion and the app

**What KD8CEC does today.** KD8CEC's blog post "How to use Multi Nextion LCD (TJC LCD) with uBITX" (July 2018, firmware 1.095) covers this:

- The displays are simply **wired in parallel** on the one serial line.
- **All of them are live.** A touch on one shows up on the others, and each can run a different screen layout.
- There's an "Other LCD Off/On" control.
- He warns not to connect a display's TX line if there's noise or a long wire. In that case, that display shows only.

**What KD8CEC 2.0 does on the Pico.** The Nextion protocol goes to one port only: `Serial1`, which is UART0 on GP0/1, the P5 connector (`ubitx_lcd_nextion.ino`). CAT goes to `Serial`, the Pico's USB. uBITX CEC Desktop speaks the Nextion protocol, so on this board it plugs in where a Nextion would: a USB-TTL adapter on P5.

**So the app and a Nextion can share P5 the way KD8CEC shares two Nextions.** The catches:

- **Two TX outputs tied together fight each other.** Each one drives the line high while idle, and the other pulls it low to send. It worked for KD8CEC with short wires, but the clean way is to diode-OR them: a Schottky in series with each TX, cathode towards the TX pin, and a pull-up (about 10 kΩ) to 3.3 V on the Pico's RX.
- **Both must run at the same baud rate.** The app uses 57600, so set the Nextion to match.
- **If both send at the same moment, one command is garbled.** That's rare, and the next poll recovers, but it can happen.

**Better on the Pico: a second UART.**

- **GP8/GP9 are the RP2040's UART1** (TX/RX). They're the pins freed by removing the LCD connector.
- **Board:** add a 3- or 4-pin header on GP8/9 for the app's USB-TTL adapter, beside P5.
- **Firmware:** a small change to KD8CEC 2.0. Send each display message to both `Serial1` and `Serial2`, and take commands from either.
- **What it gains:** no tied TX lines, no diodes, and each side can run its own baud rate. Unplugging either side doesn't disturb the other.

### The app's connection on the board (no loose USB-TTL wires)

**A. A CP2102 module plugged into the board.** Fit a female header on UART1 (GP8/9) and plug in a common CP2102 USB-TTL module. A USB cable then goes to the panel.

- **Connect GND, TXD and RXD only.** Leave the module's 5 V and 3.3 V pins unconnected, or the computer's USB powers the radio. That's the same back-feed as the VSYS point in the review.
- **The logic levels suit the Pico.** The CP2102 drives 3.3 V.
- **Add about 1 kΩ in series on the module's TXD.** With the radio off and the computer on, an idle-high TXD would otherwise feed the Pico through its input protection.
- **Ground loop.** USB ties the computer's ground to the radio's, as the loose adapter does today. A digital isolator (ISO7721 or similar) between the module and the Pico would break it, as an option.
- **Mechanics.** A module on a header adds height. Reach the panel with a panel-mount USB extension.

**B. The Pico's own USB (no extra parts).** The Pico already has a USB port. KD8CEC 2.0 uses it for CAT, as `Serial`.

- **Firmware option 1:** a build option that puts the Nextion protocol on USB instead of CAT. Simple, but CAT programs (WSJT-X etc.) lose the port, unless the app passes CAT through.
- **Firmware option 2:** two USB serial ports on one cable, using TinyUSB's multiple CDC. One port carries CAT, the other the Nextion protocol for the app. The computer sees two serial ports. This needs the Adafruit TinyUSB stack in the arduino-pico build, which is more firmware work.
- **Board:** nothing new, just a panel-mount USB extension from the Pico's micro-USB. The USB back-feed point (VSYS Schottky) applies here too.

**Suggestion:** B with two serial ports is the neatest in the end, with one cable and no extra parts. A works with today's firmware plus the mirroring change, so it's a good first step.

## SDR T/R board at the antenna jack (idea, November 2026)

**Setup:** receive on the SDR only (not listening through the uBITX), with the board's opto PTT output (P4) available.

### What it is

A small board inside the case, at the rear-panel antenna BNC. The coax from the BNC to the main board is cut into, so the path becomes: BNC → T/R board → main board ANT.

- A relay switches the antenna between the uBITX (on transmit) and an **SDR port**: an SMA/BNC bulkhead next to the antenna jack.
- **Control:** a 3-wire cable from P4 (Ext Dev V+, TX Trigger, GND). That is what P4 was designed for. A small N-MOSFET on the T/R board drives the relay coil, with a flyback diode.

### Fail-safe sense

The relay should be **energised for receive** and released for transmit.

- **Released (no power, cable unplugged, firmware crash, transmit):** antenna → uBITX, and the SDR port shorted to ground (through about 50 Ω).
- **Energised (receive):** antenna → SDR.
- **With J2 on DIR:** the opto is off on receive, so TX Trigger is pulled high, which turns the MOSFET on and energises the relay. On transmit the opto pulls TX Trigger low and the relay releases.
- A relay releases faster than it pulls in, so it drops out quickly at the start of transmit. Any failure leaves the SDR protected.

### SDR protection, in layers

1. **A DPDT relay.** One pole switches the antenna. The other pole grounds the SDR port whenever the antenna goes to the uBITX. Choose a small signal relay rated for RF, with stated isolation at 30 MHz.
2. **A limiter at the SDR port.** A series resistor, then anti-parallel small-signal or Schottky diodes to ground, to clip whatever leaks or hot-switches.
3. **Timing.** Transmit RF must start only after the relay has released. Check how KD8CEC sequences T/R against the start of RF, especially CW's first dit. If needed, add a short "T/R then RF" delay in firmware (a few ms).

### Noise: why the SDR still dangles, and options

The uBITX main board, the Si5351 harmonics and the digital lines make the inside of the case noisy.

- **SDR outside, but fixed in place:** bolt the dongle (the metal-cased RTL-SDR Blog V4) to the rear panel with a bracket or clip. Join it to the SDR port with a right-angle SMA adapter, or a 10 cm coax. Only the USB cable leaves.
- **SDR inside, shielded:** the dongle in its own small metal box. Bond the box to the chassis at the SDR port, put ferrites on the USB, and run the USB out through a panel-mount connector. **Measure first:** compare the noise floor with the SDR port terminated, dongle inside versus outside, at several bands.
- **The T/R board itself:** keep it small and in a metal can if possible. Keep its coil wiring away from the RF path.

### Is the SDR outside the case, near the antenna jack, too noisy or risky?

Assessed November 2026. **Probably not.**

**Receive noise.** Outside is the quieter place.

- A metal case keeps most of the main board's and the Si5351's radiation in. Outside, the dongle hears mainly its antenna input and whatever rides in on its USB cable.
- On receive, the relay **disconnects the uBITX from the antenna**. That also keeps the uBITX's LO leakage (the first LO, 45–75 MHz, comes back out of a receiver's antenna port) off the antenna and away from the SDR. That's an improvement.
- **The weak spot:** the few cm of SDR path inside the case, through the T/R board. Keep it short, in coax, and shielded.

**Transmit risk.** Small.

- 10 W in good coax with tight connectors stays inside the cable. The SDR is protected by the released relay, its grounded port and the limiter.
- **The real risk is common-mode RF**, which runs down the outside of the coax with an unbalanced or poorly matched antenna. It gets onto the chassis and the USB cable, causing USB dropouts, a frozen SDR or a misbehaving computer.
- **The cure:** clip-on ferrites on the USB cable at both ends, and a feedline choke if needed.
- **Not USB isolators.** The cheap ones (ADuM4160) are full-speed only, 12 Mbps, and an RTL-SDR needs USB 2.0 high speed.

**First-time test:**

1. Transmit into a dummy load with a 20–30 dB attenuator in front of the dongle. Watch the SDR during transmit: the leakage should be visible, nothing near overload, and no USB dropouts.
2. Remove the attenuator and repeat.
3. Repeat on the real antenna on each band. Dropouts on one band, but not on the dummy load, mean the antenna system needs choking.
4. On receive, compare the noise floor with the SDR port terminated, with the uBITX powered and unpowered. A rise means the path through the T/R board needs better shielding.

## Future directions: protocols (discussion, November 2026)

### Between the radio and the app

- **Today:** the Nextion protocol. It pushes changes, covers the front panel's features and leaves CAT free. Its weaknesses: it's undocumented, has no checksums, and runs over software serial on the Nano. Keep it for both boards for now. The Nano's KD8CEC 1.2 will never change, so the app keeps this support regardless.
- **KD8CEC's CAT today** is a Yaesu FT-817 emulation, plus KD8CEC's EEPROM read/write extension that the Settings Editor uses (`cat_libs.ino`). It uses fixed 5-byte binary commands, and the computer has to ask for everything. It's a poor base to extend.
- **Later, on the Pico only:** a Kenwood/Elecraft-style ASCII CAT, such as `FA00014074000;`, with **auto-information** so changes are pushed, plus vendor-prefixed KD8CEC extensions (CW settings, EEPROM, PWR/SWR). It's standard (Hamlib, loggers, digital-mode programs), extensible and readable. The Pico has the room the Nano didn't.

### TCI

- **Not on the board.** TCI is WebSocket over a network, so it would need a Pico W or a network chip. Its strength is audio and IQ streaming, which the Raduino doesn't have. Fewer programs speak it than the Kenwood protocol.
- **In the app, yes, possibly.** The app could publish the combined uBITX + SDR station as one rig, over rigctld and optionally TCI. Control would come from the uBITX through the app, and audio/spectrum from the SDR, which Brown already serves over TCI.

### The app as the station's hub

Only one program can open a serial port. If the radio speaks a standard CAT, the app owns the port and offers a rigctld-style network port, and optionally TCI, to WSJT-X and loggers. This also makes the second UART and the composite USB unnecessary in the long run.

## Future direction: native FT8 and digital modes

**Goal:** one USB cable gives the computer a serial port and a sound card, like modern rigs. No external sound card, and a clean digital transmit signal.

### Receive

- **Tap the uBITX's receive audio** at a fixed level, ahead of the volume control and audio amplifier. Bring it to the Raduino on a new connector.
- **Digitise it.**
  - The Pico's ADC is about 9 effective bits, roughly 50 dB of range. Usable for a first try, but marginal next to strong signals.
  - Better: an I2S ADC such as the PCM1808 (24-bit). Modules exist, which suits the through-hole plan. It needs 3–4 GPIOs, driven by PIO; the GPIOs freed by dropping the LCD connector will do.
- **USB:** a composite device with a CDC serial port plus a USB Audio Class microphone, using TinyUSB. The computer sees a "uBITX" sound card.

### Transmit: the QRP Labs QDX method, no DAC and no SSB modulator

- The computer sends the transmit audio over USB.
- The firmware measures the tone's frequency (zero crossings in the samples).
- The firmware sets the **Si5351 directly** to the carrier plus that offset, and keys the **CW transmit path**. The radio sends a pure carrier that follows the tones: 8-FSK for FT8.
- **Why:** no unwanted sideband, no audio-level or ALC problems, and no intermodulation from overdriving the audio. The spectrum is as clean as CW.
- **KD8CEC already does this for WSPR** (`ubitx_wspr.ino`: Si5351 tone shifting on the CW path). The same machinery serves FT8, FT4, JS8 and so on, since the computer chooses the tones.
- **PTT:** by CAT, or "audio present = transmit", as the QDX does.

### What it takes

- **Board:**
  - a receive-audio input connector and the ADC (an I2S module), with level setting, filtering and a clean 3.3 V supply;
  - nothing extra for transmit.
- **Firmware:**
  - TinyUSB composite (CDC plus UAC) in the arduino-pico build;
  - PIO I2S capture;
  - a sample-rate match to USB;
  - tone measurement;
  - Si5351 FSK on the CW path;
  - a "DIGI" mode.
- **uBITX side:** find the best receive-audio tap on the V6 main board. Check whether the CW path's carrier level and keying suit long transmissions (FT8 transmits for about 13 s per cycle). Mind the PA's heat at full duty.

### Today, with no new hardware

An external USB sound card (CM108-type dongle or SignaLink) on the speaker and mic jacks, plus PTT over CAT. It works with any uBITX, but transmit goes through the SSB modulator, so keep the audio low to avoid splatter.

### Receive on the SDR instead (Mark's idea, November 2026)

The SDR is already on the same antenna through the T/R switch, and the app already keeps it on the uBITX's frequency. Let it do the receiving.

- **With WSJT-X:**
  - Route the SDR program's audio output into WSJT-X through a virtual audio cable (BlackHole on the Mac, VB-Cable on Windows, a PulseAudio/PipeWire null sink on Linux).
  - WSJT-X's transmit audio goes to the radio.
  - **The board then needs no ADC and no receive-audio tap.** Its USB only has to be a sound-card output for transmit (QDX method). That's a much smaller job.
- **With the SDR's own decoder** (SDRoxide decodes FT8): fine for watching the band. To transmit, something still has to send tones. Possibilities:
  - WSJT-X for transmit;
  - later, the app encoding the FT8 message itself and sending the 79 tone numbers and the start time over serial, as KD8CEC's WSPR does with messages prepared by the uBITX Manager. That needs no audio at all, but the app would then be doing WSJT-X's QSO sequencing, which is a big job.

**Points to watch:**

- **Frequency accuracy.** The SDR's error shows up as an offset between where you hear and where you transmit. An RTL-SDR V3/V4 with a TCXO is within a couple of ppm (about 30 Hz at 14 MHz). FT8 tolerates that, but the planned WWV calibration in the app makes it tidy.
- **Delay.** The SDR's buffering adds a little delay to the audio. WSJT-X shows it as DT. Keep it well under a second.
- **The receiver needs the SDR running.** FT8 needs the SDR running, so there's no FT8 from the radio and computer alone.
- **The receiver is probably better:** fewer birdies than the uBITX's own receiver.

**Staged plan:**

1. **Now, no new hardware:** SDR audio into WSJT-X for receive. Transmit through a USB sound-card dongle on the mic jack (SSB, low level), with PTT over CAT.
2. **Next board:** USB sound-card output plus QDX-style FSK on the CW path. Transmit becomes clean and the dongle goes. The receive ADC is optional, for use without an SDR.
3. **Later, maybe:** FT8 transmit driven by the app, sending tone numbers over serial with no audio.

### Not suggested

Decoding FT8 on the Raduino itself. The RP2040 has no FPU and little RAM, and the computer already does it well.

## Making it fit the V3/V4/V5 Raduino as well (V11 planning)

The repo has two Pico boards: `uBitxV6Specific` (Rev 6.A and Rev 10-Optic) and `uBitxV3456` (Rev 6.A, the V3–V6 layout). The README notes there's no Rev 10 version of the V3456 board yet.

### What differs on the V3456 board (Rev 6.A)

- **2 layers.** It has a 16-pin **16x2 character LCD** header (P2) with a contrast pot (RV1), plus separate I2C (P6), SPI (P8) and PTT (P9) connectors.
- On V3–V5 radios, **the 16x2 LCD sits piggyback on the Raduino** and is the front-panel display. So "no LCD connector" isn't an option there in the same way it is on the V6.
- **Clocks:** U2 sits about 16 mm above P3, which is better than the V6 board. CLK1 and CLK2 run side by side for 8.8 mm at 0.55 mm, on 2 layers. Moving the Si5351 next to P3 helps here too.
- **P1 (controls) and P3 (the 18-pin oscillator header)** are the same parts as on the V6 board.

### Suggested approach: one core, two outlines

- **One schematic core** shared by both boards, as a hierarchical sheet in KiCad:
  - the Pico, the Si5351 module and its LDO, the EEPROM;
  - D2, the USB arrangement, the paddle and PWR/SWR inputs with their protection;
  - the opto T/R output, the Nextion socket, the AUX UART.
- **Two PCB files with the outlines and connector positions of each radio.** The same placement rule on both: **the Si5351 module directly above P3 pins 8–14**, clocks on top copper, about 10 mm.
- **4 layers on both** if the cost is acceptable. The ground plane is the biggest single improvement.

### V3/V4/V5-specific points

- **Display:**
  - Keep the 16x2.
  - Better: use a **16x2 with an I2C backpack** on the I2C header (KD8CEC display type "16x2 I2C"). That drops the 16-pin parallel header, RV1 and six GPIO lines.
  - **Watch the levels:** PCF8574 backpacks usually pull SDA/SCL up to 5 V. Use a 3.3 V-compatible backpack, or a level shifter, as with the Si5351 module.
  - Nextion and the app work as on the V6.
- **Height:** the LCD sits over the Raduino on standoffs. The Si5351 module on headers may hit the LCD. Options:
  - mount the module flat on a right-angle header;
  - put it on the back of the board;
  - choose a low-profile module.
  - Measure the gap first.
- **Firmware:** `UBITX_BOARD_VERSION` (4 for V3/V4, 5 for V5/V6) and the pin map stay firmware choices. The core design doesn't change.

## Open items

- Choose the detector (diode bridge or AD8307) and work out the divider for it.
- Decide what happens to the original key jack: disconnected, or a legacy
  straight-key input on A0.
- Choose the connector types and positions on the board; the panel position of
  the new key jack.
- Firmware: `USE_DIGITAL_PADDLE`; PWR/SWR reading and reporting; calibration.
- Optional: a footprint for a K16-style keyer chip.
- LCD connector: remove, or keep as a build option; the V6 front panel; Nextion and app at once: a second-UART header on GP8/9 plus a firmware change to mirror the Nextion protocol, or the diode-OR on P5.
- App connection: a CP2102 module on UART1, or the Pico USB with two serial ports (TinyUSB); the back-feed and ground-loop precautions.
- Protocols: Kenwood-style CAT with auto-information on the Pico (later); the app as hub with rigctld and maybe TCI.
- FT8: receive on the SDR (virtual audio cable) makes the board ADC optional; the receive-audio tap point on the V6; the ADC choice (Pico ADC vs PCM1808); TinyUSB composite; QDX-style FSK on the CW path; PA duty cycle.
- SDR T/R board at the antenna jack: relay type and isolation, limiter, fail-safe polarity (J2 DIR), KD8CEC T/R-to-RF timing, SDR mounting/noise test.
- V11 for both radios: shared schematic core, two PCB outlines; V3–V5 display (16x2 I2C backpack at 3.3 V?) and module height under the piggyback LCD.
- Through-hole build: check the DIP EEPROM and LTV-817 stock; decide on the S-meter block (remove, or leave unfitted); the app S-meter from the SDR.
- Clock section: chip, module, or both footprints; board-house assembly; display clearance for a module.
- uBITX CEC Desktop: enable the PWR/SWR meter and settings when the firmware
  reports power; a help section for the Pico board and KD8CEC 2.0.
