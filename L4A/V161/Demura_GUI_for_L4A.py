# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 09:18:05 2022

@author: RockCHLin
"""
import serial
import tkinter as tk
from tkinter import ttk
import PIL.Image, PIL.ImageTk
import numpy as np
import os,time#,sys
import csv
from scipy.interpolate import interp1d
import serial.tools.list_ports
import matplotlib.pyplot as plt

from tkinter import filedialog, messagebox
from PIL import ImageGrab

from tkinter import simpledialog
from colour.plotting import plot_chromaticity_diagram_CIE1931
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk 

#from tqdm.tk import tqdm
from tkinter.ttk import Progressbar



class PrintLogger(): # create file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass
class figure_window(tk.Toplevel):
    def __initi__(self,root):
        self.canvas=tk.Canvas()
        #self.figure=f
        #self.creat_matplotlib()
        #self.creat_form(self.figure)
        
        
    def creat_matplotlib(self,f):
        #f= plt.figure(num=2,figsize=(16,12),dpi=80)
        #fig1=plt.subplot(1,1,1)
        self.creat_form(f)
        
        
    def creat_form(self,figure):
        self.canvas=FigureCanvasTkAgg(figure,self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        toolbar=NavigationToolbar2Tk(self.canvas,self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        
        
        
        
class meas_window(tk.Toplevel):
    def __init__(self,root):
        super().__init__()
        self.title('Treeview demo')
        self.geometry('800x400+%d+%d'%(ws/2,hs/2))
        self.frame_dataview=tk.Frame(self,width=800,height=250)
        self.frame_dataview.grid(column=0,row=0,columnspan=5,sticky=tk.W+tk.N+tk.E+tk.S)
        self.frame_data = tk.Frame(self.frame_dataview, width=800,height=150)
        self.frame_data_btn = tk.Frame(self.frame_dataview)
        self.frame_data.pack(fill=tk.BOTH,expand=True,pady=5,padx=5) 
        self.frame_data_btn.pack(pady=5)
        self.tree = self.create_tree_widget()
        self.cleardata_btn = tk.Button(self.frame_data_btn, text = "Clear Data", command = lambda: self.clear_data(), width=20)
        self.cleardata_btn.pack(side=tk.RIGHT,ipadx=5,padx=1)
        
        self.savedata_btn = tk.Button(self.frame_data_btn, text = "Save Data", command = lambda: self.save_csv(), width=20)
        self.savedata_btn.pack(side=tk.LEFT,ipadx=5,padx=1)
        
    def create_tree_widget(self):
             
        column_=("c1", "c2", "c3","c4","c5","c6","c7","c8","c9",'c10','c11','c12','c13','c14','c15','c16')
        column_item=('#','R','G','B','X','Y','Z','x','y','Lv',"u'","v'",'duv','Tcp','ld','Pe')
        tree = ttk.Treeview(self.frame_data,
                            column=column_, 
                            show='headings',
                            height=18)
        for col,item in list(zip(column_,column_item)):
            tree.column(col, width=35,anchor='center')
            tree.heading(col, text=item)
        
        tree.pack(fill=tk.BOTH,expand=True,ipady=150,ipadx=400)
        tree_vbar=ttk.Scrollbar(tree,orient=tk.VERTICAL,command=tree.yview)
        tree.configure(yscrollcommand=tree_vbar.set)
        tree_vbar.pack(side=tk.RIGHT,fill=tk.Y)
        
        return tree
    def clear_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            root.update()
                
        
    def save_csv(self):
        csv_name = filedialog.asksaveasfilename(title='Save location',
                                                defaultextension=[('CSV','*.csv')],
                                                filetypes=[('CSV','*.csv'),('Excel','*.xlsx')])
        if not csv_name or csv_name == '/': # If the user closes the dialog without choosing location
            messagebox.showerror('Error','Choose a location to save')
            return
        else:
            #strtime=time.strftime("%Y%m%d%H%M%S")
            with open(csv_name, "w", newline='') as myfile:
                csvwriter = csv.writer(myfile, delimiter=',')
                csvwriter.writerow(['Measerure Time:',time.strftime("%Y/%m/%d-%H:%M:%S")])
                csvwriter.writerow(['index','R','G','B','X','Y','Z','x','y','lv','u"','v"','duv','Tcp','ld','pe'])
                for row_id in self.tree.get_children():
                    row =self.tree.item(row_id)['values']
                    print('save row:', row)
                    csvwriter.writerow(row)
                    # Stop the function


        
        

    
class CA410():
    def __init__(self,COM):
        self.port=COM
        self.ser=None
        self.get_data_flag = True
        self.real_time_data =""
        self.frequency=120
        self.connect()
        
    def connect(self):
        
        self.ser=serial.Serial()
        self.ser.port=self.port
        self.ser.baudrate = 38400
        self.ser.bytesize = serial.SEVENBITS #number of bits per bytes
        self.ser.parity = serial.PARITY_EVEN #set parity check
        self.ser.stopbits = serial.STOPBITS_TWO #number of stop bits

        self.ser.timeout = 0.02         #non-block read 0.5s
        self.ser.writeTimeout = 0.02     #timeout for write 0.5s
        self.ser.xonxoff = False    #disable software flow control
        self.ser.rtscts = True     #disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False     #disable hardware (DSR/DTR) flow control
        try:
            self.ser.open()
        except Exception as ex:
            print ("open serial port error " + str(ex))
    def Zcal(self):
        if self.ser.is_open:
            self.SendCMD('ZRC')
            time.sleep(5)
            output=self.get_data()
            self.SendCMD('SCS,4,{mFreq}'.format(mFreq=str(self.frequency)))
            self.SendCMD('FSC,1')
            
            return output
            
    def SendCMD(self,string):
            string=string+'\n'
            self.ser.write((string).encode())
            time.sleep(0.1)
            output=self.ser.readall().decode('utf-8')
            return output
    def set_get_data_flag(self, get_data_flag):
         self.get_data_flag = get_data_flag
    def get_real_time_data(self):
        return self.real_time_data     
    def clear_real_time_data(self):
        self.real_time_data = ''
    def get_data(self, over_time=30):
        all_data = ''
        start_time = time.time()
        while True:
            end_time = time.time()
            if end_time - start_time < over_time and self.get_data_flag:
                data = self.ser.read(self.ser.inWaiting())
                # data = self.open_com.read() # read 1 size
                data = data.decode('utf-8')
                if data != '':
                    all_data = all_data + data
                    print (data)
                    self.real_time_data = all_data
                else:
                    self.set_get_data_flag(True)
                    break
        return all_data
    
    def SingleMeas(self):
        
        data=self.SendCMD('MES,2').replace('\r','')
        data=data.split(',')
        x=data[3]
        y=data[4]
        lv=data[5]
        X=data[8]
        Y=data[9]
        Z=data[10]
        return x,y,lv,X,Y,Z
    def SingleMeas_all(self,delay):
        

            
        for mode in [7,1,8]:
            self.SendCMD('MDS,{mode}'.format(mode=mode))
            if mode==7:
                
                data1=self.SendCMD('MES,1').replace('\r','')
    
            elif mode==1:
                
                data2=self.SendCMD('MES,1').replace('\r','')
             
            elif mode==8:
                
                data3=self.SendCMD('MES,1').replace('\r','')
                                     
                    
        if data1=='':
            
            self.SendCMD('MDS,{mode}'.format(mode=7))           
            string='MES,1'+'\n'
            self.ser.write((string).encode())
            time.sleep(delay)
            output=self.ser.readall().decode('utf-8')
            data1=output.replace('\r','')
            #time.sleep(0.5)

        if data2=='':
            self.SendCMD('MDS,{mode}'.format(mode=7))           
            string='MES,1'+'\n'
            self.ser.write((string).encode())
            time.sleep(delay)
            output=self.ser.readall().decode('utf-8')
            data2=output.replace('\r','')
        if data3=='':
            self.SendCMD('MDS,{mode}'.format(mode=7))           
            string='MES,1'+'\n'
            self.ser.write((string).encode())
            time.sleep(delay)
            output=self.ser.readall().decode('utf-8')
            data3=output.replace('\r','')
            
        data1=data1.split(',')
        data2=data2.split(',')
        data3=data3.split(',')
      
#        print(data1)
#        print(data2)
#        print(data3)
        X=float(data1[3])
        Y=float(data1[4])
        Z=float(data1[5])
        x=X/(X+Y+Z)
        y=Y/(X+Y+Z)
        lv=Y
        
        Tcp=float(data2[3])
        duv=float(data2[4])
                
        ld=float(data3[3])
        pe=float(data3[4])
        
        u = (4*x) / (-2*x + 12*y + 3);
        v = (9*y) / (-2*x + 12*y + 3);

        
        return X,Y,Z,x,y,lv,u,v,duv,Tcp,ld,pe
        #return data1,data2,data3
    def sMeas(self,points,interval=1):
        data_list=[]
        for i in range(points):
            time.sleep(interval)
            data_list.append(self.SingleMeas())
        return data_list
    def close(self):
        if self.ser is not None and self.ser.isOpen:
          self.ser.close()



root = tk.Tk()

ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()

root.geometry('830x300+%d+%d'%(ws/2,hs/2))


root.resizable(False, False)
root.title('RGB PLAYER © 2023 AUO Corporation, All Rights Reserved. by Rock CH Lin')
frame_slider = tk.Frame(root)
frame_chip=tk.Frame(root)
frame_btn=tk.Frame(root)
frame_pos=tk.Frame(root)
frame_path=tk.Frame(root)
fram_pg_bar=tk.Frame(root)

mask_sw=False
demura_sw=False
mask_pattern_sw=False
pause_check=False
ca410_chk=False
open_flag=0
pat_delay=0.01
gamma_step=16
frame_slider.grid(column=0,row=0,padx=2,pady=2)
frame_chip.grid(column=0,row=1,padx=2,pady=2)
frame_pos.grid(column=1,row=0,padx=2,pady=2)
frame_btn.grid(column=1,row=1,padx=2,pady=2)
frame_path.grid(column=0,row=2,columnspan=2,sticky=tk.W+tk.N+tk.E+tk.S)
fram_pg_bar.grid(column=0,row=3,columnspan=4,sticky=tk.E)


p_val_string = tk.StringVar()
p_val_string.set('')
progress = Progressbar(fram_pg_bar, orient=tk.HORIZONTAL, length=200, mode='determinate')
p_val_label = tk.Label(fram_pg_bar, textvariable=p_val_string)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)

posx=0
posy=0
start=int(0)
delay=float(0.01)
data=[]
rt=None
gt=None
bt=None
nr=None
ng=None
nb=None
data_window=None
dir_path_String=tk.StringVar()
dir_path_String.set(os.getcwd())

gammaData_path_String=tk.StringVar()

gammaData_label = ttk.Label(frame_path, text='Gamma Data')
gammaData_path = tk.Entry(frame_path, width=40, textvariable=gammaData_path_String)
gammaData_label.grid(column=0,row=1,sticky=tk.W,ipadx=5,padx=1,pady=5)
gammaData_path.grid(column=1,row=1,sticky=tk.W,ipadx=5,padx=1,pady=5)



entry_dir_label = ttk.Label(frame_path, text='RVS Data')
entry_dir_path = tk.Entry(frame_path, width=40, textvariable=dir_path_String)
entry_dir_label.grid(column=0,row=2,sticky=tk.W,ipadx=5,padx=1,pady=5)
entry_dir_path.grid(column=1,row=2,sticky=tk.W,ipadx=5,padx=1,pady=5)


img_dir_path_String=tk.StringVar()
img_dir_path_String.set("")
entry_img_dir_label = ttk.Label(frame_path, text='IMG path')
entry_img_dir_path = tk.Entry(frame_path, width=40, textvariable=img_dir_path_String)
#entry_img_dir_label.grid(column=0,row=4,sticky=tk.W,ipadx=5,padx=1,pady=5)
#entry_img_dir_path.grid(column=1,row=4,sticky=tk.W,ipadx=5,padx=1,pady=5)



Demura_Target_L=tk.DoubleVar()
Demura_Target_x=tk.DoubleVar()
Demura_Target_y=tk.DoubleVar()

Demura_Target_L.set(650)
Demura_Target_x.set(0.30)
Demura_Target_y.set(0.31)
Demura_Target_label = ttk.Label(frame_path, text='Target Lxy').grid(column=0,row=3,sticky=tk.W,ipadx=5,padx=1,pady=5)

entry_Demura_Target_L = tk.Entry(frame_path, width=5, textvariable=Demura_Target_L).grid(column=1,row=3,sticky=tk.W,columnspan=3,pady=5)
entry_Demura_Target_x = tk.Entry(frame_path, width=5, textvariable=Demura_Target_x).grid(column=1,row=3,sticky=tk.W,padx=60,columnspan=3,pady=5)
entry_Demura_Target_y = tk.Entry(frame_path, width=5, textvariable=Demura_Target_y).grid(column=1,row=3,sticky=tk.W,padx=120,columnspan=3,pady=5)

#LUT
lut_dir_path_String=tk.StringVar()
lut_dir_path_String.set("")
entry_lut_dir_label = ttk.Label(frame_path, text='LUT path')
entry_lut_dir_path = tk.Entry(frame_path, width=40, textvariable=lut_dir_path_String)
entry_lut_dir_label.grid(column=0,row=4,sticky=tk.W,ipadx=5,padx=1,pady=5)
entry_lut_dir_path.grid(column=1,row=4,sticky=tk.W,ipadx=5,padx=1,pady=5)

check_Gamma_file_btn=tk.Button(frame_path, text = "0-Gamma Data", command = lambda: select_file(),width=15,anchor="w")
check_Gamma_file_btn.grid(column=3, row=1, ipady=5, sticky=tk.W,ipadx=5,padx=5)

Calibration_btn=tk.Button(frame_path, text = "0.1-Calibration", command = lambda: calbrate_ratio(),width=15,anchor="w")
Calibration_btn.grid(column=4, row=1, ipady=5, sticky=tk.W,ipadx=5,padx=5)

check_Demura_file_btn=tk.Button(frame_path, text = "1-Update RVS Pattern", command = lambda: update_RVS_pattern(),width=15,anchor="w")
check_Demura_file_btn.grid(column=3, row=2, ipady=5, sticky=tk.W,ipadx=5,padx=5)

CalibrationDG_btn=tk.Button(frame_path, text = "0.2- DG to HEX", command = lambda: DG_calibration(),width=15,anchor="w")
CalibrationDG_btn.grid(column=4, row=2, ipady=5, sticky=tk.W,ipadx=5,padx=5)

Run_Demura_btn=tk.Button(frame_path, text = "2-Run Demura", command = lambda: demura_task(),width=15,anchor="w")
Run_Demura_btn.grid(column=3, row=3, ipady=5, sticky=tk.W,ipadx=5,padx=5)

open_window_btn=tk.Button(frame_path, text = "3-Open Check", command = lambda: new_window(),width=15,anchor="w")
open_window_btn.grid(column=3, row=4, ipady=5, sticky=tk.W,ipadx=5,padx=5)

ca410_link = tk.IntVar()
tk.Checkbutton(frame_path, text="CA410?", variable=ca410_link,onvalue=1, offvalue=0).grid(column=2,row=5, sticky=tk.W,ipadx=5,padx=1)

L4A_link = tk.IntVar()
tk.Checkbutton(frame_path, text="L4A Data Mode", variable=L4A_link,onvalue=1, offvalue=0).grid(column=2,row=2, sticky=tk.W,ipadx=5,padx=1)



image_demura_npy = tk.IntVar()
#tk.Checkbutton(frame_path, text="Image Demura?", variable=image_demura_npy,onvalue=1, offvalue=0).grid(column=2,row=4, sticky=tk.W,ipadx=5,padx=1,pady=5)

from tkinter.messagebox import showinfo

def select_file():
    filetypes = (
        ('text files', '*.csv'),
        ('All files', '*.*')
    )

    filename = filedialog.askopenfilename(title='Choose CA410 Gamma Data',
                                          initialdir='/',
                                          filetypes=filetypes)
    
    showinfo(title='Selected File', message=filename)
    gammaData_path_String.set(filename) 
    
def calbrate_ratio():
    global rt,gt,bt,nr,ng,nb
    rt,gt,bt,nr,ng,nb=calibrate_color_ratio(gammaData_path_String.get(),Demura_Target_L.get(),Demura_Target_x.get(),Demura_Target_y.get())
    rt,gt,bt=calibrate_color_ratio2(gammaData_path_String.get(),Demura_Target_L.get(),Demura_Target_x.get(),Demura_Target_y.get())
    return rt,gt,bt,nr,ng,nb

def DG_calibration():
    
    dgrt,dggt,dgbt=calibrate_color_ratio_XYZ_model(gammaData_path_String.get(),Demura_Target_L.get(),Demura_Target_x.get(),Demura_Target_y.get())
    
    prefix_name=simpledialog.askstring(title="Information",prompt="DG Hex File Name =")
    save_path=r'D:\Gamma_HEX_File'
    if os.path.isdir(save_path)==True:
        pass
    else:
        os.mkdir(save_path)
    output_DG(save_path,prefix_name,gammaData_path_String.get(),dgrt,dggt,dgbt)
    



def update_RVS_pattern():
    global nr,ng,nb
    LUT_gray_8=[4,8,12,16,20,24,28,32,64,96,128,160,192,224,255]
    nr_p=nr[LUT_gray_8]
    ng_p=ng[LUT_gray_8]
    nb_p=nb[LUT_gray_8]
    
    pattern_path=r'D:\RVS\Sequence\16.1 Recipe\NEW_PATTERN_2'
    if os.path.isdir(pattern_path)==True:
        pass
    else:
        os.mkdir(pattern_path)
        
    print(nr_p)
    print(ng_p)
    print(nb_p)
    print('Output Compensation Image')
    for i in range(len(LUT_gray_8)):
        
       
        
        R=np.ones((1080,1920))*nr_p[i]
        G=np.ones((1080,1920))*ng_p[i]
        B=np.ones((1080,1920))*nb_p[i]
        
        blank=0*np.ones((1080,1920)).astype('uint8')
        
        img=np.dstack([R.astype('uint8'),G.astype('uint8'),B.astype('uint8')])
        Bimg=np.dstack([blank,blank,B.astype('uint8')])
        Gimg=np.dstack([blank,G.astype('uint8'),blank])
        Rimg=np.dstack([R.astype('uint8'),blank,blank])
        
        

        Wimage = PIL.Image.fromarray(img)
        Rimage = PIL.Image.fromarray(Rimg)
        Gimage = PIL.Image.fromarray(Gimg)
        Bimage = PIL.Image.fromarray(Bimg)


        Wimage.save(os.path.join(pattern_path,'W'+str(LUT_gray_8[i])+'.bmp'))
        Rimage.save(os.path.join(pattern_path,'R'+str(LUT_gray_8[i])+'.bmp'))
        Gimage.save(os.path.join(pattern_path,'G'+str(LUT_gray_8[i])+'.bmp'))
        Bimage.save(os.path.join(pattern_path,'B'+str(LUT_gray_8[i])+'.bmp'))
    
    
    showinfo(title='RVS Pattern Update!!!', message="LUT save in "+os.path.join(pattern_path))
    
    
def on_select(event=None):

    # get selection from event    
    print("event.widget:", event.widget.get())

    # or get selection directly from combobox
    print("comboboxes: ", cb.get())

cb_label = ttk.Label(frame_path, text='Port')
cb_label.grid(column=0,row=5,sticky=tk.W,ipadx=5,padx=1,pady=5)
cb = ttk.Combobox(frame_path, values=[p.device for p in serial.tools.list_ports.comports()])
cb.grid(column=1,row=5, sticky=tk.W,ipadx=5,padx=1,pady=5)

# assign function to combobox
cb.bind('<<ComboboxSelected>>', on_select)

model_select = ttk.Combobox(frame_path, values=['Y136_480X270','V161_240X540','Y136_960X540','Y173_1280X720','User_resolution'])
model_select.grid(column=2,row=3, sticky=tk.W,ipadx=5,padx=1,pady=5)
model_select.current(1)

def get_resxy():
        
    selresolution=['Y136_480X270','V161_240X540','Y136_960X540','Y173_1280X720','User_resolution']
    if model_select.get()==selresolution[0]:
        model='Y136'
        res_x=int(480)
        res_y=int(270)
    elif model_select.get()==selresolution[1]:
        model='Y161'
        res_x=int(240)
        res_y=int(540)
    elif model_select.get()==selresolution[2]:
        model='Y136'
        res_x=int(960)
        res_y=int(540)
    elif model_select.get()==selresolution[2]:
        model='Y173'
        res_x=int(1280)
        res_y=int(720)
    else:
        model='User_resolution'
        res_x=int(simpledialog.askstring(title="Panel Resolution",
                              prompt="Resolution X ="))
        res_y=int(simpledialog.askstring(title="Panel Resolution",
                              prompt="Resolution Y ="))
    return res_x,res_y,model

def calibrate_color_ratio(ca410_data,target_L,target_x,target_y):
    
    target_L=Demura_Target_L.get()
    target_x=Demura_Target_x.get()
    target_y=Demura_Target_y.get()
    
    r1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=261,max_rows=256,usecols=(1,2,3))
    g1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=520,max_rows=256,usecols=(1,2,3))
    b1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=779,max_rows=256,usecols=(1,2,3))
    r1[0,1]=0
    g1[0,1]=0
    b1[0,1]=0
    
    rx_ip1d=interp1d(r1[:,1],r1[:,0], fill_value='extrapolate')
    rz_ip1d=interp1d(r1[:,1],r1[:,2], fill_value='extrapolate')    
    gx_ip1d=interp1d(g1[:,1],g1[:,0], fill_value='extrapolate')
    gz_ip1d=interp1d(g1[:,1],g1[:,2], fill_value='extrapolate')    
    bx_ip1d=interp1d(b1[:,1],b1[:,0], fill_value='extrapolate')
    bz_ip1d=interp1d(b1[:,1],b1[:,2], fill_value='extrapolate')    
    
    
    ry_ip1d=interp1d([i for i in range(256)],r1[:,1], fill_value='extrapolate')
    gy_ip1d=interp1d([i for i in range(256)],g1[:,1], fill_value='extrapolate')
    by_ip1d=interp1d([i for i in range(256)],b1[:,1], fill_value='extrapolate')
    
    rt_array=[]
    gt_array=[]
    bt_array=[]
    
    # r_dg=interp1d(r1.Y.values.astype(np.float64)/np.max(r1.Y.values.astype(np.float64)),[i for i in range(256)], fill_value='extrapolate')
    # g_dg=interp1d(g1.Y.values.astype(np.float64)/np.max(g1.Y.values.astype(np.float64)),[i for i in range(256)], fill_value='extrapolate')
    # b_dg=interp1d(b1.Y.values.astype(np.float64)/np.max(b1.Y.values.astype(np.float64)),[i for i in range(256)], fill_value='extrapolate')
    r_dg=interp1d(r1[:,1]/np.max(r1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    g_dg=interp1d(g1[:,1]/np.max(g1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    b_dg=interp1d(b1[:,1]/np.max(b1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    
    nr=r_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    ng=g_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    nb=b_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    
    
    
    indexR=nr[[8,16,32,64,96,128,160,192,224,255]]
    indexG=ng[[8,16,32,64,96,128,160,192,224,255]]
    indexB=nb[[8,16,32,64,96,128,160,192,224,255]]
    
    Tgray=[8,16,32,64,96,128,160,192,224,255]
    dg=[]
    wxx=[]
    wyy=[]
    fig1= plt.figure(num=1)
    fig1,ax=plt.subplots(2,3,figsize=(12,8))
    plot_chromaticity_diagram_CIE1931(standalone=False,axes=ax[0,0],title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    for gray in range(len(indexR)): #r1.Tone.astype(np.int32).values: 
        #plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    
        #gray=1
        #0 row -1是找最接近的最後一個
        wx=[]
        wy=[]
        
        r=indexR[gray]
        #np.where(r1.Tone.astype(np.int32)==indexR[gray])[0][-1]
        g=indexG[gray]
        b=indexB[gray]
        
        for loop in range(10):
            RX, RY, RZ =rx_ip1d(ry_ip1d(r)),ry_ip1d(r),rz_ip1d(ry_ip1d(r))#float(r1.X.iloc[r]),float(r1.Y.iloc[r]),float(r1.Z.iloc[r])
            GX, GY, GZ =gx_ip1d(gy_ip1d(g)),gy_ip1d(g),gz_ip1d(gy_ip1d(g))#float(g1.X.iloc[g]),float(g1.Y.iloc[g]),float(g1.Z.iloc[g])
            BX, BY, BZ =bx_ip1d(by_ip1d(b)),by_ip1d(b),bz_ip1d(by_ip1d(b))# float(b1.X.iloc[b]),float(b1.Y.iloc[b]),float(b1.Z.iloc[b])
            R_sum = RX+RY+RZ
            G_sum = GX+GY+GZ
            B_sum = BX+BY+BZ
            alfa = RY-target_y*(RX+RY+RZ)
            beta = RX-target_x*(RX+RY+RZ)
            constantB = (beta*(target_y*B_sum-BY)-alfa*(target_x*B_sum-BX))/(alfa*(target_x*G_sum-GX)-beta*(target_y*G_sum-GY))
            constantA = (constantB*(target_x*G_sum-GX)+target_x*B_sum-BX)/(RX-target_x*R_sum)
            ratio_R = constantA
            ratio_G = constantB
            
            rt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_R*RY/(ratio_R*RY+ratio_G*GY+BY))).clip(r1[:,1][0],r1[:,1][-1])
            gt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_G*GY/(ratio_R*RY+ratio_G*GY+BY))).clip(g1[:,1][0],g1[:,1][-1])
            bt=(target_L*((Tgray[gray]/255)**2.2)*(BY/(ratio_R*RY+ratio_G*GY+BY))).clip(b1[:,1][0],b1[:,1][-1])

            
            #print(rt,gt,bt)
            rtmp=r
            gtmp=g
            btmp=b
            #找目標亮度
            r=r_dg(rt/np.max(r1[:,1])).round(4)#r=np.abs(r1.Y.astype(np.float64) - rt).argmin()
            g=g_dg(gt/np.max(g1[:,1])).round(4)#g=np.abs(g1.Y.astype(np.float64) - gt).argmin()
            b=b_dg(bt/np.max(b1[:,1])).round(4)#b=np.abs(b1.Y.astype(np.float64) - bt).argmin()
    
            if loop==8:
                newr=r_dg(rt/np.max(r1[:,1])).round(4)#67.50956154862239  #97
                newg=g_dg(gt/np.max(g1[:,1])).round(4)#166.8327090883952 #106
                newb=b_dg(bt/np.max(b1[:,1])).round(4)#15.657729362982373 #85
                print(newr,newg,newb,loop)
                
                dg.append(np.array([gray,newr,newg,newb]))
                rt_array.append(rt)
                gt_array.append(gt)
                bt_array.append(bt)
            
            wX=RX+GX+BX
            wY=RY+GY+BY
            wZ=RZ+GZ+BZ
            wx.append(wX/(wX+wY+wZ))
            wy.append(wY/(wX+wY+wZ))
            #再次找灰階最接近的值
            if rtmp==r and gtmp==g and btmp==b:
                newr=r_dg(rt/np.max(r1[:,1])).round(4)#67.50956154862239  #97 
                newg=g_dg(gt/np.max(g1[:,1])).round(4)#166.8327090883952 #106  
                newb=b_dg(bt/np.max(b1[:,1])).round(4)#15.657729362982373 #85
                print(newr,newg,newb,loop)
                
                dg.append(np.array([gray,newr,newg,newb]))
                rt_array.append(rt)
                gt_array.append(gt)
                bt_array.append(bt)
                break
        wX=RX+GX+BX
        wY=RY+GY+BY
        wZ=RZ+GZ+BZ
        wxx.append(wX/(wX+wY+wZ))
        wyy.append(wY/(wX+wY+wZ))
        ax[0,0].scatter(wx,wy)
        ax[0,0].plot(wx,wy)
    #化點
    dg_df=np.array(dg)
    #dg_df=pd.DataFrame(np.array(dg),columns=['gray','R','G','B'])
    
    plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",axes=ax[0,1],bounding_box=(-0.1, 1, -0.1, 1))
    ax[0,1].scatter(wxx,wyy)
    ax[0,1].set_xlim(-0.08, 0.8)
    ax[0,1].set_ylim(-0.08, 0.9)
    
    ax[0,2].plot(Tgray,dg_df[:,1],'-r',marker='.')
    ax[0,2].plot(Tgray,dg_df[:,2],'-g',marker='.')
    ax[0,2].plot(Tgray,dg_df[:,3],'-b',marker='.')
    ax[0,2].set_xlim(0,255)
    ax[0,2].set_xticks(Tgray)
    
    
   
    ax[1,0].plot(dg_df[:,0],rt_array,'--r',label='R Lum Target')
    ax[1,0].plot(dg_df[:,0],
            ry_ip1d(dg_df[:,1]),
            '-r',label='R Lum real ca410')
    ax[1,0].legend()
    

    ax[1,1].plot(dg_df[:,0],gt_array,'--g',label='G Lum Target')#,marker='^')
    ax[1,1].plot(dg_df[:,0],
            gy_ip1d(dg_df[:,2]),
            '-g',label='G Lum Real ca410')
    ax[1,1].legend(loc='best')
    

    ax[1,2].plot(dg_df[:,0],bt_array,'--b',label='B Lum Target')#,marker='^')
    ax[1,2].plot(dg_df[:,0],
            by_ip1d(dg_df[:,3]),
            '-b',label='B Lum Real ca410')
    ax[1,2].legend(loc='best')

    
    new_cal=figure_window(root)

    new_cal.creat_matplotlib(fig1)
    #new_cal.creat_form()
    
    if nb[-1] != 255:
       nb[-1]=255
       #print(rt_array,gt_array,bt_array,nr,ng,nb)
    return rt_array,gt_array,bt_array,nr,ng,nb

def calibrate_color_ratio2(ca410_data,target_L,target_x,target_y):
    
    target_L=Demura_Target_L.get()
    target_x=Demura_Target_x.get()
    target_y=Demura_Target_y.get()
    
    r1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=261,max_rows=256,usecols=(1,2,3))
    g1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=520,max_rows=256,usecols=(1,2,3))
    b1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=779,max_rows=256,usecols=(1,2,3))
    r1[0,1]=0
    g1[0,1]=0
    b1[0,1]=0
    
    rx_ip1d=interp1d(r1[:,1],r1[:,0], fill_value='extrapolate')
    rz_ip1d=interp1d(r1[:,1],r1[:,2], fill_value='extrapolate')    
    gx_ip1d=interp1d(g1[:,1],g1[:,0], fill_value='extrapolate')
    gz_ip1d=interp1d(g1[:,1],g1[:,2], fill_value='extrapolate')    
    bx_ip1d=interp1d(b1[:,1],b1[:,0], fill_value='extrapolate')
    bz_ip1d=interp1d(b1[:,1],b1[:,2], fill_value='extrapolate')    
    
    
    ry_ip1d=interp1d([i for i in range(256)],r1[:,1], fill_value='extrapolate')
    gy_ip1d=interp1d([i for i in range(256)],g1[:,1], fill_value='extrapolate')
    by_ip1d=interp1d([i for i in range(256)],b1[:,1], fill_value='extrapolate')
    
    rt_array=[]
    gt_array=[]
    bt_array=[]

    r_dg=interp1d(r1[:,1]/np.max(r1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    g_dg=interp1d(g1[:,1]/np.max(g1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    b_dg=interp1d(b1[:,1]/np.max(b1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    
    nr=r_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    ng=g_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    nb=b_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    
    
    
    indexR=nr[[8,16,50,64,96,128,160,192,224,255]]
    indexG=ng[[8,16,50,64,96,128,160,192,224,255]]
    indexB=nb[[8,16,50,64,96,128,160,192,224,255]]
    
    Tgray=[8,16,50,64,96,128,160,192,224,255]
    dg=[]
    wxx=[]
    wyy=[]
    fig1= plt.figure(num=1)
    fig1,ax=plt.subplots(2,3,figsize=(12,8))
    plot_chromaticity_diagram_CIE1931(standalone=False,axes=ax[0,0],title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    for gray in range(len(indexR)): #r1.Tone.astype(np.int32).values: 
        #plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    
        #gray=1
        #0 row -1是找最接近的最後一個
        wx=[]
        wy=[]
        
        r=indexR[gray]
        g=indexG[gray]
        b=indexB[gray]
        
        for loop in range(10):
            RX, RY, RZ =rx_ip1d(ry_ip1d(r)),ry_ip1d(r),rz_ip1d(ry_ip1d(r))#float(r1.X.iloc[r]),float(r1.Y.iloc[r]),float(r1.Z.iloc[r])
            GX, GY, GZ =gx_ip1d(gy_ip1d(g)),gy_ip1d(g),gz_ip1d(gy_ip1d(g))#float(g1.X.iloc[g]),float(g1.Y.iloc[g]),float(g1.Z.iloc[g])
            BX, BY, BZ =bx_ip1d(by_ip1d(b)),by_ip1d(b),bz_ip1d(by_ip1d(b))# float(b1.X.iloc[b]),float(b1.Y.iloc[b]),float(b1.Z.iloc[b])
            R_sum = RX+RY+RZ
            G_sum = GX+GY+GZ
            B_sum = BX+BY+BZ
            alfa = RY-target_y*(RX+RY+RZ)
            beta = RX-target_x*(RX+RY+RZ)
            constantB = (beta*(target_y*B_sum-BY)-alfa*(target_x*B_sum-BX))/(alfa*(target_x*G_sum-GX)-beta*(target_y*G_sum-GY))
            constantA = (constantB*(target_x*G_sum-GX)+target_x*B_sum-BX)/(RX-target_x*R_sum)
            ratio_R = constantA
            ratio_G = constantB
            
            rt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_R*RY/(ratio_R*RY+ratio_G*GY+BY))).clip(r1[:,1][0],r1[:,1][-1])
            gt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_G*GY/(ratio_R*RY+ratio_G*GY+BY))).clip(g1[:,1][0],g1[:,1][-1])
            bt=(target_L*((Tgray[gray]/255)**2.2)*(BY/(ratio_R*RY+ratio_G*GY+BY))).clip(b1[:,1][0],b1[:,1][-1])

            
            #print(rt,gt,bt)
            rtmp=r
            gtmp=g
            btmp=b
            #找目標亮度
            r=r_dg(rt/np.max(r1[:,1])).round(4)#r=np.abs(r1.Y.astype(np.float64) - rt).argmin()
            g=g_dg(gt/np.max(g1[:,1])).round(4)#g=np.abs(g1.Y.astype(np.float64) - gt).argmin()
            b=b_dg(bt/np.max(b1[:,1])).round(4)#b=np.abs(b1.Y.astype(np.float64) - bt).argmin()
    
            if loop==8:
                newr=r_dg(rt/np.max(r1[:,1])).round(4)#67.50956154862239  #97
                newg=g_dg(gt/np.max(g1[:,1])).round(4)#166.8327090883952 #106
                newb=b_dg(bt/np.max(b1[:,1])).round(4)#15.657729362982373 #85
                print(newr,newg,newb,loop)
                
                dg.append(np.array([gray,newr,newg,newb]))
                rt_array.append(rt)
                gt_array.append(gt)
                bt_array.append(bt)
            
            wX=RX+GX+BX
            wY=RY+GY+BY
            wZ=RZ+GZ+BZ
            wx.append(wX/(wX+wY+wZ))
            wy.append(wY/(wX+wY+wZ))
            #再次找灰階最接近的值
            if rtmp==r and gtmp==g and btmp==b:
                newr=r_dg(rt/np.max(r1[:,1])).round(4)#67.50956154862239  #97 
                newg=g_dg(gt/np.max(g1[:,1])).round(4)#166.8327090883952 #106  
                newb=b_dg(bt/np.max(b1[:,1])).round(4)#15.657729362982373 #85
                print(newr,newg,newb,loop)
                
                dg.append(np.array([gray,newr,newg,newb]))
                rt_array.append(rt)
                gt_array.append(gt)
                bt_array.append(bt)
                break
        wX=RX+GX+BX
        wY=RY+GY+BY
        wZ=RZ+GZ+BZ
        wxx.append(wX/(wX+wY+wZ))
        wyy.append(wY/(wX+wY+wZ))
        ax[0,0].scatter(wx,wy)
        ax[0,0].plot(wx,wy)
    #化點
    dg_df=np.array(dg)
    #dg_df=pd.DataFrame(np.array(dg),columns=['gray','R','G','B'])
    
    
    return rt_array,gt_array,bt_array

def L4A_Demura(root_dir):
    
    #################################################################################
    #Demura Process
    #################################################################################
    # #only read RVS luminace
    
    
    
    
    res_x,res_y,model=get_resxy()
    
    if model == 'Y161':
        resolution_x=res_y
        resolution_y=res_x
    else:
        resolution_x=res_x
        resolution_y=res_y
    
    def dataXYZ_noXZ(path,y_resolution=240):
        try:
            chunks=np.loadtxt(path,delimiter=",",encoding="utf-8",max_rows=y_resolution)
        except:
            chunks=np.loadtxt(path,encoding="utf-8",max_rows=y_resolution)
        #chunks = pd.read_csv(path,header=None,iterator = True)
        return np.array(chunks)
       # =============================================================================
    
    def pos(M):
        M[1][M[1]<0]=0
        return M
    
    save_path=os.path.abspath(os.path.join(root_dir,os.path.pardir,'cpimg'))
    lut_dir_path_String.set(save_path)
    root.update()
    if os.path.isdir(save_path)==True:
        pass
    else:
        os.mkdir(save_path)
    
    
    if model =='Y161' and L4A_link.get()==1:
        # fitting layer L4A
        Data_layer=[8,16,32,64,96,128,160,192,224,255]
        graylv=[48,53,64,84,94,96,104,128,192,255]
        
    elif model =='Y161' and L4A_link.get()==0:
        global nr,ng,nb
        Data_layer=[4,8,12,16,20,24,28,32,64,96,128,160,192,224,255] #Data layer
        
        #graylv=[43,48,50,53,55,58,60,64,84,94,96,104,128,192,255] # fitting layer 0908改
        
        graylv=np.array([nr[Data_layer],ng[Data_layer],nb[Data_layer]])
               
        
    elif model=='Y136' or model=='Y173':
        Data_layer=[8,12,16,20,24,28,32,64,96,128,160,192,224,255]
        graylv=[8,12,16,20,24,28,32,64,96,128,160,192,224,255]
        
    
    # Data_file_path_w=[]
    Data_file_path_r=[]
    Data_file_path_g=[]
    Data_file_path_b=[]
    
    if L4A_link.get()==1:
        data=[]
        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                            
                if file.endswith('.csv'):
                    file.format({})
                    
                    data.append(os.path.join(subdir,file))
        
        

        for gray in Data_layer:
            #Data_file_path_w.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='W',gray=i)))
            Data_file_path_r.append(np.array(data)[["R{gray}P".format(gray=gray) in i.split('\\')[-1].split('.csv')[0] for i in data]][0])
            try:
                Data_file_path_g.append(np.array(data)[["G{gray}P".format(gray=gray) in i.split('\\')[-1].split('.csv')[0] for i in data]][0])
            except:
                pass
            Data_file_path_b.append(np.array(data)[["B{gray}P".format(gray=gray) in i.split('\\')[-1].split('.csv')[0] for i in data]][0])

        ####
        W0 = np.array(data)[["R8P" in i.split('\\')[-1].split('.csv')[0] for i in data]][0]
        ###
        black_data=dataXYZ_noXZ(W0)
        
        Rdf={}
        Gdf={}
        Bdf={}
        
        for i in range(len(Data_layer)):
                
            Rdf[Data_layer[i]]=pos(dataXYZ_noXZ(Data_file_path_r[i])-black_data)
            Bdf[Data_layer[i]]=pos(dataXYZ_noXZ(Data_file_path_b[i])-black_data)
            Gdf[Data_layer[i]]=pos(dataXYZ_noXZ(Data_file_path_g[i])-black_data)
            
            # Rdf[Data_layer[i]][120:135,118:139]=Rdf[Data_layer[i]][120:135,118+21:139+21]
            # Bdf[Data_layer[i]][120:135,118:139]=Bdf[Data_layer[i]][120:135,118+21:139+21]
            # Gdf[Data_layer[i]][120:135,118:139]=Gdf[Data_layer[i]][120:135,118+21:139+21]
            
            
            
        
        # Data_layerg=[8,16,32,64,128,160,192,224,255]
        # graylvg=[48,53,64,84,96,104,128,192,255] # fitting layer 0908改

        # for i in range(len(Data_layerg)):
        #     #Wdf[Data_layer[i]]=pos(dataXYZ(Data_file_path_w[i])-black_data)
            
        #     Gdf[graylvg[i]]=pos(dataXYZ_noXZ(Data_file_path_g[i])-black_data)
        
        # Gdf[graylv[4]]=pos(dataXYZ_noXZ(Data_file_path_g[5])*(graylv[4]/graylv[5])**2.2-black_data)
        
    else:
    
        for i in Data_layer:
            #Data_file_path_w.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='W',gray=i)))
            Data_file_path_r.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Red',gray=i)))
            Data_file_path_g.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Green',gray=i)))
            Data_file_path_b.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Blue',gray=i)))
            
        #W0 = os.path.join(root_dir,'{color}{gray}.CSV'.format(color='W',gray=0))
    
        #black_data=dataXYZ_noXZ(W0)
        
        Rdf={}
        Gdf={}
        Bdf={}
        
        for i in range(len(Data_layer)):
                
            Rdf[Data_layer[i]]=pos(dataXYZ_noXZ(Data_file_path_r[i]))
            Bdf[Data_layer[i]]=pos(dataXYZ_noXZ(Data_file_path_b[i]))
            Gdf[Data_layer[i]]=pos(dataXYZ_noXZ(Data_file_path_g[i]))
            
            # Rdf[Data_layer[i]][120:135,118:139]=Rdf[Data_layer[i]][120:135,118+21:139+21]
            # Bdf[Data_layer[i]][120:135,118:139]=Bdf[Data_layer[i]][120:135,118+21:139+21]
            # Gdf[Data_layer[i]][120:135,118:139]=Gdf[Data_layer[i]][120:135,118+21:139+21]


        
        
        
    
    
    
    DataYR=[]
    DataYG=[]
    DataYB=[]
    
    
    #graylv=[8,12,16,20,24,28,32,64,128,192,255]
    
    for i in Data_layer:
        DataYR.append(Rdf[i].flatten())
        DataYG.append(Gdf[i].flatten())
        DataYB.append(Bdf[i].flatten())
    
    DataYR=np.array(DataYR)
    DataYG=np.array(DataYG)
    DataYB=np.array(DataYB)
    
    avg_DataYR=[np.average(i) for i in DataYR]
    avg_DataYG=[np.average(i) for i in DataYG]
    avg_DataYB=[np.average(i) for i in DataYB]
    

    
    
    for i in range(1,len(DataYR)):
        DataYR[i]=np.where(DataYR[-1]<0.35*avg_DataYR[-1],avg_DataYR[i],DataYR[i])
    for i in range(1,len(DataYG)):
        DataYG[i]=np.where(DataYG[-1]<0.65*avg_DataYG[-1],avg_DataYG[i],DataYG[i])
    for i in range(1,len(DataYB)):
        DataYB[i]=np.where(DataYB[-1]<0.35*avg_DataYB[-1],avg_DataYB[i],DataYB[i])    
    
    
    # import cv2
    # map_img=cv2.imread(r'E:\V161\20230725\0A1512\R255_2.bmp')
    # map_img=np.rot90(map_img,1)
    # #sns.heatmap(np.where(map_img[:,:,2]>224,255,0))
    # mask=np.ones((240,540))
    # defect=np.where(map_img[:,:,2]>224,255,0)

    # defect=np.where(defect[119:137,118:139]==255,456789,1)
    # mask[119:137,118:139]=defect
   
    
    # mask=mask.flatten()
    
    
    # for i in range(1,len(DataYR)):
    #     DataYR[i]=np.where(mask==456789,avg_DataYR[i],DataYR[i])
    # for i in range(1,len(DataYG)):
    #     DataYG[i]=np.where(mask==456789,avg_DataYG[i],DataYG[i])
    # for i in range(1,len(DataYB)):
    #     DataYB[i]=np.where(mask==456789,avg_DataYB[i],DataYB[i])    
    
    
    
    
    ###################
    
    DataYR=DataYR.T
    DataYG=DataYG.T
    DataYB=DataYB.T
    
 
    
 
    
    
    
    return DataYR,DataYG,DataYB,graylv
    
def gen_cpimg(cp_R255,cp_G255,cp_B255):
    lut_dir_path_String.get()
    LUT_gray_8=[8,16,32, 64, 96, 128, 160, 192, 224, 255]
    res_x,res_y,model=get_resxy()
    if model == 'Y161':
        resolution_x=res_y
        resolution_y=res_x
        rot=3
    else:
        resolution_x=res_x
        resolution_y=res_y
        rot=0
    print('Output Compensation Image')
    for i in range(len(LUT_gray_8)):
        
        
        R=np.array(cp_R255)[:,i].reshape(resolution_y,resolution_x)
        G=np.array(cp_G255)[:,i].reshape(resolution_y,resolution_x)
        B=np.array(cp_B255)[:,i].reshape(resolution_y,resolution_x)
        
        blank=0*np.ones((resolution_y,resolution_x)).astype('uint8')
        
        img=np.dstack([R.astype('uint8'),G.astype('uint8'),B.astype('uint8')])
        Bimg=np.dstack([blank,blank,B.astype('uint8')])
        Gimg=np.dstack([blank,G.astype('uint8'),blank])
        Rimg=np.dstack([R.astype('uint8'),blank,blank])
                
        Wimage = PIL.Image.fromarray(np.rot90(img,rot))
        Rimage = PIL.Image.fromarray(np.rot90(Rimg,rot))
        Gimage = PIL.Image.fromarray(np.rot90(Gimg,rot))
        Bimage = PIL.Image.fromarray(np.rot90(Bimg,rot))
    
    
        Wimage.save(os.path.join(lut_dir_path_String.get(),'W'+str(LUT_gray_8[i])+'_2.bmp'))
        Rimage.save(os.path.join(lut_dir_path_String.get(),'R'+str(LUT_gray_8[i])+'_2.bmp'))
        Gimage.save(os.path.join(lut_dir_path_String.get(),'G'+str(LUT_gray_8[i])+'_2.bmp'))
        Bimage.save(os.path.join(lut_dir_path_String.get(),'B'+str(LUT_gray_8[i])+'_2.bmp'))
    print("demura images save in "+ os.path.join(img_dir_path_String.get()))

def gen_LUT(cp_R255,cp_G255,cp_B255):
    res_x,res_y,model=get_resxy()
    
    #=======================================#
    #輸出LUT 10bit layer
    #=======================================#

    if model=='Y161':
        LUT_gray=(32,64,128,256,768)
        rot=3
        resolution_x=res_y
        resolution_y=res_x
        scale_bit=32
        clip_bit_upper=4095
        clip_bit_lower=-4095
        LUT_gray_8 = np.array([8,16,32,64,96,128,160,192,224,255]).astype(np.float32)    
        LUT_gray_10=np.array([  32,   64,  128,  256,  384,  512,  640,  768,  896, 1020])
    elif model =='Y136':
        LUT_gray=(32,64,128,256,768)
        rot=0
        resolution_x=res_x
        resolution_y=res_y
        scale_bit=32
        clip_bit_upper=4095
        clip_bit_lower=-4095
        LUT_gray_8 = np.array([8,16,32,64,96,128,160,192,224,255]).astype(np.float32)    
        LUT_gray_10=np.array([  32,   64,  128,  256,  384,  512,  640,  768,  896, 1020])
    else:
        rot=0
        LUT_gray=(60,  124,  252,  508, 1020)
        scale_bit=16
        resolution_x=res_x
        resolution_y=res_y
        clip_bit_upper=1023
        clip_bit_lower=-1023
        LUT_gray_8 = np.array([8,16,32,64,96,128,160,192,224,255]).astype(np.float32)    
        LUT_gray_10=np.array([  32,   64,  128,  256,  384,  512,  640,  768,  896, 1024])-4
    #輸出LUT存檔路徑
    save_path=lut_dir_path_String.get()
    #編號
    num=dir_path_String.get().split('\\')[-2]
    
    
   
    
    def img_flip(m,flip):
        if flip==True:
            m=np.flip(m,axis=0)
            #m=np.flip(m,axis=1)
        else:
            m=m
            
        return m
    def reshape_scale(m):
        m=np.array(m).reshape(540,240)
        return m
    
    
    #=======================================#
    #LUT建立
    #=======================================#
    LUT_R={}
    LUT_G={}
    LUT_B={}

    for i in range(len(LUT_gray_10)):
        
        LUT_R[str(LUT_gray_10[i])] = (np.rot90(np.array(cp_R255)[:,i].reshape(resolution_y,resolution_x).clip(0,255),rot)-LUT_gray_8[i])*scale_bit
        LUT_G[str(LUT_gray_10[i])] = (np.rot90(np.array(cp_G255)[:,i].reshape(resolution_y,resolution_x).clip(0,255),rot)-LUT_gray_8[i])*scale_bit
        LUT_B[str(LUT_gray_10[i])] = (np.rot90(np.array(cp_B255)[:,i].reshape(resolution_y,resolution_x).clip(0,255),rot)-LUT_gray_8[i])*scale_bit
        
        LUT_R[str(LUT_gray_10[i])] = np.where(LUT_R[str(LUT_gray_10[i])]>clip_bit_upper,clip_bit_upper,LUT_R[str(LUT_gray_10[i])])
        LUT_G[str(LUT_gray_10[i])] = np.where(LUT_G[str(LUT_gray_10[i])]>clip_bit_upper,clip_bit_upper,LUT_G[str(LUT_gray_10[i])])
        LUT_B[str(LUT_gray_10[i])] = np.where(LUT_B[str(LUT_gray_10[i])]>clip_bit_upper,clip_bit_upper,LUT_B[str(LUT_gray_10[i])])
        
        LUT_R[str(LUT_gray_10[i])] = np.where(LUT_R[str(LUT_gray_10[i])]<clip_bit_lower,clip_bit_lower,LUT_R[str(LUT_gray_10[i])])
        LUT_G[str(LUT_gray_10[i])] = np.where(LUT_G[str(LUT_gray_10[i])]<clip_bit_lower,clip_bit_lower,LUT_G[str(LUT_gray_10[i])])
        LUT_B[str(LUT_gray_10[i])] = np.where(LUT_B[str(LUT_gray_10[i])]<clip_bit_lower,clip_bit_lower,LUT_B[str(LUT_gray_10[i])])
    
    def bit_check(LUT):
        val=np.max([abs(LUT.min()),abs(LUT.max())])/8
        #7	8	9	10	11	12	13
        #64	128	256	512	1024 2048	4096

        if val <64:
            return 7
        elif val<128:
            return 8
        elif val <256:
            return 9
        elif val<512:
            return 10
        elif val <1024:
            return 11
        elif val<2048:
            return 12
        else:
            return 13
        

    
    if model =='Y161':
        print("="*50)
        print("Check LEFT LUT BITS TOTAL")        
        bit_sum_left=[]
        for u in LUT_gray:
            print('Layer R:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_R[str(u)][:,0:120].min().astype('int64'),LUT_R[str(u)][:,0:120].max().astype('int64'),bit_check(LUT_R[str(u)][:,0:120].astype('int64'))))
            print('Layer G:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_G[str(u)][:,0:120].min().astype('int64'),LUT_G[str(u)][:,0:120].max().astype('int64'),bit_check(LUT_G[str(u)][:,0:120].astype('int64'))))
            print('Layer B:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_B[str(u)][:,0:120].min().astype('int64'),LUT_B[str(u)][:,0:120].max().astype('int64'),bit_check(LUT_B[str(u)][:,0:120].astype('int64'))))
            
            bit_sum_left.append(bit_check(LUT_R[str(u)][:,0:120].astype('int64')))
            bit_sum_left.append(bit_check(LUT_G[str(u)][:,0:120].astype('int64')))
            bit_sum_left.append(bit_check(LUT_B[str(u)][:,0:120].astype('int64')))
        print("="*50)
        print("Check RIGHT LUT BITS TOTAL")        
        bit_sum_right=[]
        for u in LUT_gray:
            print('Layer R:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_R[str(u)][:,120:].min().astype('int64'),LUT_R[str(u)][:,120:].max().astype('int64'),bit_check(LUT_R[str(u)][:,120:].astype('int64'))))
            print('Layer G:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_G[str(u)][:,120:].min().astype('int64'),LUT_G[str(u)][:,120:].max().astype('int64'),bit_check(LUT_G[str(u)][:,120:].astype('int64'))))
            print('Layer B:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_B[str(u)][:,120:].min().astype('int64'),LUT_B[str(u)][:,120:].max().astype('int64'),bit_check(LUT_B[str(u)][:,120:].astype('int64'))))
            
            bit_sum_right.append(bit_check(LUT_R[str(u)][:,120:].astype('int64')))
            bit_sum_right.append(bit_check(LUT_G[str(u)][:,120:].astype('int64')))
            bit_sum_right.append(bit_check(LUT_B[str(u)][:,120:].astype('int64')))
                
        print('Left bits : {}'.format(np.sum(bit_sum_left)))
        print('Right bits : {}'.format(np.sum(bit_sum_right)))
        
        print('192 divide 2')            
        LUT_R[str(LUT_gray[-1])]=(LUT_R[str(LUT_gray[-1])]/4)#.clip(-254,255)
        LUT_G[str(LUT_gray[-1])]=(LUT_G[str(LUT_gray[-1])]/4)
        LUT_B[str(LUT_gray[-1])]=(LUT_B[str(LUT_gray[-1])]/4)
        bit_sum_right=[]
        bit_sum_left=[]
        for u in LUT_gray:
        
            bit_sum_left.append(bit_check(LUT_R[str(u)][:,0:120].astype('int64')))
            bit_sum_left.append(bit_check(LUT_G[str(u)][:,0:120].astype('int64')))
            bit_sum_left.append(bit_check(LUT_B[str(u)][:,0:120].astype('int64')))
            bit_sum_right.append(bit_check(LUT_R[str(u)][:,120:].astype('int64')))
            bit_sum_right.append(bit_check(LUT_G[str(u)][:,120:].astype('int64')))
            bit_sum_right.append(bit_check(LUT_B[str(u)][:,120:].astype('int64')))
        
        ############限制補償overange##############
        LUT_R[str(LUT_gray[-1])]=(LUT_R[str(LUT_gray[-1])]).clip(-1020,1023)
        LUT_G[str(LUT_gray[-1])]=(LUT_G[str(LUT_gray[-1])]).clip(-1020,1023)
        LUT_B[str(LUT_gray[-1])]=(LUT_B[str(LUT_gray[-1])]).clip(-1020,1023)
        ############限制補償overange##############
        
        print('Left bits : {}'.format(np.sum(bit_sum_left)))
        print('Right bits : {}'.format(np.sum(bit_sum_right)))
            
        
    
        #=======================================#
        #csv補償表{Left}
        #=======================================#
        print('Generate LUT File')
        header_layer=np.array([[len(LUT_gray),0],[int(120),int(540)]])
        #LUT_gray_10=(32,64,128,256,384,512,640,768,896,1023)
        
        
        strtime=time.strftime("%Y%m%d%H%M%S")
        prefix_name='Demura_LUT'+'_'+strtime+'_'+num+'_Left' #name rule LUTname + time stamp[YYYY/mm/dd/HH/MM/SS]
        
        file_name=prefix_name+'_normal.csv'

        with open(os.path.join(save_path,file_name), 'w', newline='') as file:
            mywriter = csv.writer(file, delimiter=',')
            mywriter.writerows(header_layer)
        
            for i in range(len(LUT_gray)):
                header_red=np.array([['Red','Level'+" "+str(i+1),LUT_gray[i]]])
                
                mywriter.writerows(header_red)
                mywriter.writerows(LUT_R[str(LUT_gray[i])][:,0:120].astype('int64'))
                
                header_green=np.array([['Green','Level'+" "+str(i+1),LUT_gray[i]]])
            
                mywriter.writerows(header_green)
                mywriter.writerows(LUT_G[str(LUT_gray[i])][:,0:120].astype('int64'))
                
                
                header_blue=np.array([['Blue','Level'+" "+str(i+1),LUT_gray[i]]])
                mywriter.writerows(header_blue)
                mywriter.writerows(LUT_B[str(LUT_gray[i])][:,0:120].astype('int64'))
                
       

        print('Generate LUT File')
        header_layer=np.array([[len(LUT_gray),0],[int(120),int(540)]])
        #LUT_gray_10=(32,64,128,256,384,512,640,768,896,1023)
        strtime=time.strftime("%Y%m%d%H%M%S")
        prefix_name='Demura_LUT'+'_'+strtime+'_'+num+'_Right' #name rule LUTname + time stamp[YYYY/mm/dd/HH/MM/SS]
        file_name=prefix_name+'_normal.csv'
        
        with open(os.path.join(save_path,file_name), 'w', newline='') as file:
            #=======================================#
            #csv補償表{right}
            #=======================================#
            mywriter = csv.writer(file, delimiter=',')
            mywriter.writerows(header_layer)
        
            for i in range(len(LUT_gray)):
                header_red=np.array([['Red','Level'+" "+str(i+1),LUT_gray[i]]])
                
                mywriter.writerows(header_red)
                mywriter.writerows(LUT_R[str(LUT_gray[i])][:,120:].astype('int64'))
                
                header_green=np.array([['Green','Level'+" "+str(i+1),LUT_gray[i]]])
            
                mywriter.writerows(header_green)
                mywriter.writerows(LUT_G[str(LUT_gray[i])][:,120:].astype('int64'))
                
                
                header_blue=np.array([['Blue','Level'+" "+str(i+1),LUT_gray[i]]])
                mywriter.writerows(header_blue)
                mywriter.writerows(LUT_B[str(LUT_gray[i])][:,120:].astype('int64'))
    else:
        if model =='Y136':
            print("="*50)
            print("Check LEFT LUT BITS TOTAL")        
            bit_sum_left=[]
            for u in LUT_gray:
                print('Layer R:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_R[str(u)][:,:].min().astype('int64'),LUT_R[str(u)][:,:].max().astype('int64'),bit_check(LUT_R[str(u)][:,:].astype('int64'))))
                print('Layer G:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_G[str(u)][:,:].min().astype('int64'),LUT_G[str(u)][:,:].max().astype('int64'),bit_check(LUT_G[str(u)][:,:].astype('int64'))))
                print('Layer B:{} Min: {} , Max: {} , bit: {}'.format(u,LUT_B[str(u)][:,:].min().astype('int64'),LUT_B[str(u)][:,:].max().astype('int64'),bit_check(LUT_B[str(u)][:,:].astype('int64'))))
                
                bit_sum_left.append(bit_check(LUT_R[str(u)][:,:].astype('int64')))
                bit_sum_left.append(bit_check(LUT_G[str(u)][:,:].astype('int64')))
                bit_sum_left.append(bit_check(LUT_B[str(u)][:,:].astype('int64')))
            print("="*50)
            
            
                    
            LUT_R[str(LUT_gray[-1])]=LUT_R[str(LUT_gray[-1])]/4
            LUT_G[str(LUT_gray[-1])]=LUT_G[str(LUT_gray[-1])]/4
            LUT_B[str(LUT_gray[-1])]=LUT_B[str(LUT_gray[-1])]/4
                
        
        
        print('Generate LUT File')
        header_layer=np.array([[len(LUT_gray),0],[int(resolution_x),int(resolution_y)]])
        #LUT_gray_10=(32,64,128,256,384,512,640,768,896,1023)

        strtime=time.strftime("%Y%m%d%H%M%S")
        prefix_name='Demura_LUT'+'_'+strtime+'_'+num #name rule LUTname + time stamp[YYYY/mm/dd/HH/MM/SS]

        file_name=prefix_name+'.csv'

        with open(os.path.join(save_path,file_name), 'w', newline='') as file:
            mywriter = csv.writer(file, delimiter=',')
            mywriter.writerows(header_layer)

            for i in range(len(LUT_gray)):
                header_red=np.array([['Red','Level'+" "+str(i+1),LUT_gray[i]]])
                
                mywriter.writerows(header_red)
                mywriter.writerows(LUT_R[str(LUT_gray[i])].astype('int64'))
                
                header_green=np.array([['Green','Level'+" "+str(i+1),LUT_gray[i]]])
            
                mywriter.writerows(header_green)
                mywriter.writerows(LUT_G[str(LUT_gray[i])].astype('int64'))
                
                
                header_blue=np.array([['Blue','Level'+" "+str(i+1),LUT_gray[i]]])
                mywriter.writerows(header_blue)
                mywriter.writerows(LUT_B[str(LUT_gray[i])].astype('int64'))
                
    showinfo(title='Selected File', message="LUT save in "+os.path.join(save_path,file_name))



def calibrate_color_ratio_XYZ_model(ca410_data,target_L,target_x,target_y):
    
    r1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=261,max_rows=256,usecols=(1,2,3))
    g1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=520,max_rows=256,usecols=(1,2,3))
    b1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=779,max_rows=256,usecols=(1,2,3))
    r1[0,1]=0
    g1[0,1]=0
    b1[0,1]=0
    
    rx_ip1d=interp1d(r1[:,1],r1[:,0], fill_value='extrapolate')
    rz_ip1d=interp1d(r1[:,1],r1[:,2], fill_value='extrapolate')    
    gx_ip1d=interp1d(g1[:,1],g1[:,0], fill_value='extrapolate')
    gz_ip1d=interp1d(g1[:,1],g1[:,2], fill_value='extrapolate')    
    bx_ip1d=interp1d(b1[:,1],b1[:,0], fill_value='extrapolate')
    bz_ip1d=interp1d(b1[:,1],b1[:,2], fill_value='extrapolate')    
    
    
    ry_ip1d=interp1d([i for i in range(256)],r1[:,1], fill_value='extrapolate')
    gy_ip1d=interp1d([i for i in range(256)],g1[:,1], fill_value='extrapolate')
    by_ip1d=interp1d([i for i in range(256)],b1[:,1], fill_value='extrapolate')
    
    rt_array=[]
    gt_array=[]
    bt_array=[]
  
    r_dg=interp1d(r1[:,1]/np.max(r1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    g_dg=interp1d(g1[:,1]/np.max(g1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    b_dg=interp1d(b1[:,1]/np.max(b1[:,1]),[i for i in range(256)], fill_value='extrapolate')
    
    nr=r_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    ng=g_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    nb=b_dg([(i/255)**2.2 for i in range(256)]).astype('int64')
    
    indexR=nr[[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]
    indexG=ng[[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]
    indexB=nb[[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]

    Tgray=[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]
    dg=[]
    wxx=[]
    wyy=[]
    fig1= plt.figure(num=1)
    fig1,ax=plt.subplots(2,3,figsize=(12,8))
    plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    for gray in range(len(indexR)): #r1.Tone.astype(np.int32).values: 
        #plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
        #gray=1
        #0 row -1是找最接近的最後一個
        wx=[]
        wy=[]
        
        r=indexR[gray]
        g=indexG[gray]
        b=indexB[gray]
        
        for loop in range(10):
            RX, RY, RZ =rx_ip1d(ry_ip1d(r)),ry_ip1d(r),rz_ip1d(ry_ip1d(r))#float(r1.X.iloc[r]),float(r1.Y.iloc[r]),float(r1.Z.iloc[r])
            GX, GY, GZ =gx_ip1d(gy_ip1d(g)),gy_ip1d(g),gz_ip1d(gy_ip1d(g))#float(g1.X.iloc[g]),float(g1.Y.iloc[g]),float(g1.Z.iloc[g])
            BX, BY, BZ =bx_ip1d(by_ip1d(b)),by_ip1d(b),bz_ip1d(by_ip1d(b))# float(b1.X.iloc[b]),float(b1.Y.iloc[b]),float(b1.Z.iloc[b])
            R_sum = RX+RY+RZ
            G_sum = GX+GY+GZ
            B_sum = BX+BY+BZ
            alfa = RY-target_y*(RX+RY+RZ)
            beta = RX-target_x*(RX+RY+RZ)
            constantB = (beta*(target_y*B_sum-BY)-alfa*(target_x*B_sum-BX))/(alfa*(target_x*G_sum-GX)-beta*(target_y*G_sum-GY))
            constantA = (constantB*(target_x*G_sum-GX)+target_x*B_sum-BX)/(RX-target_x*R_sum)
            ratio_R = constantA
            ratio_G = constantB
            
            rt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_R*RY/(ratio_R*RY+ratio_G*GY+BY))).clip(r1[:,1][0],r1[:,1][-1])
            gt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_G*GY/(ratio_R*RY+ratio_G*GY+BY))).clip(g1[:,1][0],g1[:,1][-1])
            bt=(target_L*((Tgray[gray]/255)**2.2)*(BY/(ratio_R*RY+ratio_G*GY+BY))).clip(b1[:,1][0],b1[:,1][-1])
            
            wX=RX+GX+BX
            wY=RY+GY+BY
            wZ=RZ+GZ+BZ
            wx.append(wX/(wX+wY+wZ))
            wy.append(wY/(wX+wY+wZ))
            
            
            
            #print(rt,gt,bt)
            rtmp=r
            gtmp=g
            btmp=b
            #找目標亮度
            r=r_dg(rt/np.max(r1[:,1])).round(4)#r=np.abs(r1.Y.astype(np.float64) - rt).argmin()
            g=g_dg(gt/np.max(g1[:,1])).round(4)#g=np.abs(g1.Y.astype(np.float64) - gt).argmin()
            b=b_dg(bt/np.max(b1[:,1])).round(4)#b=np.abs(b1.Y.astype(np.float64) - bt).argmin()
            
            
            
            if loop==8:
                newr=r_dg(rt/np.max(r1[:,1])).round(4)#67.50956154862239  #97
                newg=g_dg(gt/np.max(g1[:,1])).round(4)#166.8327090883952 #106
                newb=b_dg(bt/np.max(b1[:,1])).round(4)#15.657729362982373 #85
                print(newr,newg,newb,loop)
                
                dg.append(np.array([gray,newr,newg,newb]))
                rt_array.append(rt)
                gt_array.append(gt)
                bt_array.append(bt)

            #再次找灰階最接近的值
            if rtmp==r and gtmp==g and btmp==b:
                newr=r_dg(rt/np.max(r1[:,1])).round(4)#67.50956154862239  #97 
                newg=g_dg(gt/np.max(g1[:,1])).round(4)#166.8327090883952 #106  
                newb=b_dg(bt/np.max(b1[:,1])).round(4)#15.657729362982373 #85
                print(newr,newg,newb,loop)
                
                dg.append(np.array([gray,newr,newg,newb]))
                rt_array.append(rt)
                gt_array.append(gt)
                bt_array.append(bt)
    
                
                break
        
        wX=RX+GX+BX
        wY=RY+GY+BY
        wZ=RZ+GZ+BZ
        wxx.append(wX/(wX+wY+wZ))
        wyy.append(wY/(wX+wY+wZ))
        
        ax[0,0].scatter(wx,wy)
        ax[0,0].plot(wx,wy)
    #化點
    dg_df=np.array(dg)
    #dg_df=pd.DataFrame(np.array(dg),columns=['gray','R','G','B'])
    
    plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",axes=ax[0,1],bounding_box=(-0.1, 1, -0.1, 1))
    ax[0,1].scatter(wxx,wyy)
    ax[0,1].set_xlim(-0.08, 0.8)
    ax[0,1].set_ylim(-0.08, 0.9)
    
    ax[0,2].plot(Tgray,dg_df[:,1],'-r',marker='.')
    ax[0,2].plot(Tgray,dg_df[:,2],'-g',marker='.')
    ax[0,2].plot(Tgray,dg_df[:,3],'-b',marker='.')
    ax[0,2].set_xlim(0,255)
    ax[0,2].set_xticks(Tgray)
    
    
   
    ax[1,0].plot(dg_df[:,0],rt_array,'--r',label='R Lum Target')
    ax[1,0].plot(dg_df[:,0],
            ry_ip1d(dg_df[:,1]),
            '-r',label='R Lum real ca410')
    ax[1,0].legend()
    

    ax[1,1].plot(dg_df[:,0],gt_array,'--g',label='G Lum Target')#,marker='^')
    ax[1,1].plot(dg_df[:,0],
            gy_ip1d(dg_df[:,2]),
            '-g',label='G Lum Real ca410')
    ax[1,1].legend(loc='best')
    

    ax[1,2].plot(dg_df[:,0],bt_array,'--b',label='B Lum Target')#,marker='^')
    ax[1,2].plot(dg_df[:,0],
            by_ip1d(dg_df[:,3]),
            '-b',label='B Lum Real ca410')
    ax[1,2].legend(loc='best')

    
    new_cal=figure_window(root)

    new_cal.creat_matplotlib(fig1)
    return rt_array,gt_array,bt_array

def output_DG(save_path,prefix_name,ca410_data,rt,gt,bt):
    
    rt=np.insert(rt, 0,0)
    gt=np.insert(gt, 0,0)
    bt=np.insert(bt, 0,0)

    #gray=np.array([0,8,16,32,64,96,128,160,192,224,256])*16
    gray=np.array([0,7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255])*16
    r_t_it1d=interp1d(gray,rt,fill_value='extrapolate')
    g_t_it1d=interp1d(gray,gt,fill_value='extrapolate')
    b_t_it1d=interp1d(gray,bt,fill_value='extrapolate')

    nr_t=r_t_it1d([i for i in range(4096)]).clip(0,4095)
    ng_t=g_t_it1d([i for i in range(4096)]).clip(0,4095)
    nb_t=b_t_it1d([i for i in range(4096)]).clip(0,4095)

    r1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=261,max_rows=256,usecols=(1,2,3))
    g1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=520,max_rows=256,usecols=(1,2,3))
    b1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=779,max_rows=256,usecols=(1,2,3))
    
    r1[0,1]=0
    g1[0,1]=0
    b1[0,1]=0
    #b1=np.sort(b1[:,1])
    
    r_dg=interp1d(r1[:,1],[i*256 for i in range(256)], fill_value='extrapolate')
    g_dg=interp1d(g1[:,1],[i*256 for i in range(256)], fill_value='extrapolate')
    b_dg=interp1d(b1[:,1],[i*256 for i in range(256)], fill_value='extrapolate')
    
    R=r_dg(nr_t).astype('uint32').clip(0,65535)
    G=g_dg(ng_t).astype('uint32').clip(0,65535)
    B=(b_dg(nb_t).astype('uint32')).clip(0,65535)
    
    DG=[]
    for i in range(len(R)):
        DG.append(hex(R[i]//256)[2:].upper().zfill(2))
        DG.append(hex(R[i]%256)[2:].upper().zfill(2))
    for i in range(len(R)):
        DG.append(hex(G[i]//256)[2:].upper().zfill(2))
        DG.append(hex(G[i]%256)[2:].upper().zfill(2))
    for i in range(len(R)):
        DG.append(hex(B[i]//256)[2:].upper().zfill(2))
        DG.append(hex(B[i]%256)[2:].upper().zfill(2))
    
    
    addr=['@'+hex(i)[2:].upper()+" " for i in range(24576,49152,1)]
    lut=''
    for i in range(len(addr)):
        tmp=addr[i]+DG[i]+'\n'
        if i == len(addr)-1:
            tmp=addr[i]+DG[i]
        
        lut=lut+tmp
    
    lut=lut+'\n'+'@021B 10'
        
    file_name=prefix_name+'.DESIGN_HEX_ROM'
    text_file = open(os.path.join(save_path,file_name), "w")
    text_file.write(lut)
         
    print("LUT save in "+os.path.join(save_path,file_name))
    
    

    
def demura_task():
    p_val_label.grid(column=0,row=0)
    progress.grid(column=0,row=1)
    percent=np.array([0.125,0.25,0.375,0.5,0.625,0.75,0.875,1])
    indexer_p=0
    resolution_x,resolution_y,model=get_resxy()
    
    DataYR,DataYG,DataYB,graylv=L4A_Demura(dir_path_String.get())
    progress['value'] = 10
    p_val_string.set('Loading RVS Data...')
    global rt,gt,bt
    cp_R255=[]
    cp_G255=[]
    cp_B255=[]
    
   
    for i in range(0,resolution_y*resolution_x):
        
        if model =='Y161' and L4A_link.get()==0:
            rs=interp1d(DataYR[i],graylv[0], fill_value='extrapolate')
            gs=interp1d(DataYG[i],graylv[1], fill_value='extrapolate')           
            bs=interp1d(DataYB[i],graylv[2], fill_value='extrapolate')
        else:
                
            rs=interp1d(DataYR[i],graylv, fill_value='extrapolate')
            gs=interp1d(DataYG[i],graylv, fill_value='extrapolate')               
            bs=interp1d(DataYB[i],graylv, fill_value='extrapolate')
            
        
        
        cp_R255.append(rs(rt).clip(0,255))
        cp_G255.append(gs(gt).clip(0,255))
        cp_B255.append(bs(bt).clip(0,255))
        
        tmp_indexer_p=indexer_p
        
        status=np.around((i/(resolution_y*resolution_x)),3)
        indexer_p=np.abs(percent-status).argmin()
        
        if indexer_p !=tmp_indexer_p:
            progress['value'] = 10+10*(indexer_p+1)
            root.update()
        p_val_string.set(f'{i}/{resolution_y*resolution_x}')
    root.update()
        #pbar.update(1)
  
    gen_cpimg(cp_R255,cp_G255,cp_B255)
    progress['value'] = 95
    p_val_string.set('Output CP image')
    root.update()
    gen_LUT(cp_R255,cp_G255,cp_B255)
    progress['value'] = 100
    root.update()
    
    showinfo(title='New Update', message="Demura Compelete")
    p_val_label.grid_forget()
    progress.grid_forget()




def new_window():
    

    posx=0
    posy=0
    com=cb.get()
    
    start=int(0)
    delay=float(0.01)
    data=[]
    

    
    
    res_x,res_y,model=get_resxy()
    root.geometry('830x730+%d+%d'%(ws/2,hs/2-350))
    
            
            
    print('Open Pattern')
    global open_flag,mask_craet
    mask_craet=np.ones((1080,1920,3))
    open_flag=1
    open_window_btn.destroy()
    window=tk.Toplevel(root)
    window.attributes('-toolwindow', True)
    window.resizable(0,0)

    window.overrideredirect(True)
    #window.attributes('-fullscreen', 1)

    #slider current value
    R_int = tk.IntVar()
    G_int = tk.IntVar()
    B_int = tk.IntVar()
    W_int = tk.IntVar()
    img_int=tk.IntVar()
    pat_bg = tk.IntVar()
    
    
    XString=tk.StringVar()
    YString=tk.StringVar()
    CountString=tk.IntVar()
    XString.set(posx)
    YString.set(posy)
    CountString.set(start)
    resultString=tk.StringVar()
    pat_delay_float=tk.DoubleVar()
    pat_delay_float.set(pat_delay)
    gamma_step_int=tk.IntVar()
    gamma_step_int.set(gamma_step)
    


    Gray_String=tk.IntVar()
    
    
    y_start,y_end,x_start,x_end=0,res_y,0,res_x
    
    
    def load_lut(dir_path):
        img_path=[]
        #LUT_gray_8 = [8,16,32,64,96,128,160,192,224,255]
        LUT_gray_8 = [8,16,32,64,192]

        for i in LUT_gray_8:
            img_path.append(os.path.join(dir_path,'{color}{gray}_2.bmp'.format(color='W',gray=i)))
        
        R_LUT={}
        G_LUT={}
        B_LUT={}
        R_LUT[0]=0*np.ones((y_end,x_end)).flatten()
        G_LUT[0]=0*np.ones((y_end,x_end)).flatten()
        B_LUT[0]=0*np.ones((y_end,x_end)).flatten()
        
        for i in range(len(LUT_gray_8)):
            R_LUT[LUT_gray_8[i]]=np.array(PIL.Image.open(img_path[i]).convert('RGB'))[y_start:y_end,x_start:x_end][:,:,0].flatten()
            G_LUT[LUT_gray_8[i]]=np.array(PIL.Image.open(img_path[i]).convert('RGB'))[y_start:y_end,x_start:x_end][:,:,1].flatten()
            B_LUT[LUT_gray_8[i]]=np.array(PIL.Image.open(img_path[i]).convert('RGB'))[y_start:y_end,x_start:x_end][:,:,2].flatten()
        
        LUT_gray_8.insert(0,0)

        #LUT_gray_8=[0,8,16,32,64,192,255]
        R_linfit = interp1d(LUT_gray_8, np.array(tuple(R_LUT.values())).T, axis=1, fill_value='extrapolate')
        G_linfit = interp1d(LUT_gray_8, np.array(tuple(G_LUT.values())).T, axis=1, fill_value='extrapolate')           
        B_linfit = interp1d(LUT_gray_8, np.array(tuple(B_LUT.values())).T, axis=1, fill_value='extrapolate')
        
        return R_linfit,G_linfit,B_linfit
    
    if lut_dir_path_String.get()!="":
        R_linfit,G_linfit,B_linfit=load_lut(lut_dir_path_String.get())
    
    def load_image_file():
        if img_dir_path_String.get()!="":
            img_path_list=[]
            img_path_list.append(os.path.join(img_dir_path_String.get(),os.listdir(img_dir_path_String.get())[0]))
            for images in os.listdir(img_dir_path_String.get()):
                
                # check if the image ends with png or jpg or jpeg
                if (images.endswith(".png")
                    or images.endswith(".PNG") 
                    or images.endswith(".jpg") 
                    or images.endswith(".JPG")
                    or images.endswith(".jpeg")
                    or images.endswith(".Bmp")
                    or images.endswith(".BMP")
                    or images.endswith(".bmp") ):
                    # display
                    print(os.path.join(img_dir_path_String.get(),images))
                    img_path_list.append(os.path.join(img_dir_path_String.get(),images))
        return img_path_list    
    
    if image_demura_npy.get()==1:
       
        indexer=np.array([i for i in range(res_x*res_y)])
        with open(os.path.join(dir_path_String.get(),'Demura.npy'), 'rb') as f:
            Rdemura = np.load(f)
            Gdemura = np.load(f)
            Bdemura = np.load(f)
            
            
    def demura_switch():
        global demura_sw
        demura_sw= (demura_sw is False)
        creat_image()
        
        window.geometry("+{}+{}".format(XString.get(),YString.get()))
        
        return demura_sw
    
    def mask_switch():
        global mask_sw
        mask_sw= (mask_sw is False)
        
        
        
        creat_image()
        
        window.geometry("+{}+{}".format(XString.get(),YString.get()))
        
    def creat_mask():
        global mask_craet
        x_point=int(simpledialog.askstring(title="X",
                              prompt="SPLIT X ="))
        y_point=int(simpledialog.askstring(title="Y",
                              prompt="SPLIT Y ="))
        
        res_x,res_y,model=get_resxy()
        mask_craet=np.ones((1080,1920,3))        
        
        mask_x=[i for i in range(0,res_x+1,int(res_x/x_point))][1:-1]
        mask_y=[i for i in range(0,res_y+1,int(res_y/y_point))][1:-1]
        
        mask_craet[:,mask_x,:]=0
        mask_craet[mask_y,:,:]=0
        return mask_craet
    
    def slider_changed(event):

    
            
        slider_label_R.configure(text='R:{}'.format(str(R_int.get()).zfill(3)))
        slider_label_G.configure(text='G:{}'.format(str(G_int.get()).zfill(3)))
        slider_label_B.configure(text='B:{}'.format(str(B_int.get()).zfill(3)))
        slider_label_W.configure(text='W:{}'.format(str(W_int.get()).zfill(3)))
        if img_dir_path_String.get()!="":
            slider_label_P.configure(text='P:{}'.format(str(img_int.get()).zfill(3)))


        creat_image()
        #window.geometry("+{}+{}".format(XString.get(),YString.get()))
        
    #label for the slider
    slider_label_R = ttk.Label(frame_slider, text='R:{}'.format(str(R_int.get()).zfill(3)))
    slider_label_G = ttk.Label(frame_slider, text='G:{}'.format(str(G_int.get()).zfill(3)))
    slider_label_B = ttk.Label(frame_slider, text='B:{}'.format(str(B_int.get()).zfill(3)))
    slider_label_W = ttk.Label(frame_slider, text='W:{}'.format(str(W_int.get()).zfill(3)))
    if img_dir_path_String.get()!="":
        slider_label_P = ttk.Label(frame_slider, text='P:{}'.format(str(img_int.get()).zfill(3)))

    
    
    
    
    
    
    #slider
    slider_R = ttk.Scale(frame_slider,from_=0,to=255,orient='horizontal',
                       command=slider_changed,variable=R_int
                       )
    slider_G = ttk.Scale(frame_slider,from_=0,to=255,orient='horizontal',
                       command=slider_changed,variable=G_int
                       )
    slider_B = ttk.Scale(frame_slider,from_=0,to=255,orient='horizontal',
                       command=slider_changed,variable=B_int
                       )
    slider_W = ttk.Scale(frame_slider,from_=0,to=255,orient='horizontal',
                       command=slider_changed,variable=W_int
                       )
    if img_dir_path_String.get()!="":
        img_path_list=load_image_file()
        slider_img = ttk.Scale(frame_slider,from_=0,to=len(img_path_list)-1,
                               orient='horizontal',
                               command=slider_changed,variable=img_int)
        slider_img.grid(column=1,row=4,sticky='we')

        slider_label_P.grid(column=0,row=4,sticky='w')    
        img_left=tk.Button(frame_slider, text = "◄", command = lambda: color_change("IMAGE",-1),width=1)
        img_right=tk.Button(frame_slider, text = "►", command = lambda: color_change("IMAGE",1),width=1)
        
        img_left.grid(column=2,row=4,sticky='we')
        img_right.grid(column=3,row=4,sticky='we')
    
    
    entry_X_label = ttk.Label(frame_pos, text='POS X')
    entry_Y_label = ttk.Label(frame_pos, text='POS Y')
    entry_count_label = ttk.Label(frame_pos, text='Count')
    entry_pat_delay_label=ttk.Label(frame_pos, text='Delay')
    entry_gamma_step_label=ttk.Label(frame_pos, text='Step')
    
    
    entry_X = tk.Entry(frame_pos, width=5, textvariable=XString)
    entry_Y = tk.Entry(frame_pos, width=5, textvariable=YString)
    entry_count = tk.Entry(frame_pos, width=5, textvariable=CountString)
    entry_pat_delay = tk.Entry(frame_pos, width=5, textvariable=pat_delay_float)
    entry_gamma_step = tk.Entry(frame_pos, width=5, textvariable=gamma_step_int)
    
    
    pos_x1 = tk.IntVar()
    pos_y1 = tk.IntVar()
    pos_x2 = tk.IntVar()
    pos_y2=tk.IntVar()
    
    pat_bg.set(64)
    pos_x1.set(0)
    pos_y1.set(0)
    pos_x2.set(res_x)
    pos_y2.set(res_y)
    
    entry_pat_X= tk.Entry(frame_pos, width=5, textvariable=pos_x1)
    entry_pat_Y= tk.Entry(frame_pos, width=5, textvariable=pos_y1)
    
    entry_pat_X_label = ttk.Label(frame_pos, text='X-Talk X')
    entry_pat_Y_label = ttk.Label(frame_pos, text='Y-Talk Y')
    
    entry_pat_width= tk.Entry(frame_pos, width=5, textvariable=pos_x2)
    entry_pat_length= tk.Entry(frame_pos, width=5, textvariable=pos_y2)

    entry_pat_width_label = ttk.Label(frame_pos, text='PAT W')
    entry_pat_length_label = ttk.Label(frame_pos, text='PAT L')
    
    
    slider_R.grid(column=1,row=0,sticky='we',padx=10)
    slider_G.grid(column=1,row=1,sticky='we',padx=10)
    slider_B.grid(column=1,row=2,sticky='we',padx=10)
    slider_W.grid(column=1,row=3,sticky='we',padx=10)
    if img_dir_path_String.get()!="":
        slider_img.grid(column=1,row=4,sticky='we')
    
    entry_gray = tk.Entry(frame_chip, width=5, textvariable=Gray_String)
    entry_gray.grid(column=0,row=0,sticky='w')
    
    
    entry_X_label.grid(column=0, row=0, sticky=tk.W)
    entry_Y_label.grid(column=0, row=1, sticky=tk.W)
    
    entry_pat_X_label.grid(column=2, row=0, sticky=tk.W)
    entry_pat_Y_label.grid(column=2, row=1, sticky=tk.W)
    
    entry_pat_width_label.grid(column=4, row=0, sticky=tk.W)
    entry_pat_length_label.grid(column=4, row=1, sticky=tk.W)
    
    
    entry_count_label.grid(column=0, row=4, sticky=tk.W)
    
    entry_X.grid(column=1, row=0, sticky=tk.W)
    entry_Y.grid(column=1, row=1, sticky=tk.W)
    
    entry_pat_X.grid(column=3, row=0, sticky=tk.W)
    entry_pat_Y.grid(column=3, row=1, sticky=tk.W)
    
    entry_pat_width.grid(column=5, row=0, sticky=tk.W)
    entry_pat_length.grid(column=5, row=1, sticky=tk.W)
    
    
    
    entry_count.grid(column=1, row=4, sticky=tk.W)
    
   
    
    gamma_check_label=ttk.Label(frame_pos, text='Gamma')
    gamma_check_label.grid(column=0,row=5, sticky=tk.W)
    
    
    
    entry_pat_delay_label.grid(column=0, row=6, sticky=tk.W)
    entry_gamma_step_label.grid(column=0, row=7, sticky=tk.W)
    
    entry_pat_delay.grid(column=1, row=6, sticky=tk.W)
    entry_gamma_step.grid(column=1, row=7, sticky=tk.W)
    R=R_int.get()
    G=G_int.get()
    B=B_int.get()
    
    resultString.set("( {} , {} , {} )".format(R,G,B))
    canvas = tk.Canvas(window, width = res_x, height = res_y,highlightthickness=0)
    
    canvas.pack()
    
    imgbox = canvas.create_image(0, 0, image=None, anchor='nw')
    
    
    gamma_R_link = tk.IntVar()
    gamma_G_link = tk.IntVar()
    gamma_B_link = tk.IntVar()
    gamma_W_link = tk.IntVar()
    
    #tk.Checkbutton(frame_pos, text="R", variable=gamma_R_link,onvalue=1, offvalue=0).grid(column=1,row=5, sticky=tk.W,ipadx=5,padx=1)
    #tk.Checkbutton(frame_pos, text="G", variable=gamma_G_link,onvalue=1, offvalue=0).grid(column=2,row=5, sticky=tk.W,ipadx=5,padx=1)
    #tk.Checkbutton(frame_pos, text="B", variable=gamma_B_link,onvalue=1, offvalue=0).grid(column=3,row=5, sticky=tk.W,ipadx=5,padx=1)
    #tk.Checkbutton(frame_pos, text="W", variable=gamma_W_link,onvalue=1, offvalue=0).grid(column=4,row=5, sticky=tk.W,ipadx=5,padx=1)
    mb=  tk.Menubutton ( frame_pos, text="Select Color", relief=tk.RAISED )
    mb.grid(column=1,row=5, sticky=tk.W,ipadx=5,padx=1)
    mb.menu  =  tk.Menu ( mb, tearoff = 0 )
    mb["menu"]  =  mb.menu
 
    
    mb.menu.add_checkbutton ( label="R", variable=gamma_R_link)
    mb.menu.add_checkbutton ( label="G", variable=gamma_G_link)
    mb.menu.add_checkbutton ( label="B", variable=gamma_B_link)
    mb.menu.add_checkbutton ( label="W", variable=gamma_W_link)
    
    pat_fix_label=ttk.Label(frame_pos, text='Pat Fix Gray')
    pat_fix_label.grid(column=0,row=8, sticky=tk.W)
    
    pat_fix_link = tk.IntVar()
    tk.Checkbutton(frame_pos, text="Fix BG", variable=pat_fix_link,onvalue=1, offvalue=0).grid(column=1,row=8, sticky=tk.W)
    
    entry_gray_bg = tk.Entry(frame_pos, width=5, textvariable=pat_bg)
    entry_gray_bg.grid(column=2,row=8,sticky='w')
    rot_select_label=ttk.Label(frame_pos, text='Screen Rotation')
    rot_select_label.grid(column=3,row=8, sticky=tk.W)
    rot_select = ttk.Combobox(frame_pos, values=['0','180'],state="readonly", width=3)
    rot_select.grid(column=4,row=8, sticky=tk.W)
    rot_select.current(0)
    
    def image_array(B,G,R):
        if demura_sw is False:
            x1=pos_x1.get()
            y1=pos_y1.get()
            
            x2=pos_x2.get()
            y2=pos_y2.get()
            
            
            if pat_fix_link.get()==0:
                r_ch=np.ones((y2,x2)).astype(np.uint8)*R
                g_ch=np.ones((y2,x2)).astype(np.uint8)*G
                b_ch=np.ones((y2,x2)).astype(np.uint8)*B    
                
                blank_b=np.ones((1080,1920))*pat_bg.get()
                blank_g=np.ones((1080,1920))*pat_bg.get()
                blank_r=np.ones((1080,1920))*pat_bg.get()
                        
                blank_b[y1:y1+y2,x1:x1+x2]=b_ch[:y2,0:x2]
                blank_g[y1:y1+y2,x1:x1+x2]=g_ch[:y2:,0:x2]
                blank_r[y1:y1+y2,x1:x1+x2]=r_ch[:y2:,0:x2]
            else:
                r_ch=np.ones((y2,x2)).astype(np.uint8)*pat_bg.get()
                g_ch=np.ones((y2,x2)).astype(np.uint8)*pat_bg.get()
                b_ch=np.ones((y2,x2)).astype(np.uint8)*pat_bg.get()
                
                blank_b=np.ones((1080,1920))*R
                blank_g=np.ones((1080,1920))*G
                blank_r=np.ones((1080,1920))*B
                        
                blank_b[y1:y1+y2,x1:x1+x2]=b_ch[:y2,0:x2]
                blank_g[y1:y1+y2,x1:x1+x2]=g_ch[:y2:,0:x2]
                blank_r[y1:y1+y2,x1:x1+x2]=r_ch[:y2:,0:x2]
            
            
            
        else:
            if rot_select.get()=='180':
                rot=2
            else:
                rot=0
                
            r_ch=R_linfit(R).reshape((y_end,x_end)).clip(0,255)
            g_ch=G_linfit(G).reshape((y_end,x_end)).clip(0,255)
            b_ch=B_linfit(B).reshape((y_end,x_end)).clip(0,255)
            r_ch=np.rot90(r_ch,rot)
            g_ch=np.rot90(g_ch,rot)
            b_ch=np.rot90(b_ch,rot)
            blank_b=np.ones((1080,1920))*B
            blank_g=np.ones((1080,1920))*G
            blank_r=np.ones((1080,1920))*R
            blank_b[0:y_end,0:x_end]=b_ch[:y_end,0:x_end]
            blank_g[0:y_end,0:x_end]=g_ch[:y_end:,0:x_end]
            blank_r[0:y_end,0:x_end]=r_ch[:y_end:,0:x_end]
        return blank_b,blank_g,blank_r
    
    def creat_image():
        global mask_craet
        if img_int.get()==0:
            if W_int.get()==0:
                R=R_int.get()
                G=G_int.get()
                B=B_int.get()
                     
            else:
                R=W_int.get()
                G=W_int.get()
                B=W_int.get()
            
            
            blank_b,blank_g,blank_r=image_array(B,G,R)
            array=np.dstack([blank_r.astype('uint8'), blank_g.astype('uint8'),blank_b.astype('uint8')])

            if mask_sw==False:
                array=array
            else:
                array=array*mask_craet.astype('uint8')
            
        
        
        else:
            if rot_select.get()=='180':
                rot=2
            else:
                rot=0
            tmp=np.array(PIL.Image.open(img_path_list[img_int.get()]).convert('RGB').resize((res_x,res_y)))
            tmp=np.rot90(tmp,rot)
            img_r=tmp[:,:,0].flatten()
            img_g=tmp[:,:,1].flatten()
            img_b=tmp[:,:,2].flatten()
            
            if demura_sw is False:
                array=tmp
            else:
                    
                if image_demura_npy.get()==1:
                    R_demura=Rdemura[indexer,np.array(img_r)].reshape(y_end,x_end)
                    G_demura=Gdemura[indexer,np.array(img_g)].reshape(y_end,x_end)
                    B_demura=Bdemura[indexer,np.array(img_b)].reshape(y_end,x_end)
        
         
                    array=np.dstack([R_demura.astype('uint8'), G_demura.astype('uint8'),B_demura.astype('uint8')])
                else:
                    array=tmp
        
        image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(array))
        # update the image
        canvas.itemconfig(imgbox, image=image)
        # need to keep a reference of the image, otherwise it will be garbage collected
        canvas.image = image

    

        
        
        
    slider_label_R.grid(column=0,row=0,sticky='w',padx=1)
    slider_label_G.grid(column=0,row=1,sticky='w',padx=1)
    slider_label_B.grid(column=0,row=2,sticky='w',padx=1)    
    slider_label_W.grid(column=0,row=3,sticky='w',padx=1) 
    if img_dir_path_String.get()!="":
        slider_label_P.grid(column=0,row=4,sticky='w')    

    red_left=tk.Button(frame_slider, text = "◄", command = lambda: [color_change("RED",-1),slider_changed(event='Button-1')],width=1)
    red_right=tk.Button(frame_slider, text = "►", command = lambda: [color_change("RED",1),slider_changed(event='Button-1')],width=1)
    
    red_left.grid(column=2,row=0,sticky='we')
    red_right.grid(column=3,row=0,sticky='we')
    
    green_left=tk.Button(frame_slider, text = "◄", command = lambda: [color_change("GREEN",-1),slider_changed(event='Button-1')],width=1)
    green_right=tk.Button(frame_slider, text = "►", command = lambda: [color_change("GREEN",1),slider_changed(event='Button-1')],width=1)
    
    green_left.grid(column=2,row=1,sticky='we')
    green_right.grid(column=3,row=1,sticky='we')
    
    
    blue_left=tk.Button(frame_slider, text = "◄", command = lambda: [color_change("BLUE",-1),slider_changed(event='Button-1')],width=1)
    blue_right=tk.Button(frame_slider, text = "►", command = lambda: [color_change("BLUE",1),slider_changed(event='Button-1')],width=1)
    
    blue_left.grid(column=2,row=2,sticky='we')
    blue_right.grid(column=3,row=2,sticky='we')
    
    
    white_left=tk.Button(frame_slider, text = "◄", command = lambda: [color_change("WHITE",-1),slider_changed(event='Button-1')],width=1)
    white_right=tk.Button(frame_slider, text = "►", command = lambda: [color_change("WHITE",1),slider_changed(event='Button-1')],width=1)
    
    white_left.grid(column=2,row=3,sticky='we')
    white_right.grid(column=3,row=3,sticky='we')  

    creat_image()
    
    
    
    
    global ca410
    if ca410_link.get()==True:
        #if ca410_chk==False:
        
        ser=CA410(com)
        ser.Zcal()
            
        ca410_chk=True
    
    def close_window():
        global open_flag,ca410_chk
        if ca410_link.get()==True:
            ser.close()
        else:
            pass
        
        time.sleep(1)
        window.destroy()
        
        
        open_flag=0
        open_window_btn=tk.Button(frame_btn, text = "Open Pattern", command = lambda: new_window(),width=20)
        open_window_btn.grid(column=1, row=1, ipady=5, sticky=tk.W,padx=1)
    
    def meas():
#        
#        tmp_data=ser.SingleMeas()
#        #x,y,lv,X,Y,Z
#        print("lv:{},cx:{},cy:{},X:{},Y:{},Z:{}".format(tmp_data[0],tmp_data[1],tmp_data[2],tmp_data[3],tmp_data[4],tmp_data[5]))
#        
        global data_window
        if data_window is None:
            data_window=meas_window(root)
            
        if not data_window.winfo_exists():
            CountString.set(0)
            data_window=meas_window(root)
            #data_window.deiconify()   
        data_tmp=ser.SingleMeas_all(delay)
        #data_tmp=(0,1,2,3,4,5,6,7,8,9,10,11,12,13)#ser.SingleMeas_all(0.5)

        data_window.tree.insert("",'end',values=((CountString.get(),R_int.get(),G_int.get(),B_int.get())+data_tmp))
        data_window.tree.yview_moveto(1)
        #np.savetxt(os.path.join(os.getcwd(),'tmp.csv'), np.asarray(data), delimiter=',', header='R,G,B,X,Y,Z,x,y,lv,u",v",duv,Tcp,ld,pe')
        count = CountString.get()+1
        CountString.set(count)
        
    def Pause():
        global pause_check
        #print(ser.SingleMeas())
        pause_check=(pause_check==False)
        if pause_check==False:
            cal_btn3.configure(text='Pause')
        else:
            cal_btn3.configure(text='Continue')
    def test_function():
        global data_window
        if data_window is None:
            data_window=meas_window(root)
            
        if not data_window.winfo_exists():
            CountString.set(0)
            data_window=meas_window(root)
        
        tmp_data=(CountString.get(),1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
        data_window.tree.insert("",'end',values=(tmp_data))
        data_window.tree.yview_moveto(1)
        
    
    def Gamma():
        msg_box = tk.messagebox.askquestion('Clear Data', 'Entering gamma measurment mode will clear previous data! Do you want to proceed?',
                                        icon='warning')
        global data_window
        if data_window is None:
            data_window=meas_window(root)
            
        if not data_window.winfo_exists():
            CountString.set(0)
            data_window=meas_window(root)
            
        if msg_box == 'yes':
            data_window.clear_data()
            CountString.set(0)
            R_int.set(0)
            G_int.set(0)
            B_int.set(0)
            W_int.set(0)

            global pause_check,ca410_chk,data
            def creat_image2(i,j,k):

                R_int.set(i)
                G_int.set(j)
                B_int.set(k)
                if W_int.get()==0:
                    R=R_int.get()
                    G=G_int.get()
                    B=B_int.get()
                    slider_label_R.configure(text='R:{}'.format(str(R_int.get()).zfill(3)))
                    slider_label_G.configure(text='G:{}'.format(str(G_int.get()).zfill(3)))
                    slider_label_B.configure(text='B:{}'.format(str(B_int.get()).zfill(3)))
                    slider_label_W.configure(text='W:{}'.format(str(W_int.get()).zfill(3)))
                    
                else:
                    R=W_int.get()
                    G=W_int.get()
                    B=W_int.get()
                
    
                blank_b,blank_g,blank_r=image_array(B,G,R)
                
                array=np.dstack([blank_r.astype('uint8'), blank_g.astype('uint8'),blank_b.astype('uint8')])
                image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(array))
                # update the image
                canvas.itemconfig(imgbox, image=image)
                # need to keep a reference of the image, otherwise it will be garbage collected
                canvas.image = image
                    
           
            cal_btn3.configure(text='Pause')
            #data=[]
            gamma_step=gamma_step_int.get()
            pat_delay=pat_delay_float.get()
            
            gamma=[]
            print(gamma_R_link.get())
            if gamma_R_link.get()==1:
                
                for i in np.array([i for i in range(0,257,gamma_step)]).clip(0,255):
                    gamma.append([i,0,0])
            if gamma_G_link.get()==1:
                for i in np.array([i for i in range(0,257,gamma_step)]).clip(0,255):
                    gamma.append([0,i,0])
            if gamma_B_link.get()==1:
                for i in np.array([i for i in range(0,257,gamma_step)]).clip(0,255):
                    gamma.append([0,0,i])
            if gamma_W_link.get()==1:
                for i in np.array([i for i in range(0,257,gamma_step)]).clip(0,255):
                    gamma.append([i,i,i])
                
            count=CountString.get()
            
            while CountString.get()<len(gamma):
                
                if pause_check==False:
                    count=CountString.get()
    
                    i,j,k=gamma[count]
                    creat_image2(i,j,k)
                    window.update()
                    time.sleep(pat_delay)
                    data_tmp=ser.SingleMeas_all(delay)
                    #data_tmp=(0,1,2,3,4,5,6,7,8,9,10,11,12,13)#ser.SingleMeas_all(0.5)
    
                    data_window.tree.insert("",'end',values=((CountString.get(),i,j,k)+data_tmp))
                    data_window.tree.yview_moveto(1)
                    #np.savetxt(os.path.join(os.getcwd(),'tmp.csv'), np.asarray(data), delimiter=',', header='R,G,B,X,Y,Z,x,y,lv,u",v",duv,Tcp,ld,pe')
                    count=count+1
                    CountString.set(count)
                else:
    
                    break

            
            creat_image2(0,0,0)
            window.update()
            time.sleep(0.2)
            
            #strtime=time.strftime("%Y%m%d%H%M%S")
            #np.savetxt(os.path.join(os.getcwd(),'CA410_Gamma_results_{strtime}.csv'.format(strtime=strtime)), np.asarray(data), delimiter=',', header='R,G,B,X,Y,Z,x,y,lv,u",v",duv,Tcp,ld,pe')
            #print('Gammma data save in '+ os.path.join(os.getcwd(),'CA410_results_{strtime}.csv'.format(strtime=strtime)))
            window.update()
            CountString.set(0)
    
    
    if ca410_link.get()==True:

        cal_btn2= tk.Button(frame_btn, text = "Single MEAS", command = lambda: meas(), width=20)
        cal_btn2.grid(column=0, row=1, ipady=5, sticky=tk.W,padx=1)
        cal_btn3= tk.Button(frame_btn, text = "Pause", command = lambda: Pause(), width=20)
        cal_btn3.grid(column=1, row=0, ipady=5, sticky=tk.W,padx=1)
        cal_btn4= tk.Button(frame_btn, text = "MEAS Gamma", command = lambda: Gamma(), width=20)
        cal_btn4.grid(column=0, row=2, ipady=5, sticky=tk.W,padx=1)
    else:
        pass

    def close_root():
        global open_flag,ca410_chk
        if ca410_link.get()==True:
            ser.close()
        else:
            pass
        time.sleep(1)
        window.destroy()
        open_flag=0
        root.destroy()
    
    reset_btn= tk.Button(frame_btn, text = "Close", command = lambda: close_root(),width=20)
    reset_btn.grid(column=2, row=0, ipady=5, sticky=tk.W)
    
    demura_btn=tk.Button(frame_btn, text = "Demura SW", command = lambda: demura_switch(),width=20)
    demura_btn.grid(column=1, row=1, ipady=5, sticky=tk.W,padx=1)
    
    refresh_btn=tk.Button(frame_btn, text = "REFRESH PAT", command = lambda: refresh_pattern(),width=20)
    refresh_btn.grid(column=0, row=0, ipady=5, sticky=tk.W,padx=1)
    

    pic = ImageGrab.grab()
    def color_change(c1,c):
        
        if c1=="RED":
            if c==1:
                if R_int.get()>=255:R_int.set(255)
                else:R_int.set(R_int.get()+1)

            if c==-1:
                if R_int.get()==0:R_int.set(0)
                else:R_int.set(R_int.get()-1)
        elif c1=='GREEN':
            if c==1:
                if G_int.get()>=255:G_int.set(255)
                else:G_int.set(G_int.get()+1)

            if c==-1:
                if G_int.get()==0:G_int.set(0)
                else:G_int.set(G_int.get()-1)
        elif c1=='BLUE':
            if c==1:
                if B_int.get()>=255:B_int.set(255)
                else:B_int.set(B_int.get()+1)

            if c==-1:
                if B_int.get()==0:B_int.set(0)
                else:B_int.set(B_int.get()-1)            
        elif c1=='WHITE':
            if c==1:
                if W_int.get()>=255:W_int.set(255)
                else:W_int.set(W_int.get()+1)

            if c==-1:
                if W_int.get()==0:W_int.set(0)
                else:W_int.set(W_int.get()-1)            
        
        elif c1=='IMAGE':
            if c==1:
                if img_int.get()>=len(img_path_list)-1:img_int.set(1)
                else:img_int.set(img_int.get()+1)

            if c==-1:
                if img_int.get()==0:img_int.set(0)
                else:img_int.set(img_int.get()-1)
    
    
    
    def refresh_pattern():
        creat_image()
        window.geometry("+{}+{}".format(XString.get(),YString.get()))
    
    def set_up_R():
        if Gray_String.get()>255:
            Gray_String.set(255)
        R_int.set(Gray_String.get())
        G_int.set(0)
        B_int.set(0)
        W_int.set(0)
        img_int.set(0)

   
    def set_up_G():
        if Gray_String.get()>255:
            Gray_String.set(255)
                          
        G_int.set(Gray_String.get())
        B_int.set(0)
        R_int.set(0)
        W_int.set(0)
        img_int.set(0)

    def set_up_B():
        
        if Gray_String.get()>255:
            Gray_String.set(255)
        B_int.set(Gray_String.get())
        G_int.set(0)   
        R_int.set(0)
        W_int.set(0)
        img_int.set(0)

    def set_up_W():
        
        if Gray_String.get()>255:
            Gray_String.set(255)
        W_int.set(Gray_String.get())
        B_int.set(0)
        G_int.set(0)
        R_int.set(0)
        img_int.set(0)

    def set_up_Black():
        
        if Gray_String.get()>255:
            Gray_String.set(255)
            
        R_int.set(0)
        G_int.set(0)
        B_int.set(0)
        W_int.set(0)

        Gray_String.set(0)
        img_int.set(0)
    
    
    
    def set_lu():
        pos_x1.set(0)
        pos_y1.set(0)
    
    def set_ru():
        pos_x1.set(res_x-pos_x2.get())
        pos_y1.set(0)
        
    def set_ld():
        pos_x1.set(0)
        pos_y1.set(res_y-pos_y2.get())
    
    def set_rd():
        pos_x1.set(res_x-pos_x2.get())
        pos_y1.set(res_y-pos_y2.get())
    
    def set_center():
        pos_x1.set(res_x/2-pos_x2.get()/2)
        pos_y1.set(res_y/2-pos_y2.get()/2)
    def set_center_left():
        pos_x1.set(0)
        pos_y1.set(res_y/2-pos_y2.get()/2)
    def set_center_right():
        pos_x1.set(res_x-pos_x2.get())
        pos_y1.set(res_y/2-pos_y2.get()/2)
    def set_center_top():
        pos_x1.set(res_x/2-pos_x2.get()/2)
        pos_y1.set(0)
    def set_center_down():
        pos_x1.set(res_x/2-pos_x2.get()/2)
        pos_y1.set(res_y-pos_y2.get())
    
    mask=np.ones((1080,1920)).astype('uint8')
    def click(event):
        x, y = event.x, event.y
        r, g, b = pic.getpixel((x, y))
        #print('{}, {},R:{},G:{},B:{}'.format(x, y,r,g,b))
        
        
        if W_int.get()==0:
            R=R_int.get()
            G=G_int.get()
            B=B_int.get()
                 
        else:
            R=W_int.get()
            G=W_int.get()
            B=W_int.get()
        
        blank_b,blank_g,blank_r=image_array(B,G,R)
        
        r=int(blank_b[y,x])
        g=int(blank_g[y,x])
        b=int(blank_r[y,x])
        RGB_label.configure(text='x:{},y:{},R:{},G:{},B:{}'.format(x,y,r,g,b))    
        mask[y,x]=0
        array=np.dstack([blank_r.astype('uint8')*mask, blank_g.astype('uint8')*mask,blank_b.astype('uint8')*mask])               
        image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(array))
        canvas.itemconfig(imgbox, image=image)
        canvas.image = image
    
    def click_clear(event):
        x, y = event.x, event.y
        if W_int.get()==0:
            R=R_int.get()
            G=G_int.get()
            B=B_int.get()
                 
        else:
            R=W_int.get()
            G=W_int.get()
            B=W_int.get()
        
        blank_b,blank_g,blank_r=image_array(B,G,R)
        
        r=int(blank_b[y,x])
        g=int(blank_g[y,x])
        b=int(blank_r[y,x])
        RGB_label.configure(text='x:{},y:{},R:{},G:{},B:{}'.format(x,y,r,g,b))    
        mask[y,x]=1

        array=np.dstack([blank_r.astype('uint8')*mask, blank_g.astype('uint8')*mask,blank_b.astype('uint8')*mask])
               
        
        image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(array))

        im=PIL.Image.fromarray(array[:y_end,:x_end,:])
        im.save('R{}G{}B{}_fix.bmp'.format(R,G,B))
        # update the image
        canvas.itemconfig(imgbox, image=image)
        # need to keep a reference of the image, otherwise it will be garbage collected
        canvas.image = image
        
    RGB_label = ttk.Label(frame_slider, text="")
    
    RGB_label.grid(column=1, row=4, ipady=5, sticky=tk.W)
    window.bind('<Escape>', lambda _: close_window())
    window.bind('<r>',lambda event:set_up_R())
    window.bind('<g>',lambda event:set_up_G())
    window.bind('<b>',lambda event:set_up_B())
    window.bind('<w>',lambda event:set_up_W())
    window.bind('<space>', lambda event: demura_switch())
    window.bind('<c>', click_clear)
    window.config(cursor="draft_small")
    setR_btn=tk.Button(frame_chip, text = "R", command = lambda: [set_up_R(),slider_changed(event='Button-1')],bg='red',font=('Arial',10,'bold'),fg='black',width=5)
    setR_btn.grid(column=1, row=0, ipady=5, sticky=tk.W)
    setG_btn=tk.Button(frame_chip, text = "G", command = lambda: [set_up_G(),slider_changed(event='Button-1')],bg='green',font=('Arial',10,'bold'),fg='black',width=5)
    setG_btn.grid(column=2, row=0, ipady=5, sticky=tk.W)
    setB_btn=tk.Button(frame_chip, text = "B", command = lambda: [set_up_B(),slider_changed(event='Button-1')],bg='blue',font=('Arial',10,'bold'),fg='white',width=5)
    setB_btn.grid(column=3, row=0, ipady=5, sticky=tk.W)
    setW_btn=tk.Button(frame_chip, text = "W", command = lambda: [set_up_W(),slider_changed(event='Button-1')],bg='white',font=('Arial',10,'bold'),fg='black',width=5)
    setW_btn.grid(column=4, row=0, ipady=5, sticky=tk.W)
    setW_btn=tk.Button(frame_chip, text = "B", command = lambda: [set_up_Black(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    setW_btn.grid(column=5, row=0, ipady=5, sticky=tk.W)
    
    set_lu_btn=tk.Button(frame_chip, text = "LU", command = lambda: [set_lu(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_lu_btn.grid(column=1, row=1, ipady=5, sticky=tk.W)
    set_ru_btn=tk.Button(frame_chip, text = "RU", command = lambda: [set_ru(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_ru_btn.grid(column=2, row=1, ipady=5, sticky=tk.W)
    set_ld_btn=tk.Button(frame_chip, text = "LD", command = lambda: [set_ld(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_ld_btn.grid(column=3, row=1, ipady=5, sticky=tk.W)
    set_rd_btn=tk.Button(frame_chip, text = "RD", command = lambda: [set_rd(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_rd_btn.grid(column=4, row=1, ipady=5, sticky=tk.W)
    
    set_pattern_btn=tk.Button(frame_chip, text = "Meas P", command = lambda: [creat_mask(),refresh_pattern()],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_pattern_btn.grid(column=5, row=1, ipady=5, sticky=tk.W)
    
    sw_pattern_btn=tk.Button(frame_chip, text = "P-sw", command = lambda: [mask_switch(),refresh_pattern()],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    sw_pattern_btn.grid(column=6, row=1, ipady=5, sticky=tk.W)

    
    set_ct_btn=tk.Button(frame_chip, text = "CT", command = lambda: [set_center_top(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_ct_btn.grid(column=1, row=2, ipady=5, sticky=tk.W)
    
    set_cc_btn=tk.Button(frame_chip, text = "CC", command = lambda: [set_center(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_cc_btn.grid(column=2, row=2, ipady=5, sticky=tk.W)
    
    set_cl_btn=tk.Button(frame_chip, text = "CL", command = lambda: [set_center_left(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_cl_btn.grid(column=3, row=2, ipady=5, sticky=tk.W)

    set_cr_btn=tk.Button(frame_chip, text = "CR", command = lambda: [set_center_right(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_cr_btn.grid(column=4, row=2, ipady=5, sticky=tk.W)
    
    set_cd_btn=tk.Button(frame_chip, text = "CD", command = lambda: [set_center_down(),slider_changed(event='Button-1')],bg='Black',font=('Arial',10,'bold'),fg='white',width=5)
    set_cd_btn.grid(column=5, row=2, ipady=5, sticky=tk.W)
    
    
    
    window.mainloop()
    
    
    
    

    
root.mainloop()

