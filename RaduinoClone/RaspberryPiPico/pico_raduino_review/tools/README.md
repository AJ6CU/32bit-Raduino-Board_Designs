# Board-check scripts

These are the scripts behind PICO_RADUINO_LAYOUT_REVIEW.md. They need Python 3; plot.py, proposal.py and rev11.py also need matplotlib.

First parse a board into a .pkl file, then run the checks on that file:

    python3 pcb.py   "board.kicad_pcb" r10                 # lists layers, parts, zones and net lengths; writes r10.pkl
    python3 par.py   r10.pkl "Net-(P3-Pin_8),Net-(P3-Pin_11),Net-(P3-Pin_14)"  # traces running parallel to these nets
    python3 plane.py "board.kicad_pcb" "Net-(P3-Pin_8),..."  # is the reference plane under each trace? (4-layer boards)
    python3 pads.py  "board.kicad_pcb" U2 P3                # the net on each pad of the parts named
    python3 plot.py  r10.pkl out.png "Title"                # copper picture with the clock nets highlighted

Notes:

- The scripts use the folder layout of the session they came from: some paths start `tools/...` and are relative to the folder above this one.
- proposal.py and rev11.py made the two sketches. They are drawings, not checks.
- Net names change whenever the schematic changes, so check them with pads.py first.
