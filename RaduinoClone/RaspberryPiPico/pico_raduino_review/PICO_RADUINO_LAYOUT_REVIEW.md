# Pico Raduino (uBITX V6): schematic and layout review

Reviewed in November 2026 from `RaduinoClone/RaspberryPiPico/uBitxV6Specific` on the `Rev6A` branch. Two boards are covered:

- **Rev 10-Optic**: 4 layers. Top, a ground plane (In1), a +3.3 V plane (In2), and bottom.
- **Rev 6.A**: 2 layers, with ground pours on both sides.

**How this was done:** I parsed the `.kicad_pcb` files with a script. It lists, for every trace segment, which nearby segments of other nets run parallel to it, how long they overlap and the gap between them. I also checked the ground plane under each clock trace and read the schematic PDF. Nothing was measured on a real board.

Pictures (clock traces in colour; solid lines are top copper, dotted lines bottom copper):

- `rev10_clock_routing.png`
- `rev6a_clock_routing.png`

## The short answer

Your worry is justified, and it is mostly about one thing: **the three Si5351 clocks travel 40–50 mm from U2 to the oscillator header P3, and part of the way they run side by side.** Where the Si5351 sits is the root cause. Moving it next to P3 fixes most of what follows at once.

Rev 10's 4-layer stackup is already a big improvement over Rev 6.A, roughly 10–40 times less coupling for the same traces. Rev 10 still has three runs that are worth fixing.

## What the clocks are

In KD8CEC, on the uBITX V5/V6:

- **CLK2** is the first LO (VFO), around 45–75 MHz.
- **CLK1** is the second LO, around 33 or 57 MHz.
- **CLK0** is the BFO, around 11–12 MHz.

They are square waves, so their energy reaches several hundred MHz in harmonics.

A little of one LO getting into another LO's line means each mixer sees two LOs. The result is birdies at the sums and differences, which move as you tune. The Si5351 itself only isolates its outputs to around −50 to −60 dB, so the board should not make that any worse.

## Rev 10-Optic: findings

### 1. CLK1 and CLK2 side by side for 20 mm (main issue)

Down the left edge, the second-LO trace (to P3-11) and the VFO trace (to P3-14) run in parallel for **20 mm, 0.35 mm apart**. These two are the worst pair to couple, because they feed the two mixers of the same conversion chain.

### 2. CLK1 next to the 12 V input for 10 mm

The raw 12 V line (P3-15/16 to the 7805) runs **0.16 mm** from CLK1 for 10.5 mm, and crosses both CLK1 and CLK2. This puts the LO onto the radio's 12 V wiring. It also brings anything on the 12 V line (PA current, keying transients) next to the LO.

### 3. CLK0 next to PTT for 12 mm

The BFO trace (to P3-8) runs alongside PTT for **11.7 mm, 0.41 mm apart**. PTT goes out through P1 to the front-panel harness and the mic jack. That cable can carry the BFO and its harmonics out of the box. It can also bring RF back in on transmit, which is the usual cause of "PTT chatter".

### 4. Each clock changes layers twice, with no ground via nearby

Each clock goes top → bottom → top to cross other traces. That is two vias per clock.

