import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
fig,ax=plt.subplots(figsize=(15,10))
def box(x0,y0,x1,y1,label,fc,ec='k',fs=8,ls='-',tc='k',z=3):
    ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=fc,ec=ec,ls=ls,lw=1.3,zorder=z))
    ax.text((x0+x1)/2,(y0+y1)/2,label,ha='center',va='center',fontsize=fs,color=tc,zorder=z+1)
def wire(pts,c,lw=2.2,ls='-',z=2):
    xs,ys=zip(*pts); ax.plot(xs,ys,ls,color=c,lw=lw,zorder=z,solid_capstyle='round')
# board
ax.add_patch(Rectangle((39.4,74.5),132.7-39.4,133.0-74.5,fc='#eef5ee',ec='k',lw=2,zorder=0))
for x,y in ((44.9,79.6),(122.1,79.4),(122.1,123.3),(44.9,123.3)):
    ax.add_patch(Circle((x,y),1.6,fc='white',ec='#666',zorder=1))
# Pico (bottom side)
box(70,85.4,121,106.4,'',  '#f0f0ff',ls='--',fs=9,z=1)
ax.text(80,101.5,'U5  Raspberry Pi Pico\n(bottom side, keep position)',ha='center',fontsize=9)
ax.add_patch(Rectangle((121,92.5),3.5,6.2,fc='#999',ec='k',zorder=3))
ax.annotate('micro-USB: ONE cable, TWO serial ports\n  COM a = CAT (WSJT-X, loggers)\n  COM b = Nextion protocol (uBITX CEC Desktop)\n-> panel-mount USB extension',xy=(124.5,95.6),xytext=(112.5,111.5),fontsize=8.5,
            arrowprops=dict(arrowstyle='->',lw=1.5),bbox=dict(fc='#fffbe6',ec='#b8860b'),zorder=6)
# removed J1
ax.add_patch(Rectangle((125.6,83.2),2.6,35.4,fc='none',ec='#c00',ls='--',zorder=2))
ax.plot([125.6,128.2],[83.2,118.6],color='#c00',lw=1); ax.plot([128.2,125.6],[83.2,118.6],color='#c00',lw=1)
ax.text(129.3,101,'J1 LCD\nremoved',color='#c00',fontsize=8,rotation=90,va='center')
# P3 header
for i in range(18):
    x=98.6-2.54*i
    ax.add_patch(Rectangle((x-0.9,127.1),1.8,1.8,fc='#ccc',ec='k',zorder=3))
    ax.text(x,130.2,str(i+1),ha='center',fontsize=6.5)
ax.text(77,132.2,'P3  to uBITX main board (unchanged)',ha='center',fontsize=8.5)
gnd=[7,9,10,12,13]
for g in gnd: ax.text(98.6-2.54*(g-1),126.2,'G',ha='center',fontsize=6.5,color='#555')
# Si5351 module
box(63.5,107.5,84.5,121.0,'A1  Adafruit Si5351A\n(#2045 or #5640)\nsize/pins: check part\n25 MHz xtal on module','#ffe08a',fs=8,z=3)
cols={'CLK0':('#d62728',8),'CLK1':('#1f77b4',11),'CLK2':('#2ca02c',14)}
for name,(c,pin) in cols.items():
    px=98.6-2.54*(pin-1); sx=px
    wire([(sx,121.0),(px,127.1)],c,lw=3)
    ax.add_patch(Rectangle((px-0.8,122.0),1.6,1.0,fc='white',ec=c,zorder=5)); ax.add_patch(Rectangle((px-0.8,124.1),1.6,1.0,fc='white',ec=c,zorder=5))
    ax.text(px+1.0,122.6,'R',fontsize=6,color=c); ax.text(px+1.0,124.7,'C',fontsize=6,color=c)
    ax.text(px,119.9,name,ha='center',fontsize=7,color=c,zorder=6,fontweight='bold')
for gx in (77.0,69.4):
    wire([(gx,121.0),(gx,126.6)],'#555',lw=1.2)
