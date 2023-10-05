import numpy as np
from guizero import App, Box, Text, TextBox, PushButton, CheckBox
from time import sleep, time
from serial import Serial
from DevicesNovatic import *
import matplotlib.pyplot as plt

class DEV_box:
    def __init__(self, dev, index=0, name='', state=0, cb=None):
        self.dev = dev
        self.index = index
        self.name = name
        self.state = state
        self.cb = cb
    
    def get_state(self):
        return self.state
    
    def set_dev(self, dev):
        self.dev = dev
    
    def set_index(self, index):
        self.index = index
    
    def set_name(self, name):
        self.name = name
        
    def set_state(self, state):
        self.state = state
    
    def set_cb(self, cb):
        self.cb = cb
    
class TTL_box(DEV_box):
    def __init__(self, dev, index=0, name='', state=0, cb=None):
        super().__init__(dev, index, name, state, cb)
        if state:
            self.dev.turn_on()
        else:
            self.dev.turn_off()
            
class ELL_box(DEV_box):
    def __init__(self, dev, index=0, name='', state=0, cb=None, tb1=None, tb2=None, tb3=None,
                 txt=None, tb4=None, pb=None):
        super().__init__(dev, index, name, state, cb)
        self.tb1 = tb1
        self.tb2 = tb2
        self.tb3 = tb3
        self.txt = txt
        self.tb4 = tb4
        self.pb = pb
    
    def set_tb1(self, tb1):
        self.tb1 = tb1
        
    def set_tb2(self, tb2):
        self.tb2 = tb2
        
    def set_tb3(self, tb3):
        self.tb3 = tb3
    
    def set_txt(self, txt):
        self.txt = txt
        
    def set_tb4(self, tb4):
        self.tb4 = tb4
        
    def set_pb(self, pb):
        self.pb = pb
        
class ACQ_box(DEV_box):
    def __init__(self, dev, index=0, name='', state=0, cb=None, cb2=None, tb1=None, tb2=None, pb=None, data=None):
        super().__init__(dev, index, name, state, cb)
        self.tb1 = tb1
        self.tb2 = tb2
        self.pb = pb
        self.data = data
        self.cb2 = cb2
    
    def set_tb1(self, tb1):
        self.tb1 = tb1
        
    def set_tb2(self, tb2):
        self.tb2 = tb2
        
    def set_pb(self, pb):
        self.pb = pb
        
    def set_data(self, data):
        self.data = data
        
    def set_cb2(self, cb2):
        self.cb2 = cb2

#################
# Initilization #
#################
ACQs = []
#ACQs.append(ACQ_box(CD48('ttyACM0', 50, 2, 1, ['S01000','S10100','S21100','S30000','S40000','S50000','S60000','S70000']), 0, 'CD48'))

#ports_objects = list(find_ports.comports())
abacus = '/dev/ttyUSB_Tausand'
ACQs.append(ACQ_box(ABACUS(abacus)))
#data = ABCD.acquire_data()

TTLs = []
#TTLs.append(TTL_box(piTTL(11, True), 0, 'Laser'))  # Normally closed
TTLs.append(TTL_box(piTTL(37, True), 1, 'SPCM A'))   # Normally closed
TTLs.append(TTL_box(piTTL(29, True), 2, 'SPCM B'))   # Normally closed

for TTL in TTLs:
    TTL.set_state(0)

ELLs = []
#Rotations
#ell_rot_usb_port = '/dev/ttyUSB_ELL0'
#ell_rot_usb_port = '/dev/ttyUSB_ELL1'
#ell0 = Serial(port=ell_rot_usb_port, baudrate=9600, timeout=1)
#ELLs.append(ELL_box(ell_device(ell0, 1, 143360/360, -540, 540), 1, 'ROT 1'))
#ELLs.append(ELL_box(ell_device(ell0, 2, 143360/360, -540, 540), 2, 'ROT 2'))
#ELLs.append(ELL_box(ell_device(ell0, 3, 143360/360, -540, 540), 3, 'ROT 3'))

#Translations
#ell_trans_usb_port = '/dev/ttyUSB_ELL0'
#ell_trans_usb_port = '/dev/ttyUSB_ELL1'
#ell1 = Serial(port=ell_trans_usb_port, baudrate=9600, timeout=1)
#ELLs.append(ELL_box(ell_device(ell1, 0, 1024, 0, 28), 0, 'LIN 0'))
zaber_trans_usb_port = '/dev/tty...'
ser = Serial(port = zaber_trans_usb_port, baudrate = 9600, timeout = 1, stopbits = 1, bytesize = 8)
ELLs.append(ELL_box(zaber_device(ser, 0, 1024, 0, 28), 0, 'LIN 0'))