- On the top layer, a trace's return current flows in the ground plane (In1) directly underneath it.
- On the bottom layer, the plane underneath is **+3.3 V** (In2), so the return current has to move from one plane to the other at every via.
- The nearest place it can do that is a decoupling capacitor, and the nearest ground via is **5–17 mm** away (CLK2's vias: 16–17 mm).
- So the return current takes a long detour around a loop. That loop radiates and picks up noise, and it undoes much of the 4-layer benefit for those stretches.

### 5. What is fine

- **The planes are unbroken under every clock trace**, apart from the normal clearance holes around vias. There are no slots and no splits.
- At P3, ground pins (7, 9–10, 12–13) sit between the clock pins (8, 11, 14), matching the main board.
- The crystal is close to U2. Its traces are short, 4.4 mm.
- The UART (GPIO0/1) runs 1.7–2.4 mm from the clocks. That is acceptable.

### How much it matters, roughly

This uses the rule of thumb from Howard Johnson: the coupling between two traces over a plane goes as 1 / (1 + (D/H)²), where:

- D is the distance between the trace centres;
- H is the height of the trace above the plane.

These figures are ballpark, for comparing layouts, not predictions.

| Case | H | CLK1/CLK2 today (0.35 mm gap) | With a 3 mm gap |
| :--- | :--- | :--- | :--- |
| Rev 10, 0.1 mm prepreg (as set in KiCad) | 0.1 mm | about −35 dB | about −61 dB |
| Rev 10, about 0.2 mm prepreg (a common default 4-layer stackup) | 0.21 mm | about −22 dB | about −48 dB |
| Rev 6.A, 2-layer, plane on the far side | about 1.5 mm | essentially uncontrolled | about −16 dB |

Two things follow:

- **Spacing is the cheapest fix.** Three times the gap gives 25 dB or more.
- **Order the thin-prepreg stackup.** KiCad's stackup assumes 0.1 mm prepreg, but the board house builds its own. At JLCPCB, for example, 1.6 mm 4-layer comes with about 0.2 mm (7628) or about 0.1 mm (3313) prepreg. Pick the thin one, or set the real value in KiCad so the numbers mean something.

## Rev 6.A: findings

Rev 6.A has the same routing as Rev 10, but on 2 layers, so each problem is worse:

- **CLK2 runs alongside PTT for 26 mm, 0.27 mm apart.** This is the worst pair on either board.
- CLK1 and CLK2 run together for 22 mm, 0.34 mm apart.
- CLK1 runs alongside PTT for 20 mm, about 1 mm apart.
- The only reference is the bottom ground pour, 1.5 mm away. Bottom-layer traces break it into 19 separate pieces.

If Rev 6.A is the board in use and it shows birdies that move with tuning, this is the likely reason. Rev 10 should be audibly better even before the fixes below.

## Recommended changes, most effective first

1. **Move U2 (Si5351), Y1 and C4–C6 to just above P3 pins 8–14.**
   - The clock runs then shrink from 40–50 mm to under 10 mm, entirely on the top layer over In1.
   - Fan the three traces out so they are separated rather than bundled.
   - Only I2C (two slow lines) then has to travel the board. It can tolerate distance and vias.
   - **This one move fixes findings 1–4.**
2. **If U2 can't move**, keep the clocks on the top layer all the way:
   - Space them at least 3 trace widths apart, ideally a ground trace between them stitched to In1 with vias every 5 mm or so.
   - Move the 12 V and PTT traces away from the clocks rather than alongside.
   - Where a clock must change layers, put a ground via within 1 mm of the signal via, and keep its bottom-layer run short. Better still, route the other trace under it instead.
3. **A series resistor footprint at each clock output, right at U2**, fitted with 0 Ω by default. Fitting 22–47 Ω later slows the edges, which cuts harmonics, crosstalk and radiation, at no cost to the board.
4. **Lower the Si5351 drive in firmware.** As I recall, KD8CEC sets all three outputs to 8 mA (`si5351bx_drive`). 4 mA or 6 mA is often enough for the uBITX mixers and gives softer edges. Test receive sensitivity and transmit power after the change.

## Schematic: other points

These are not crosstalk, but they matter for a quiet receiver.

1. **The Si5351 runs from the Pico's switching regulator.**
   - +3.3 V comes from the Pico's 3V3 pin, the output of its RT6150 buck-boost. At light load it runs in power-save mode, so its ripple varies in frequency.
   - On a clock chip, that ripple turns into spurs either side of every LO.
   - Fixes:
     - Give U2 its own low-noise LDO from +5 V Reg, for example an LP5907 or MCP1700, with a ferrite bead and 10 µF.
     - At least drive **GPIO23 high in firmware**. That forces the Pico's regulator into PWM mode, which the Pico datasheet recommends for lower ripple.
2. **USB back-feeds the radio.**
   - +5 V Reg goes straight to VSYS. When the radio is off and a USB cable is plugged in (for flashing, or the app), the Pico's VBUS diode powers VSYS. That in turn powers the +5 V Reg net, which includes the display, the controls and the 7805's output, all from the computer's USB port.
   - The Pico datasheet's answer is a Schottky diode, or a P-MOSFET ideal diode, between the external 5 V and VSYS.
3. **The LM358 on 3.3 V clips the S-meter.**
   - On a 3.3 V supply, the LM358's output and input range only reach about Vcc − 1.5 V, which is about 1.8 V. The S-meter tops out early and doesn't use the ADC's full range.
   - A rail-to-rail op-amp in the same SOIC-8 pinout fixes it, for example an MCP6002.
4. **ADC references.**
   - AGND (pin 33) and ADC_VREF (pin 35) are left unconnected. That works, because the Pico ties AGND to ground internally and feeds VREF from 3V3 through a filter.
   - Taking AGND to the ground plane is still worth doing.
   - For accurate PWR/SWR readings, consider an external reference on ADC_VREF (an LM4040 at 3.0 V).
5. **The opto output (P4) is not open-collector.**
   - R6 (10 kΩ) pulls TX Trigger up to Ext Dev V+, so P4 gives a logic level. That suits a T/R switch's control input.
   - It can't drive a relay coil. The LED runs at about 2 mA from the GPIO through R5, so at the LTV-817's CTR the transistor can only sink a few mA.
   - For an antenna relay (the SDR-protection case), add a small MOSFET or a ULN2003 channel. Alternatively, make R6 optional so P4 can be a true open collector driving a 2N7000 or similar near the relay.
   - The output is safe at power-up in both J2 settings: a GPIO that isn't driven leaves the LED off.
6. **The pin map affects the next-revision notes.**
   - On this board, **GP28 (A2) is FBUTTON**, not free.
   - GP10–GP13 (pins 14–17) are unused. They are the natural place for the digital paddles.
   - For reflected power on A2, move FBUTTON to one of GP10–13.

## Proposed placement (sketch)

`rev10_proposed_placement.png` shows where things could go on Rev 10. It's a guide for re-routing in KiCad, not a finished layout: part sizes are approximate.

- **U2 (Si5351)** sits about 10 mm above P3, between pins 14 and 8. **Y1** goes right beside it, to the left.
- **Each clock** runs straight down to its P3 pin on top copper, about 10–12 mm. That's a quarter of today's length, and the clocks no longer change layers.
- **The DC-blocking caps C4–C6** sit partway down each clock line, with the optional series-resistor footprint right beside each one.
- **Ground guard traces** run between the clocks, with a via every few mm down to the ground plane (In1). At the connector, P3's ground pins (7, 9, 10, 12, 13) already sit between the clock pins.
- **C1, C2 and the optional LDO** sit right at U2's supply pins.
- **Only SDA and SCL** have to cross the board to reach the Pico. They are slow, so vias don't matter for them.

**What has to move.** These nets have traces in the area to clear (pink in the picture):

- PTT
- Keyer
- GPIO0/1 (the UART)
- P3-6
- D17/CS

Only the **top-copper** ones have to go. On this 4-layer board, a bottom-copper trace under U2 is shielded from it by the two inner planes. So the long dotted UART runs and the bottom stretches of PTT can stay where they are. In practice, the top stretches of PTT, Keyer, P3-6 and D17/CS need re-routing around the area.

The old U2 position, near R13/R14, is freed up.

## Option: an Si5351 module instead of the chip

Added November 2026. **The problem:** the Si5351 (MSOP-10, 0.5 mm pitch) is the hardest part on the board for a builder to solder.

### What a module gives

The T41 SDR transceiver takes this route. Early builds put Adafruit's Si5351A breakout on the board. I haven't checked whether the current T41-EP RF board still does.

- **No fine-pitch soldering.** The chip becomes a row of header pins.
- **A known-good layout.** The module already has the crystal, the decoupling and its ground.
- **Its own regulator (Adafruit #2045).** It takes 5 V and makes its own 3.3 V, with level shifting on I2C. Fed from +5 V Reg, it no longer runs from the Pico's switching regulator. That fixes the "Si5351 runs from the Pico's switching regulator" point above.
- **Swap or upgrade later.** The QRP Labs Synth module, for example, takes an optional TCXO.

### What to watch

- **Placement still matters most.** Put the module where U2 sits in `rev10_proposed_placement.png`, just above P3. A module in the middle of the board with 40 mm clock runs is no better than today.
- **A ground pin beside each clock output.** On the Adafruit board, use each SMA footprint's own ground pads, not one shared ground pin on the header.
- **Height.** A module on headers adds about 10 mm. Check the clearance behind the uBITX display.
- **Crystal frequency.** KD8CEC assumes 25 MHz, as on the Adafruit board. I believe the QRP Labs module uses 27 MHz. If so, the firmware's crystal constant has to change, or every frequency will be off.
- **I2C pull-ups.** The module's pull-ups end up in parallel with R13/R14. That's harmless, but R13/R14 can be left unfitted.

### Other ways round the soldering

- **Board-house assembly.** JLCPCB and similar can fit just the SMD parts. Check that the Si5351A-B-GT is in their parts library and in stock. The single-board layout stays as it is.
- **Footprints for both.** Put the chip footprint and a module header at the same spot above P3, sharing the clock and I2C traces, and let the builder fit one or the other. The extra few mm of trace to the empty footprint don't matter at these frequencies.

### Suggested

Use board-house assembly for builders who order boards, plus the module footprint for builders who don't. Both fit the new placement near P3.

### Open questions

- Which module? Look at the Adafruit #2045, the QRP Labs Synth and the Etherkit/NT7S breakout. Compare their pinout, height and crystal frequency.
- Measure the clearance behind the display.
- Is the Si5351A-B-GT in stock at the chosen board house?
- Look at the current T41-EP RF board files to see how they mount and ground the module.

Sources:
- [AD5GH T41 board (Adafruit breakout)](https://ad5gh.wordpress.com/sdr-transceiver-qsd-qse-lo-teensy-4-1-dsp-audio-board/)
- [Adafruit #2045](https://www.adafruit.com/products/2045)
- [QRP Labs Synth](https://www.qrp-labs.com/images/synth/synth_assembly6.pdf)
- [NT7S breakout](https://nt7s.com/2014/06/si5351-libraries-and-breakout-board/)

## What I did not check

- I did not run KiCad's DRC or ERC; kicad-cli wasn't available here.
- Traces were judged as segments. Arcs, and the copper inside footprints, weren't included.
- I made no field-solver or SPICE model, and took no measurements on a built board. The dB figures above are rules of thumb.
- The main board's side of P3 (how the uBITX V6 routes the clocks onward) is not covered.
