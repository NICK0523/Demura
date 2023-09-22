# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 15:48:33 2022

@author: RockCHLin

1. 機器學習+RVS亮度資料整合Demura算法測試
2. 補償圖3缺1錯補處理

"""

import pandas as pd
import numpy as np
import os,time,csv
from tqdm import tqdm
import matplotlib.pyplot as plt
from colour.plotting import plot_chromaticity_diagram_CIE1931
import PIL.Image
from scipy.interpolate import interp1d




def calibrate_color_ratio(ca410_data):
    target_L=1250
    target_x=0.313#3+(0.313-0.3147)
    target_y=0.329#+(0.329-0.3594)
    
    csv_data=[]
    with open(ca410_data, 'r', encoding='utf-8-sig') as file:
        csvreader = csv.reader(file,delimiter=",")
        for row in csvreader:
            if row==[]:
                csv_data.append("")
            else:
                csv_data.append(row[0])

    csv_data=np.array(csv_data)    
    
    r_row=np.where(csv_data=='Red')[0][0]+2
    g_row=np.where(csv_data=='Green')[0][0]+2
    b_row=np.where(csv_data=='Blue')[0][0]+2
    step=np.where(csv_data=='255')[0][0]-np.where(csv_data=='0')[0][0]
    
    r1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=r_row,max_rows=step+1,usecols=(0,1,2,3))
    g1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=g_row,max_rows=step+1,usecols=(0,1,2,3))
    b1=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=b_row,max_rows=step+1,usecols=(0,1,2,3))
    
    
    r1[1:,1:3]=r1[1:,1:3]-r1[0,1:3]
    g1[1:,1:3]=g1[1:,1:3]-g1[0,1:3]
    b1[1:,1:3]=b1[1:,1:3]-b1[0,1:3]
    
    
    r1[0,2]=0
    g1[0,2]=0
    b1[0,2]=0
    
    rx_ip1d=interp1d(r1[:,2],r1[:,1], fill_value='extrapolate')
    rz_ip1d=interp1d(r1[:,2],r1[:,3], fill_value='extrapolate')    
    gx_ip1d=interp1d(g1[:,2],g1[:,1], fill_value='extrapolate')
    gz_ip1d=interp1d(g1[:,2],g1[:,3], fill_value='extrapolate')    
    bx_ip1d=interp1d(b1[:,2],b1[:,1], fill_value='extrapolate')
    bz_ip1d=interp1d(b1[:,2],b1[:,3], fill_value='extrapolate')    
    
    
    ry_ip1d=interp1d(r1[:,0],r1[:,2], fill_value='extrapolate')
    gy_ip1d=interp1d(g1[:,0],g1[:,2], fill_value='extrapolate')
    by_ip1d=interp1d(b1[:,0],b1[:,2], fill_value='extrapolate')
    
    rt_array=[]
    gt_array=[]
    bt_array=[]
    
    r_dg=interp1d(r1[:,2]/np.max(r1[:,2]),r1[:,0], fill_value='extrapolate')
    g_dg=interp1d(g1[:,2]/np.max(g1[:,2]),g1[:,0], fill_value='extrapolate')
    b_dg=interp1d(b1[:,2]/np.max(b1[:,2]),b1[:,0], fill_value='extrapolate')
    
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
            
            rt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_R*RY/(ratio_R*RY+ratio_G*GY+BY))).clip(r1[:,2][0],r1[:,2][-1])
            gt=(target_L*((Tgray[gray]/255)**2.2)*(ratio_G*GY/(ratio_R*RY+ratio_G*GY+BY))).clip(g1[:,2][0],g1[:,2][-1])
            bt=(target_L*((Tgray[gray]/255)**2.2)*(BY/(ratio_R*RY+ratio_G*GY+BY))).clip(b1[:,2][0],b1[:,2][-1])

            
            #print(rt,gt,bt)
            rtmp=r
            gtmp=g
            btmp=b
            #找目標亮度
            r=r_dg(rt/np.max(r1[:,2])).round(4)#r=np.abs(r1.Y.astype(np.float64) - rt).argmin()
            g=g_dg(gt/np.max(g1[:,2])).round(4)#g=np.abs(g1.Y.astype(np.float64) - gt).argmin()
            b=b_dg(bt/np.max(b1[:,2])).round(4)#b=np.abs(b1.Y.astype(np.float64) - bt).argmin()
    
            if loop==8:
                newr=r_dg(rt/np.max(r1[:,2])).round(4)#67.50956154862239  #97
                newg=g_dg(gt/np.max(g1[:,2])).round(4)#166.8327090883952 #106
                newb=b_dg(bt/np.max(b1[:,2])).round(4)#15.657729362982373 #85
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
                newr=r_dg(rt/np.max(r1[:,2])).round(4)#67.50956154862239  #97 
                newg=g_dg(gt/np.max(g1[:,2])).round(4)#166.8327090883952 #106  
                newb=b_dg(bt/np.max(b1[:,2])).round(4)#15.657729362982373 #85
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
        # ax[0,0].scatter(wx,wy)
        # ax[0,0].plot(wx,wy)
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


    return rt_array,gt_array,bt_array,nr,ng,nb







#################################################################################
#Demura Process
#################################################################################

resolution_y=720
resolution_x=1280
root_dir=r'E:\Y173\20230918\#2\DATA'

ca410_data=r'E:\Y173\20230918\GammaMeasData_20230918#2_old P.csv'
rt_array,gt_array,bt_array,nr,ng,nb=calibrate_color_ratio(ca410_data)



save_path=os.path.abspath(os.path.join(root_dir,os.path.pardir,'cpimg'))

if os.path.isdir(save_path)==True:
    pass
else:
    os.mkdir(save_path)

Data_layer=[4,8,12,16,20,24,28,32,48,64,80,96,128,160,192,224,255] #Data layer

graylv_r=Data_layer
graylv_g=Data_layer
graylv_b=Data_layer


Data_file_path_w=[]
Data_file_path_r=[]
Data_file_path_g=[]
Data_file_path_b=[]
for i in Data_layer:
    #Data_file_path_w.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='W',gray=i)))
    Data_file_path_r.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Red',gray=i)))
    Data_file_path_g.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Green',gray=i)))
    Data_file_path_b.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Blue',gray=i)))


####
W0 = os.path.join(root_dir,'{color}{gray}.CSV'.format(color='W',gray=0))
####


# #only read RVS luminace
def dataXYZ_noXZ(path,y_resolution=resolution_y):
    chunks = pd.read_csv(path,header=None,iterator = True)
    return chunks.get_chunk(y_resolution).values
# =============================================================================

def pos(M):
    M[1][M[1]<0]=0
    return M
    
try:
    black_data=dataXYZ_noXZ(W0)
except:
    pass


#Wdf={}
Rdf={}
Gdf={}
Bdf={}
for i in range(len(Data_layer)):
    if graylv_g[i]==255:
        kr=410/461
        kg=1100/1038
        kb=100/109.5
    elif graylv_g[i]==224:
        kr=356/336
        kg=843/785
        kb=77/84.8
    elif graylv_g[i]==192:
        kr=193/197
        kg=563/523
        kb=54.4/59.7
    elif graylv_g[i]==160:
        kr=130/115
        kg=382/352
        kb=37.5/38
    elif graylv_g[i]==128:
        kr=77.73/65.6
        kg=225.11/202.3
        kb=21.76/22.76
    elif graylv_g[i]==96:
        kr=38.89/31.8
        kg=117.20/102.5
        kb=11.462/11.45
    elif graylv_g[i]==80:
        kr=25.928/22.4
        kg=79.429/70.3
        kb=7.607/7.93
    elif graylv_g[i]==64:
        kr=15.3/12.41
        kg=45.1/37.8
        kb=4.6/4.4
    elif graylv_g[i]==48:
        kr=4.75/3.92
        kg=12.139/9.83
        kb=1.58/1.518
    elif graylv_g[i]==32:
        kr=1.07/0.798
        kg=1.60/1.075
        kb=0.37/0.32
    elif graylv_g[i]<=28:
        kr=0.695/0.538
        kg=0.821/0.604
        kb=0.235/0.2188
    
    
    
    #Wdf[Data_layer[i]]=pos(dataXYZ(Data_file_path_w[i])-black_data)
    Rdf[graylv_r[i]]=pos(dataXYZ_noXZ(Data_file_path_r[i])*kr)
    Gdf[graylv_g[i]]=pos(dataXYZ_noXZ(Data_file_path_g[i])*kg)
    Bdf[graylv_b[i]]=pos(dataXYZ_noXZ(Data_file_path_b[i])*kb)

   



DataYR=[]
DataYG=[]
DataYB=[]


#graylv=[8,12,16,20,24,28,32,64,128,192,255]

for i in graylv_r:
    DataYR.append(Rdf[i].flatten())
for i in graylv_g:
    DataYG.append(Gdf[i].flatten())
for i in graylv_b:
    DataYB.append(Bdf[i].flatten())#*1.337876289550341)-for v161校正藍色係數

DataYR=np.array(DataYR)
DataYG=np.array(DataYG)
DataYB=np.array(DataYB)

avg_DataYR=[np.average(i) for i in DataYR]
avg_DataYG=[np.average(i) for i in DataYG]
avg_DataYB=[np.average(i) for i in DataYB]

for i in range(1,len(DataYR)):
    DataYR[i]=np.where(DataYR[-1]<0.2*avg_DataYR[-1],avg_DataYR[i],DataYR[i])
for i in range(1,len(DataYG)):
    DataYG[i]=np.where(DataYG[-1]<0.2*avg_DataYG[-1],avg_DataYG[i],DataYG[i])
for i in range(1,len(DataYB)):
    DataYB[i]=np.where(DataYB[-1]<0.2*avg_DataYB[-1],avg_DataYB[i],DataYB[i])    

DataYR=DataYR.T
DataYG=DataYG.T
DataYB=DataYB.T

#plt.plot(DataYR[12361])
#plt.plot(DataYG[12361])
#plt.plot(DataYB[12361])
cp_R255=[]
cp_G255=[]
cp_B255=[]

#[DataYR[i][-1]*(lv/255)**1.8 for lv in graylv]
with tqdm(total=resolution_y*resolution_x) as pbar:
    for i in range(0,resolution_y*resolution_x):
        
        

        rs=interp1d(DataYR[i],graylv_r, fill_value='extrapolate')
        gs=interp1d(DataYG[i],graylv_g, fill_value='extrapolate')           
        bs=interp1d(DataYB[i],graylv_b, fill_value='extrapolate')

        
        cp_R255.append(rs(rt_array).clip(0,255))
        cp_G255.append(gs(gt_array).clip(0,255))
        cp_B255.append(bs(bt_array).clip(0,255))

        pbar.update(1)

# import threading       
# cp_R255=[]
# cp_G255=[]
# cp_B255=[]
# cp_R2552=[]
# cp_G2552=[]
# cp_B2552=[]

# def job(offset):
#     with tqdm(total=460800) as pbar:
#         for i in range(offset,460800+offset):
#             rs=interp1d(DataYR[i],graylv_r, fill_value='extrapolate')
#             gs=interp1d(DataYG[i],graylv_g, fill_value='extrapolate')           
#             bs=interp1d(DataYB[i],graylv_b, fill_value='extrapolate')
#             cp_R255.append(rs(rt_array).clip(0,255))
#             cp_G255.append(gs(gt_array).clip(0,255))
#             cp_B255.append(bs(bt_array).clip(0,255))
#             pbar.update(1)
# def job2(offset):
#     with tqdm(total=460800) as pbar:
#         for i in range(offset,460800+offset):
#             rs=interp1d(DataYR[i],graylv_r, fill_value='extrapolate')
#             gs=interp1d(DataYG[i],graylv_g, fill_value='extrapolate')           
#             bs=interp1d(DataYB[i],graylv_b, fill_value='extrapolate')
#             cp_R2552.append(rs(rt_array).clip(0,255))
#             cp_G2552.append(gs(gt_array).clip(0,255))
#             cp_B2552.append(bs(bt_array).clip(0,255))
#             pbar.update(1)            
# threads = []
# threads.append(threading.Thread(target = job, args = (0,)))
# threads.append(threading.Thread(target = job2, args = (460800,)))

# threads[0].start()
# threads[1].start()
# threads[0].join()
# threads[1].join()

    
    
LUT_gray_8=[8,16,32, 64, 96, 128, 160, 192, 224, 255]
#LUT_gray_8=Data_layer
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
    

    Wimage = PIL.Image.fromarray(np.rot90(img,0))
    Rimage = PIL.Image.fromarray(np.rot90(Rimg,0))
    Gimage = PIL.Image.fromarray(np.rot90(Gimg,0))
    Bimage = PIL.Image.fromarray(np.rot90(Bimg,0))


    Wimage.save(os.path.join(save_path,'W'+str(LUT_gray_8[i])+'_2.bmp'))
    Rimage.save(os.path.join(save_path,'R'+str(LUT_gray_8[i])+'_2.bmp'))
    Gimage.save(os.path.join(save_path,'G'+str(LUT_gray_8[i])+'_2.bmp'))
    Bimage.save(os.path.join(save_path,'B'+str(LUT_gray_8[i])+'_2.bmp'))




print("demura images save in "+ os.path.join(save_path))


#=======================================#
#=======================================#
#輸出LUT 10bit layer
#LUT_gray=(32,64,128,256,768)

LUT_gray=(60,  124,  252,  508, 1020)

#輸出翻轉data map
flip=False
rot=0
#補償White image 路徑
#dir_path=r'D:\UserShare\code\Demura_new_algo\Y161_ca410\Chip1_Data2\cpimg'
#輸出LUT存檔路徑
#save_path=r'D:\UserShare\code\Demura_new_algo\Y161_ca410\Chip1_Data2\cpimg'
#編號
num='ITRI_#1'
#LUT解析度




#影像8bit to 13 bit補償
scale_bit=16

#補償上下限
clip_bit_upper=1023
clip_bit_lower=-1023
#=======================================#
#=======================================#


#=======================================#
LUT_gray_8 = np.array([8,16,32,64,96,128,160,192,224,255]).astype(np.float32)
#LUT_gray_8 = np.array([8,16,32,64,192]).astype(np.float32)

LUT_gray_10=np.array([  32,   64,  128,  256,  384,  512,  640,  768,  896, 1024])-4
#LUT_gray_10=np.array([32,64,128,256,768])

#=======================================#


def img_flip(m,flip):
    if flip==True:
        m=np.flip(m,axis=0)
        #m=np.flip(m,axis=1)
    else:
        m=m
        
    return m
def reshape_scale(m):
    m=np.array(m).reshape(720,1280)
    return m


#=======================================#
#LUT建立
#=======================================#
LUT_R={}
LUT_G={}
LUT_B={}

#R=np.array(cp_R255)[:,i].reshape(resolution_y,resolution_x)
#G=np.array(cp_G255)[:,i].reshape(resolution_y,resolution_x)
#B=np.array(cp_B255)[:,i].reshape(resolution_y,resolution_x)

for i in range(len(LUT_gray_10)):

    tmpR=np.rot90(np.array(cp_R255)[:,i].clip(0,255).reshape(720,1280),rot)
    tmpG=np.rot90(np.array(cp_G255)[:,i].clip(0,255).reshape(720,1280),rot)
    B=np.rot90(np.array(cp_B255)[:,i].clip(0,255).reshape(720,1280),rot)
    
    if i ==0:
        mask=np.where(np.rot90(np.array(cp_B255)[:,0].clip(0,255).reshape(720,1280),rot)>np.array(cp_B255)[:,0].clip(0,255).reshape(720,1280).mean()*3,0,1)
        B=B*mask.astype('uint8')
    else:
   
        B=B
    


    LUT_R[str(LUT_gray_10[i])] = (np.rot90(tmpR,rot)-LUT_gray_8[i])*scale_bit
    LUT_G[str(LUT_gray_10[i])] = (np.rot90(tmpG,rot)-LUT_gray_8[i])*scale_bit
    LUT_B[str(LUT_gray_10[i])] = (np.rot90(B,rot)-LUT_gray_8[i])*scale_bit
    
    LUT_R[str(LUT_gray_10[i])] = np.where(LUT_R[str(LUT_gray_10[i])]>clip_bit_upper,clip_bit_upper,LUT_R[str(LUT_gray_10[i])])
    LUT_G[str(LUT_gray_10[i])] = np.where(LUT_G[str(LUT_gray_10[i])]>clip_bit_upper,clip_bit_upper,LUT_G[str(LUT_gray_10[i])])
    LUT_B[str(LUT_gray_10[i])] = np.where(LUT_B[str(LUT_gray_10[i])]>clip_bit_upper,clip_bit_upper,LUT_B[str(LUT_gray_10[i])])
    
    LUT_R[str(LUT_gray_10[i])] = np.where(LUT_R[str(LUT_gray_10[i])]<clip_bit_lower,clip_bit_lower,LUT_R[str(LUT_gray_10[i])])
    LUT_G[str(LUT_gray_10[i])] = np.where(LUT_G[str(LUT_gray_10[i])]<clip_bit_lower,clip_bit_lower,LUT_G[str(LUT_gray_10[i])])
    LUT_B[str(LUT_gray_10[i])] = np.where(LUT_B[str(LUT_gray_10[i])]<clip_bit_lower,clip_bit_lower,LUT_B[str(LUT_gray_10[i])])
    
    
LUT_R[str(1020)]=np.where(LUT_R[str(1020)]>15,15,LUT_R[str(1020)])
LUT_G[str(1020)]=np.where(LUT_G[str(1020)]>15,15,LUT_G[str(1020)])   
LUT_B[str(1020)]=np.where(LUT_B[str(1020)]>15,15,LUT_B[str(1020)])    

#=======================================#
#csv補償表{LU/RU/LD/RD}
#=======================================#
print('Generate LUT File')
header_layer=np.array([[len(LUT_gray),0],[int(1280),int(720)]])
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
        
print("LUT save in "+os.path.join(save_path,file_name))


    