n = 0
for ELL in ELLs:
    while n == 0:
        try:
            ELL.dev.SetPos(ser, 0)
            n = 1
        except Exception as e:
            pass

#################
# GUI functions #
#################
def acquisition(ELL_List, START_List, STEP_List, NSTEP_List, Nrep, ACQtime, tausand, TTL_List):
    idcs = gen_nest_indices(NSTEP_List)
    Ndev = len(ELL_List)
    Nacq = len(idcs)
    #data = np.zeros([Nacq, Nrep, Ndev+8]) # CD48
    data = np.zeros([Nacq, Nrep, Ndev+3])  # Tausand
    positions = np.zeros(Ndev)
    for TTLn in TTL_List:
        TTLn.turn_on()
    for i in range(Nacq):
        for j, (dev, sv, ss) in enumerate(zip(ELL_List, START_List, STEP_List)):
            positions[j] = dev.goto(sv + idcs[i, j]*ss)
            sleep(2)
        acquired_data = tausand.acquire_data(Nrep, ACQtime)
        for j in range(Nrep):
            data[i,j,:Ndev] = positions
            #data[i,j,Ndev:] = acquired_data[j+1]
            data[i,j,Ndev:] = acquired_data[j]
    for TTLn in TTL_List:
        TTLn.turn_off()
    return data

def toggle_TTL_box(TTL_b):
    if TTL_b.cb.value:
        TTL_b.cb.text=f'{TTL_b.name} IN'
        TTL_b.cb.text_color = 'green'
        TTL_b.set_state(1)
    else:
        TTL_b.cb.text=f'{TTL_b.name} OUT'
        TTL_b.cb.text_color = 'red'
        TTL_b.set_state(0)       
        
def toggle_ELL_box(ELL_b):
    if ELL_b.cb.value:
        ELL_b.cb.text=f'{ELL_b.name} IN'
        ELL_b.cb.text_color = 'green'
        ELL_b.tb1.enable()
        ELL_b.tb2.enable()
        ELL_b.tb3.enable()
        ELL_b.set_state(1)
    else:
        ELL_b.cb.text=f'{ELL_b.name} OUT'
        ELL_b.cb.text_color = 'red'
        ELL_b.tb1.disable()
        ELL_b.tb2.disable()
        ELL_b.tb3.disable()
        ELL_b.set_state(0)
        
def goto_ELL(ELL_b):
    ELL_b.dev.goto(float(ELL_b.tb4.value))
    ELL_b.txt.value=f'{round(ELL_b.dev.GetPos(ser),2)}'
        
def toggle_ACQ_box(ACQ_b):
    if ACQ_b.cb.value:
        if app.yesno('ATTENTION','Lumieres eteintes?'):
            ACQ_b.cb.text=f'Lights OFF'
            ACQ_b.cb.text_color = 'green'
            ACQ_b.pb.enable()
        else:
            ACQ_b.cb.text=f'Lights ON'
            ACQ_b.cb.text_color = 'red'
            ACQ_b.pb.disable()
            ACQ_b.cb.value = 0
    else:
        ACQ_b.cb.text=f'Lights ON'
        ACQ_b.cb.text_color = 'red'
        ACQ_b.pb.disable()
        
def toggle_graph_box(ACQ_b):
    if ACQ_b.cb2.value:
        ACQ_b.cb2.text=f'Display Graph'
        ACQ_b.cb2.text_color = 'green'
        
def start_ACQ(ACQ_b, TTL_bs, ELL_bs):
    inTTLs = []
    for TTL_b in TTL_bs:
        if TTL_b.get_state():
            inTTLs.append(TTL_b.dev)
    inELLs = []
    inNAMEs = []
    inSTARTs = []
    inSTEPs = []
    inNSTEPs = []
    for ELL_b in ELL_bs:
        if ELL_b.get_state():
            inELLs.append(ELL_b.dev)
            inNAMEs.append(ELL_b.name)
            inSTARTs.append(float(ELL_b.tb1.value))
            inSTEPs.append(float(ELL_b.tb2.value))
            inNSTEPs.append(int(ELL_b.tb3.value))
    acqt = float(ACQ_b.tb1.value)
    nrep = int(ACQ_b.tb2.value)
    ACQdata = acquisition(inELLs, inSTARTs, inSTEPs, inNSTEPs, nrep, acqt, ACQ_b.dev, inTTLs)