ax.text(86.0,124.5,'R = 0 Ω (22-47 Ω option)\nC = 0.1 µF DC block\nGND guard + vias between',fontsize=7)
# LDO
box(85.5,108.5,91,112.5,'U7 LDO\n3.3 V',  '#d0f0d0',fs=7)
wire([(91,110.5),(95,110.5),(95,114)],'#e67e22',lw=1.6)
ax.text(95.5,114.5,'+5V Reg',fontsize=7,color='#e67e22')
wire([(85.5,110.5),(84.5,110.5)],'#2e8b57',lw=2)
ax.text(85.6,107.6,'clean 3.3 V -> A1 Vin',fontsize=6.5,color='#2e8b57')
# I2C
wire([(70,111),(66,111),(66,104),(70,104)],'#8c564b',lw=1.6,ls='--')
ax.text(56.0,106.0,'SDA/SCL\n(GP20/21)\n+ EEPROM U4',fontsize=7,color='#8c564b')
# Nextion socket
box(40.8,93.0,47.0,101.0,'P5\nNextion\n4-pin XH','#cfe2ff',fs=7)
ax.text(47.6,93.2,'1 +5V\n2 GND\n3 TX  GP0\n4 RX  GP1',fontsize=6.5,va='top')
ax.text(41.0,103.6,'P2 (5 V to Nextion) can go:\npower now on P5',fontsize=6.5,color='#555')
# Paddle connector
box(104.4,76.0,110.9,80.5,'P8 PADDLE\n3-pin XH','#e8d5ff',fs=7)
ax.text(104.4,83.3,'1 DIT GP11 (pin15)\n2 DAH GP12 (pin16)\n3 GND\n1 kΩ + 1 nF + ESD each',fontsize=6.3,va='top')
# PWR/SWR
box(112.0,76.0,118.9,80.5,'P9 PWR/SWR\n4-pin XH','#ffd6d6',fs=7)
ax.text(112.2,83.3,'1 FWD -> A1 GP27\n2 REF -> A2 GP28\n3 GND\n4 +5V\ndivider+clamp+10 nF',fontsize=6.3,va='top')
# P1
for i in range(8):
    x=102.4-2.54*i; ax.add_patch(Rectangle((x-0.9,77.6),1.8,1.8,fc='#ccc',ec='k',zorder=3))
ax.text(93.5,75.6,'P1 Controls (unchanged pins): 1 SMeter-In (NC, JP1 opt.)  2 Keyer->A0  3 +5V  4 GND  5 PTT  6 FBUTTON->GP10  7/8 ENC',fontsize=6.5,ha='center')
# opto, J2, P4 unchanged
box(54,84,66,89,'U6 opto (TX out)\nunchanged','#eeeeee',fs=7)
box(52.8,77.3,61,80.7,'P4 TX/RX','#eeeeee',fs=7)
box(66.8,76.8,70.3,79.5,'J2','#eeeeee',fs=7)
# 7805 + Schottky
box(51.5,113.5,59.5,118.5,'U1 7805\n(unchanged)','#eeeeee',fs=7)
box(115.5,89.5,119,91.8,'D2','#ffcccc',fs=7)
ax.text(100.5,109.2,'D2 Schottky: +5V Reg -> VSYS\n(stops USB back-feeding the radio)',fontsize=6.5,color='#a00')
# EEPROM
box(108.2,93.5,113.2,99.5,'U4\nEEPROM\nDIP-8','#eeeeee',fs=7)
# removed S-meter block
box(94,90.5,103,97.0,'U3 S-meter\nblock\nremoved','none',ec='#c00',ls='--',tc='#c00',fs=7)
# AUX UART optional
box(40.8,108.0,46.5,113.0,'P10 AUX\nUART1\nGP8/9','#f5f5f5',fs=6.5,ls=':')
ax.text(47,113.5,'optional:\ndebug / 2nd\nNextion',fontsize=6.3,color='#555',va='top')
ax.set_xlim(37,135); ax.set_ylim(135,72.5); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Proposed Pico Raduino (next revision): Si5351 module, dual USB serial, Nextion socket, no LCD\nSKETCH - positions approximate, top view; existing parts kept where marked unchanged',fontsize=11)
plt.tight_layout(); plt.savefig('/tmp/claude-0/out/board_review/next_rev_proposed_layout.png',dpi=110)
