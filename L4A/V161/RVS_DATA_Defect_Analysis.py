# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 13:33:42 2023

@author: NickNHHuang
"""

import serial
import tkinter as tk
from tkinter import ttk
import PIL.Image, PIL.ImageTk
import numpy as np
import pandas as pd
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

####################################################################################################
root = tk.Tk()

ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()

root.geometry('700x100+%d+%d'%(ws/2,hs/2))


root.resizable(False, False)
root.title('RVS_DATA_Defect_Analysis © 2023 AUO Corporation')
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

Data_path_String=tk.StringVar()

Data_label = ttk.Label(frame_path, text='DataPath')
show_folderPath = tk.Entry(frame_path, width=60, textvariable=Data_path_String)
Data_label.grid(column=0,row=1,sticky=tk.W,ipadx=5,padx=1,pady=5)
show_folderPath.grid(column=1,row=1,sticky=tk.W,ipadx=5,padx=1,pady=5)


check_Gamma_file_btn=tk.Button(frame_path, text = "0-Data_Path", command = lambda: open_folder(),width=15,anchor="w")
check_Gamma_file_btn.grid(column=2, row=1, ipady=5, sticky=tk.W,ipadx=1,padx=5)

Run_Defect_Analysis_btn=tk.Button(frame_path, text = "1-Run Defect_Analysis", command = lambda: RVS_DATA_Defect_Analysis(),width=20,anchor="w")
Run_Defect_Analysis_btn.grid(column=2, row=3, ipady=5, sticky=tk.W,ipadx=1,padx=5)


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
    Data_path_String.set(filename) 

def open_folder():
    folder_path = filedialog.askdirectory()#打開文件
    #show_folderPath.delete(0,END)#清空
    show_folderPath.insert(0,folder_path)
    
def RVS_DATA_Defect_Analysis():
    
    #resolution_y=240
    #resolution_x=540
    root_path=show_folderPath.get()
    defect_folder=os.listdir(root_path)
    
    root_save_path=show_folderPath.get()+'\Defect_MAP'
    
    root_save_path2=show_folderPath.get()+'\Defect_MAP_Gray4'
    
    # #only read RVS luminace
    def dataXYZ_noXZ(path,y_resolution=240):
        try:
            chunks=np.loadtxt(path,delimiter=",",encoding="utf-8",max_rows=y_resolution)
        except:
            chunks=np.loadtxt(path,encoding="utf-8",max_rows=y_resolution)
        #chunks = pd.read_csv(path,header=None,iterator = True)
        return np.array(chunks)
    # =============================================================================
    
    raw=[]
    
    raw_defect_sum=[]
    
    if os.path.isdir(root_save_path)==True:
        pass
    else:
        os.mkdir(root_save_path)
    
    if os.path.isdir(root_save_path2)==True:
        pass
    else:
        os.mkdir(root_save_path2)
    
    
    for folder in defect_folder:
        
        print(folder)
        
        #folder='VKV3457686A0213'
        root_dir=os.path.join(root_path,'{data}'.format(data=folder),'DATA')
        if len(os.listdir(root_dir)) == 0:
            print("{} Directory is empty".format(folder))
            
            
        save_path=os.path.join(root_save_path,'{data}'.format(data=folder))
        if os.path.isdir(save_path)==True:
            pass
        else:
            os.mkdir(save_path)
        
        
        try:
            R255=dataXYZ_noXZ(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Red',gray=255)))
            G255=dataXYZ_noXZ(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Green',gray=255)))
            B255=dataXYZ_noXZ(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Blue',gray=255)))
            #W255=dataXYZ_noXZ(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='W',gray=255)))
            R4=dataXYZ_noXZ(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Red',gray=4)))
            G4=dataXYZ_noXZ(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Green',gray=4)))
            B4=dataXYZ_noXZ(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Blue',gray=4)))
            
           
            
            R255_defcet=np.where(R255<R255.mean()*0.25,0,255)
            G255_defcet=np.where(G255<G255.mean()*0.25,0,255)
            B255_defcet=np.where(B255<B255.mean()*0.25,0,255)
            W255_defect_sum=len(np.where(R255<R255.mean()*0.25)[0])+ len(np.where(G255<G255.mean()*0.25)[0])+len(np.where(B255<B255.mean()*0.25)[0])
            
            
            raw_defect_sum.append((folder,W255_defect_sum))
    
            W255_defect_tmp=R255_defcet*G255_defcet*B255_defcet
            W255_decet=np.where(W255_defect_tmp<255**3,0,255).astype('uint8')
            
            blank=0*np.ones((240,540)).astype('uint8')
        #     R=((R255/R255.max())*255).clip(0,255).astype('uint8')
        #     G=((G255/G255.max())*255).clip(0,255).astype('uint8')
        #     B=((B255/B255.max())*255).clip(0,255).astype('uint8')
        #     W=((W255/W255.max())*255).clip(0,255).astype('uint8')
            
        #     cv2.imwrite(os.path.join(root_save_path,folder,'RVS_R255.bmp'),cv2.merge([R,R,R]))
        #     cv2.imwrite(os.path.join(root_save_path,folder,'RVS_G255.bmp'),cv2.merge([G,G,G]))
        #     cv2.imwrite(os.path.join(root_save_path,folder,'RVS_B255.bmp'),cv2.merge([B,B,B]))
        #     cv2.imwrite(os.path.join(root_save_path,folder,'RVS_W255.bmp'),cv2.merge([W,W,W]))
        # except:
        #     pass
            
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([blank,((G255/G255.max())*255).clip(0,255).astype('uint8'),blank]))
            plt.savefig(os.path.join(save_path,'G255_RVS.png'))
            plt.close()
            
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([blank,blank,((B255/B255.max())*255).clip(0,255).astype('uint8')]))
            plt.savefig(os.path.join(save_path,'B255_RVS.png'))
            plt.close()
            
            
            blank=0*np.ones((240,540)).astype('uint8')
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([((R255/R255.max())*255).clip(0,255).astype('uint8'),blank,blank]))
            plt.savefig(os.path.join(save_path,'R255_RVS.png'))
            plt.close()
            
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([blank,((G255/G255.max())*255).clip(0,255).astype('uint8'),blank]))
            plt.savefig(os.path.join(save_path,'G255_RVS.png'))
            plt.close()
            
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([blank,blank,((B255/B255.max())*255).clip(0,255).astype('uint8')]))
            plt.savefig(os.path.join(save_path,'B255_RVS.png'))
            plt.close()
            
            blank=0*np.ones((240,540)).astype('uint8')
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([((R4/R4.max()/0.7)*255).clip(0,255).astype('uint8'),blank,blank]))
            plt.savefig(os.path.join(root_save_path2,'{}_R4_RVS.png'.format(folder)))
            plt.close()
            
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([blank,((G4/G4.max()/0.7)*255).clip(0,255).astype('uint8'),blank]))
            plt.savefig(os.path.join(root_save_path2,'{}_G4_RVS.png'.format(folder)))
            plt.close()
            
            plt.figure(figsize=(16,9))
            plt.imshow(np.dstack([blank,blank,((B4/B4.max()/0.7)*255).clip(0,255).astype('uint8')]))
            plt.savefig(os.path.join(root_save_path2,'{}_B4_RVS.png'.format(folder)))
            plt.close()
            
            
            import csv
            #np.where(R255_defcet==0)[0].T
            with open(os.path.join(save_path,'defect.csv'), 'w', newline='') as file:
                mywriter = csv.writer(file, delimiter=',')
                mywriter.writerows(np.array([['R_Y','R_X']]))
                mywriter.writerows(np.array(np.where(R255_defcet==0)).T)
                
                mywriter.writerows(np.array([['G_Y','G_X']]))
                mywriter.writerows(np.array(np.where(G255_defcet==0)).T)
                
                mywriter.writerows(np.array([['B_Y','B_X']]))
                mywriter.writerows(np.array(np.where(B255_defcet==0)).T)
                
        
            R_defect_map=np.dstack([R255_defcet.astype('uint8'),blank,blank])
            G_defect_map=np.dstack([blank,G255_defcet.astype('uint8'),blank])
            B_defect_map=np.dstack([blank,blank,B255_defcet.astype('uint8')])
            W_defect_map=np.dstack([W255_decet,W255_decet,W255_decet])
            
            
            # #plt.figure(figsize=(16,9))
            # plt.imshow(R_defect_map)
            # plt.savefig(os.path.join(save_path,'R_255_defect.bmp'))
            # plt.close()
            
            # #plt.figure(figsize=(16,9))
            # plt.imshow(G_defect_map)
            # plt.savefig(os.path.join(save_path,'G_255_defect.bmp'))
            # plt.close()
            
            # #plt.figure(figsize=(16,9))
            # plt.imshow(B_defect_map)
            # plt.savefig(os.path.join(save_path,'B_255_defect.bmp'))
            # plt.close()
        
            # #plt.figure(figsize=(16,9))
            # plt.imshow(W_defect_map)
            # plt.savefig(os.path.join(save_path,'W_255_defect.bmp'))
            # plt.close()
        
            
            Wimage = PIL.Image.fromarray(W_defect_map)
            Rimage = PIL.Image.fromarray(R_defect_map)
            Gimage = PIL.Image.fromarray(G_defect_map)
            Bimage = PIL.Image.fromarray(B_defect_map)
        
        
            Wimage.save(os.path.join(save_path,'W_255_defect'+'.bmp'))
            Rimage.save(os.path.join(save_path,'R_255_defect'+'.bmp'))
            Gimage.save(os.path.join(save_path,'G_255_defect'+'.bmp'))
            Bimage.save(os.path.join(save_path,'B_255_defect'+'.bmp'))
        
        
        
        
            plt.hist(R255.flatten(),bins=1000)
            plt.savefig(os.path.join(save_path,'R255_disturbution.png'))
            plt.close()
            plt.hist(G255.flatten(),bins=1000)
            plt.savefig(os.path.join(save_path,'G255_disturbution.png'))
            plt.close()
            plt.hist(B255.flatten(),bins=1000)
            plt.savefig(os.path.join(save_path,'B255_disturbution.png'))
            plt.close()
            
            r_raw=pd.DataFrame(np.array(R255.flatten()),columns=[folder+'_R255']).describe()
            g_raw=pd.DataFrame(np.array(G255.flatten()),columns=[folder+'_G255']).describe()
            b_raw=pd.DataFrame(np.array(B255.flatten()),columns=[folder+'_B255']).describe()
            
            df=pd.concat([r_raw,g_raw,b_raw],axis=1)
            
            
            df.loc['defect Count']=[len(np.where(R255_defcet==0)[0]),
                                    len(np.where(G255_defcet==0)[0]),
                                    len(np.where(B255_defcet==0)[0]),
                                    ]
        
            raw.append(df)
        except:
            r_raw=pd.DataFrame(np.array(0*np.ones((240,540)).flatten()),columns=[folder+'_R255']).describe()
            g_raw=pd.DataFrame(np.array(0*np.ones((240,540)).flatten()),columns=[folder+'_G255']).describe()
            b_raw=pd.DataFrame(np.array(0*np.ones((240,540)).flatten()),columns=[folder+'_B255']).describe()
            df=pd.concat([r_raw,g_raw,b_raw],axis=1)
                    
            raw.append(df)
    
    pd.DataFrame(raw_defect_sum,columns=['CHIP ID','Defect Pts']).to_csv(os.path.join(root_save_path, 'defct_pts.csv'))
    pd.concat([i for i in raw],axis=1).transpose().to_csv(os.path.join(root_save_path, 'defct_statics.csv'))
    

root.mainloop()