#     print(ACQdata)
    ACQcsv = ACQdata.reshape((ACQdata.shape[0]*ACQdata.shape[1]),ACQdata.shape[2])
    ACQmean = ACQdata.mean(1)
    ACQstd = ACQdata.std(1)
    if ACQ_b.cb2.value:
        fig, ax = plt.subplots()
        lin_0 = ACQcsv[:, 0]
        Amean = ACQmean[:, 1]
        Astd = ACQstd[:, 1]
#         print('Astd = ', Astd)
        Bmean = ACQmean[:, 2]
        Bstd = ACQstd[:, 2]
        ABmean = ACQmean[:, 3]
        ABstd = ACQstd[:, 3]
        ax.plot(lin_0, Amean, label = 'A')
        ax.plot(lin_0, Bmean, label = 'B')
        ax.plot(lin_0, ABmean, label = 'AB')
#         ax.fill_between(lin_0, Amean-Astd, Amean+Astd)
#         ax.fill_between(lin_0, Bmean-Bstd, Bmean+Bstd)
#         ax.fill_between(lin_0, ABmean-ABstd, ABmean+ABstd)
        ax.legend()
        ax.set_xlabel('LIN 0')
        ax.set_ylabel('Count')
        ax.set_title(f'{MDt0.value}')
        fig.show()
        fig.savefig(f'/home/pi/Desktop/Novatic/Data/T_{int(time.time())}_{MDt0.value.replace(" ","").upper()}.png')
    ACQ_b.set_data(ACQdata)
    for ELL_b in ELL_bs:
        if ELL_b.get_state():
            ELL_b.txt.value=f'{round(ELL_b.dev.GetPos(ser),2)}'
    ACQ_b.cb.value = 0
    ACQ_b.cb.text=f'Lights ON'
    ACQ_b.cb.text_color = 'red'
    ACQ_b.pb.disable()
    path = f'/home/pi/Desktop/Novatic/Data/T_{int(time.time())}_{MDt0.value.replace(" ","").upper()}.csv'
    hdr = ''
    fmt = ''
    for inNAME in inNAMEs:
        hdr = hdr + inNAME + ','
        fmt = fmt + '%.2f,'
    hdr = hdr + 'A,B,AB'
    fmt = fmt + '%d,%d,%d'
    np.savetxt(path, ACQcsv, delimiter=',', header=hdr, comments=f'#{MDt1.value}\n', fmt=fmt)
    print(f'{np.around(ACQcsv.mean(0),1)}')
    print(f'{np.around(ACQcsv.std(0),1)}')
            
app = App(title='Novatic', width=750, height=350, layout='grid')

boxMD = Box(app, grid=[0,0], layout='grid', align='left', width='fill', height = 'fill')
boxTTL = Box(app, grid=[0,1], layout='grid', align='left', width='fill', height='fill')
boxA = Box(app, grid=[0,2], align='left', width='fill', height=40)
boxELL = Box(app, grid=[0,3], layout='grid', align='left', width='fill', height='fill')
boxB = Box(app, grid=[0,4], align='left', width='fill', height=40)
boxACQ = Box(app, grid=[0,5], layout='grid', align='left', width='fill', height= 'fill')

MDt0 = TextBox(boxMD, enabled=True, grid=[2,0], width=40)
MDt1 = TextBox(boxMD, enabled=True, grid=[2,1], width=40)
MDt2 = Text(boxMD, grid=[1,0], width=12, height = 2, text='Title', align = 'right')
MDt3 = Text(boxMD, grid=[1,1], width=12, height = 2, text='Comment', align = 'right')

for iTTL, TTL in enumerate(TTLs):
    TTL.set_index(iTTL)
    if TTL.get_state():
        inout = 'IN'
        col = 'green'
    else:
        inout = 'OUT'
        col = 'red'
    TTLcb = CheckBox(boxTTL, grid=[iTTL,0], width=12, command=toggle_TTL_box, args=[TTL])
    TTLcb.text = f'{TTL.name} {inout}'
    TTLcb.value = TTL.get_state()
    TTLcb.text_color = col
    TTL.set_cb(TTLcb)

ELLt0 = Text(boxELL, grid=[0,0], width=12, text='Device')
ELLtA = Text(boxELL, grid=[1,0], width=1, text='')
ELLt1 = Text(boxELL, grid=[2,0], width=8, text='Start')
ELLtB = Text(boxELL, grid=[3,0], width=1, text='')
ELLt2 = Text(boxELL, grid=[4,0], width=8, text='Step')
ELLtC = Text(boxELL, grid=[5,0], width=1, text='')
ELLt3 = Text(boxELL, grid=[6,0], width=8, text='N Steps')
ELLtD = Text(boxELL, grid=[7,0], width=2, text='')
ELLt4 = Text(boxELL, grid=[8,0], width=8, text='Position')
ELLtE = Text(boxELL, grid=[9,0], width=1, text='')
ELLt5 = Text(boxELL, grid=[10,0], width=8, text='Go to')
ELLtF = Text(boxELL, grid=[11,0], width=1, text='')
for iELL, ELL in enumerate(ELLs):
    ELL.set_index(iELL)
    ELL.set_state(0)
    ELLcb = CheckBox(boxELL, grid=[0,iELL+1], width=12, command=toggle_ELL_box, args=[ELL])
    ELLcb.text=f'{ELL.name} OUT'
    ELLcb.text_color = 'red'
    ELLtb1 = TextBox(boxELL, enabled=False, grid=[2,iELL+1], width=8)
    ELLtb2 = TextBox(boxELL, enabled=False, grid=[4,iELL+1], width=8)
    ELLtb3 = TextBox(boxELL, enabled=False, grid=[6,iELL+1], width=8)
    ELLtxt = TextBox(boxELL, enabled=False, grid=[8,iELL+1], width=8)
    ELLtb4 = TextBox(boxELL, grid=[10,iELL+1], width=8)
    ELLpb = PushButton(boxELL, text='Go', grid=[12,iELL+1], width=8, command=goto_ELL, args=[ELL])
    ELLtb1.value = '0'
    ELLtb2.value = '0'
    ELLtb3.value = '1'
    ELLtxt.value = f'{round(ELL.dev.GetPos(ser),2)}'
    ELLtb4.value = '0'
    ELL.set_cb(ELLcb)
    ELL.set_tb1(ELLtb1)
    ELL.set_tb2(ELLtb2)
    ELL.set_tb3(ELLtb3)
    ELL.set_txt(ELLtxt)
    ELL.set_tb4(ELLtb4)
    ELL.set_pb(ELLpb)

ACQt0 = Text(boxACQ, grid=[0,0,1,1], width=12, text='Lights')
ACQtA = Text(boxACQ, grid=[1,0,3,1], width=11, text='')
ACQt1 = Text(boxACQ, grid=[2,0,1,1], width=8, text='Acq Time')
ACQt2 = Text(boxACQ, grid=[4,0,1,1], width=8, text='N Acqs')
ACQt3 = Text(boxACQ, grid=[6,0,1,1], width=12, text='Graph')
ACQtD = Text(boxACQ, grid=[7,0,3,1], width=2, text='')

for iACQ, ACQ in enumerate(ACQs):
    ACQcb = CheckBox(boxACQ, grid=[0,iACQ+1], width=12, command=toggle_ACQ_box, args=[ACQ])
    ACQcb.text = 'Lights ON'
    ACQcb.text_color = 'red'
    ACQtb1 = TextBox(boxACQ, enabled=True, grid=[2,iACQ+1], width=8)
    ACQtb2 = TextBox(boxACQ, enabled=True, grid=[4,iACQ+1], width=8)
    ACQtb1.value = '1'
    ACQtb2.value = '1'
    ACQcb2 = CheckBox(boxACQ, grid=[6,iACQ+1], width=12, command=toggle_graph_box, args=[ACQ])
    ACQcb2.text = 'Hide Graph'
    ACQcb2.text_color = 'red'
    ACQpb = PushButton(boxACQ, text='ACQ', enabled=False, grid=[8,iACQ+1], width=8, command=start_ACQ, args=[ACQ,TTLs,ELLs])
    ACQ.set_cb(ACQcb)
    ACQ.set_cb2(ACQcb2)
    ACQ.set_tb1(ACQtb1)
    ACQ.set_tb2(ACQtb2)
    ACQ.set_pb(ACQpb)
    
# app.display()