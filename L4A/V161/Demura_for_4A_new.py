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

##導入RVS資料處理
#from AUO_Demura.Data_Reader import read_pormetric_dataX,read_pormetric_dataY,read_pormetric_dataZ
## 內插算法導入
from scipy.interpolate import interp1d




def calibrate_color_ratio(ca410_data,target_L,target_x,target_y):
    

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


    
    if nb[-1] != 255:
       nb[-1]=255
    

    return rt_array,gt_array,bt_array,nr,ng,nb

def calibrate_color_ratio_2(ca410_data,target_L,target_x,target_y):
    

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
    
    
    
    indexR=nr[[8,16,50,64,96,128,160,192,244,255]]
    indexG=ng[[8,16,50,64,96,128,160,192,244,255]]
    indexB=nb[[8,16,50,64,96,128,160,192,244,255]]
    
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


    
    if nb[-1] != 255:
       nb[-1]=255
    

    return rt_array,gt_array,bt_array,nr,ng,nb

ca410_data=r'E:\V161\GammaMeasData_20230810_pattern_check.csv'
#ca410_data=r'E:\V161\20230710\GammaMeasData_4A1913.csv'
rt_array,gt_array,bt_array,nr,ng,nb=calibrate_color_ratio(ca410_data,650,0.30,0.31)
rt_array,gt_array,bt_array,nnr,nng,nnb=calibrate_color_ratio_2(ca410_data,650,0.30,0.31)
bt_array[-2]=bt_array[-1]
bt_array[-1]=bt_array[-1]+2
def Demura(root_dir,rt_array,gt_array,bt_array,nr,ng,nb):
    #################################################################################
    #Demura Process
    #################################################################################
    
    resolution_y=240
    resolution_x=540
    root_dir=r'E:\V161\20230821\DATA'
    save_path=os.path.abspath(os.path.join(root_dir,os.path.pardir,'cpimg'))
    
    if os.path.isdir(save_path)==True:
        pass
    else:
        os.mkdir(save_path)
    
    Data_layer=[4,8,12,16,20,24,28,32,64,96,128,160,192,224,255] #Data layer
    

    graylv_r=nr[Data_layer]
    graylv_g=ng[Data_layer]
    graylv_b=nb[Data_layer]

    Data_file_path_r=[]
    Data_file_path_g=[]
    Data_file_path_b=[]
    for i in Data_layer:
        Data_file_path_r.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Red',gray=i)))
        Data_file_path_g.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Green',gray=i)))
        Data_file_path_b.append(os.path.join(root_dir,'{color}{gray}.CSV'.format(color='Blue',gray=i)))
    
    
    ####
    #W0 = os.path.join(root_dir,'{color}{gray}.CSV'.format(color='W',gray=0))
    ####
    
    # def dataXYZ(M):
    #     #tmpX=read_pormetric_dataX(M,resolution_y).reshape(resolution_y,resolution_x)
    #     tmpY=read_pormetric_dataY(M,resolution_y).reshape(resolution_y,resolution_x)
    #     #tmpZ=read_pormetric_dataZ(M,resolution_y).reshape(resolution_y,resolution_x)
        
    #     return np.array([0*np.ones((resolution_y,resolution_x)),tmpY,0*np.ones((resolution_y,resolution_x))])
    
    # #only read RVS luminace
    def dataXYZ_noXZ(path,y_resolution=resolution_y):
             	chunks = pd.read_csv(path,header=None,iterator = True)
             	return chunks.get_chunk(y_resolution).values
    # =============================================================================
    
    def pos(M):
        M[1][M[1]<0]=0
        return M
        
       
    
    
    
    #black_data=dataXYZ_noXZ(W0)
    #Wdf={}
    Rdf={}
    Gdf={}
    Bdf={}
    for i in range(len(Data_layer)):
        #Wdf[Data_layer[i]]=pos(dataXYZ(Data_file_path_w[i])-black_data)
        Rdf[graylv_r[i]]=pos(dataXYZ_noXZ(Data_file_path_r[i]))
        Gdf[graylv_g[i]]=pos(dataXYZ_noXZ(Data_file_path_g[i]))
        Bdf[graylv_b[i]]=pos(dataXYZ_noXZ(Data_file_path_b[i]))
    

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
        DataYR[i]=np.where(DataYR[-1]<0.45*avg_DataYR[-1],avg_DataYR[i],DataYR[i])
    for i in range(1,len(DataYG)):
        DataYG[i]=np.where(DataYG[-1]<0.45*avg_DataYG[-1],avg_DataYG[i],DataYG[i])
    for i in range(1,len(DataYB)):
        DataYB[i]=np.where(DataYB[-1]<0.45*avg_DataYB[-1],avg_DataYB[i],DataYB[i])    
    
    DataYR=DataYR.T
    DataYG=DataYG.T
    DataYB=DataYB.T

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
    
    
    
    
    
    import PIL.Image
    
    
    R_ondot=np.rot90(np.array(PIL.Image.open(r'E:\V161\20230815_wood\6A1813\R_ondot.bmp').convert('RGB'))[:,:,0],1).flatten()
    G_ondot=np.rot90(np.array(PIL.Image.open(r'E:\V161\20230815_wood\6A1813\G_ondot.bmp').convert('RGB'))[:,:,1],1).flatten()
    B_ondot=np.rot90(np.array(PIL.Image.open(r'E:\V161\20230815_wood\6A1813\B_ondot.bmp').convert('RGB'))[:,:,2],1).flatten()
    
    for p in np.where(R_ondot==0)[0]:
        
        cp_R255[p]=np.array([30,30,30,30,30,30,30,30,30,30])
        print(cp_R255[p])
    for p in np.where(G_ondot==0)[0]:
        cp_G255[p]=np.array([30,30,30,30,30,30,30,30,30,30])
        print(cp_G255[p])

    for p in np.where(B_ondot==0)[0]:
        cp_B255[p]=np.array([30,30,30,30,30,30,30,30,30,30])
        print(cp_B255[p])

    
    
    
    LUT_gray_8=[8,16,32, 64, 96, 128, 160, 192, 224, 255]
    
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
        
        
        

        
    
        Wimage = PIL.Image.fromarray(np.rot90(img,3))
        Rimage = PIL.Image.fromarray(np.rot90(Rimg,3))
        Gimage = PIL.Image.fromarray(np.rot90(Gimg,3))
        Bimage = PIL.Image.fromarray(np.rot90(Bimg,3))
    
    
        Wimage.save(os.path.join(save_path,'W'+str(LUT_gray_8[i])+'_2.bmp'))
        Rimage.save(os.path.join(save_path,'R'+str(LUT_gray_8[i])+'_2.bmp'))
        Gimage.save(os.path.join(save_path,'G'+str(LUT_gray_8[i])+'_2.bmp'))
        Bimage.save(os.path.join(save_path,'B'+str(LUT_gray_8[i])+'_2.bmp'))
    
    
    
    
    print("demura images save in "+ os.path.join(save_path))
    
    
    #=======================================#
    #=======================================#
    #輸出LUT 10bit layer
    #LUT_gray=(32,64,128,256,768)
    LUT_gray=(240, 272, 336, 464,976)
    #輸出翻轉data map
    flip=False
    rot=3
    #補償White image 路徑
    #dir_path=r'D:\UserShare\code\Demura_new_algo\Y161_ca410\Chip1_Data2\cpimg'
    #輸出LUT存檔路徑
    #save_path=r'D:\UserShare\code\Demura_new_algo\Y161_ca410\Chip1_Data2\cpimg'
    #編號
    num=root_dir.split('\\')[-2]
    #LUT解析度
    
    
    #裁切影像位置
    x_start,x_end,y_start,y_end=0,resolution_x,0,resolution_y
    
    #影像8bit to 13 bit補償
    scale_bit=32
    
    #補償上下限
    clip_bit_upper=4095
    clip_bit_lower=-4095
    #=======================================#
    #=======================================#
    
    
    #=======================================#
    #LUT_gray_8 = np.array([8,16,32,64,96,128,160,192,224,255]).astype(np.float32)
    
    LUT_gray_8 = np.array([8,16,32,64,96,128,160,192,224,255]).astype(np.float32)
    LUT_gray_8_move = np.array([8,16,32,64,96,128,160,224,224,255]).astype(np.float32)
    
    LUT_gray_8_target = LUT_gray_8+52
    
    LUT_gray_10=(LUT_gray_8_target*4).astype(np.int32)
    
    #LUT_gray_10=np.array([  32,   64,  128,  256,  384,  512,  640,  768,  896, 1020])
    
    
    #=======================================#
    cp_R255_dict={}
    cp_G255_dict={}
    cp_B255_dict={}
    for i in range(len(LUT_gray_10)):
        cp_R255_dict[str(LUT_gray_8[i])]=np.array(cp_R255)[:,i]
        cp_G255_dict[str(LUT_gray_8[i])]=np.array(cp_G255)[:,i]
        cp_B255_dict[str(LUT_gray_8[i])]=np.array(cp_B255)[:,i]
    
    
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
        
            
        
        LUT_R[str(LUT_gray_10[i])] = (np.rot90(cp_R255_dict[str(LUT_gray_8_move[i])].reshape(resolution_y,resolution_x),rot)-LUT_gray_8_target[i])*scale_bit
        LUT_G[str(LUT_gray_10[i])] = (np.rot90(cp_G255_dict[str(LUT_gray_8_move[i])].reshape(resolution_y,resolution_x),rot)-LUT_gray_8_target[i])*scale_bit
        LUT_B[str(LUT_gray_10[i])] = (np.rot90(cp_B255_dict[str(LUT_gray_8_move[i])].reshape(resolution_y,resolution_x),rot)-LUT_gray_8_target[i])*scale_bit
        
        #LUT_R[str(LUT_gray_10[i])] = (np.rot90(R,rot)-LUT_gray_8[i])*scale_bit
        #LUT_G[str(LUT_gray_10[i])] = (np.rot90(G,rot)-LUT_gray_8[i])*scale_bit
        #LUT_B[str(LUT_gray_10[i])] = (np.rot90(B,rot)-LUT_gray_8[i])*scale_bit
        
        
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
        
    print("="*50)
    print("Check LEFT LUT BITS TOTAL")        
    bit_sum_left=[]
    for u in LUT_gray:
        print('Layer R:{} Min: {} , Max: {} , bit: {}'.format(u,(LUT_R[str(u)][:,0:120].min().astype('int64'))/8,(LUT_R[str(u)][:,0:120].max().astype('int64'))/8,bit_check(LUT_R[str(u)][:,0:120].astype('int64'))))
        print('Layer G:{} Min: {} , Max: {} , bit: {}'.format(u,(LUT_G[str(u)][:,0:120].min().astype('int64'))/8,(LUT_G[str(u)][:,0:120].max().astype('int64'))/8,bit_check(LUT_G[str(u)][:,0:120].astype('int64'))))
        print('Layer B:{} Min: {} , Max: {} , bit: {}'.format(u,(LUT_B[str(u)][:,0:120].min().astype('int64'))/8,(LUT_B[str(u)][:,0:120].max().astype('int64'))/8,bit_check(LUT_B[str(u)][:,0:120].astype('int64'))))
        
        bit_sum_left.append(bit_check(LUT_R[str(u)][:,0:120].astype('int64')))
        bit_sum_left.append(bit_check(LUT_G[str(u)][:,0:120].astype('int64')))
        bit_sum_left.append(bit_check(LUT_B[str(u)][:,0:120].astype('int64')))
    print("="*50)
    print("Check RIGHT LUT BITS TOTAL")        
    bit_sum_right=[]
    for u in LUT_gray:
        print('Layer R:{} Min: {} , Max: {} , bit: {}'.format(u,(LUT_R[str(u)][:,120:].min().astype('int64'))/8,(LUT_R[str(u)][:,120:].max().astype('int64'))/8,bit_check(LUT_R[str(u)][:,120:].astype('int64'))))
        print('Layer G:{} Min: {} , Max: {} , bit: {}'.format(u,(LUT_G[str(u)][:,120:].min().astype('int64'))/8,(LUT_G[str(u)][:,120:].max().astype('int64'))/8,bit_check(LUT_G[str(u)][:,120:].astype('int64'))))
        print('Layer B:{} Min: {} , Max: {} , bit: {}'.format(u,(LUT_B[str(u)][:,120:].min().astype('int64'))/8,(LUT_B[str(u)][:,120:].max().astype('int64'))/8,bit_check(LUT_B[str(u)][:,120:].astype('int64'))))
        
        bit_sum_right.append(bit_check(LUT_R[str(u)][:,120:].astype('int64')))
        bit_sum_right.append(bit_check(LUT_G[str(u)][:,120:].astype('int64')))
        bit_sum_right.append(bit_check(LUT_B[str(u)][:,120:].astype('int64')))
            
    print('Left bits : {}'.format(np.sum(bit_sum_left)))
    print('Right bits : {}'.format(np.sum(bit_sum_right)))
    
    #if np.sum(bit_sum_left)>144 or np.sum(bit_sum_right)>144:
    print('192 divide 2')            
    LUT_R[str(LUT_gray[-1])]=(LUT_R[str(LUT_gray[-1])])#.clip(-254,255)
    LUT_G[str(LUT_gray[-1])]=(LUT_G[str(LUT_gray[-1])])
    LUT_B[str(LUT_gray[-1])]=(LUT_B[str(LUT_gray[-1])])
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
    #LUT_R[str(LUT_gray[-1])]=(LUT_R[str(LUT_gray[-1])]).clip(-1020,1023)
    #LUT_G[str(LUT_gray[-1])]=(LUT_G[str(LUT_gray[-1])]).clip(-1020,1023)
    #LUT_B[str(LUT_gray[-1])]=(LUT_B[str(LUT_gray[-1])]).clip(-1020,1023)
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
            
    print("LUT save in "+os.path.join(save_path,file_name))
    
    #=======================================#
    #csv補償表
    #=======================================#
    print('Generate LUT File')
    header_layer=np.array([[len(LUT_gray),0],[int(120),int(540)]])
    #LUT_gray_10=(32,64,128,256,384,512,640,768,896,1023)
    
    
    strtime=time.strftime("%Y%m%d%H%M%S")
    prefix_name='Demura_LUT'+'_'+strtime+'_'+num+'_Right' #name rule LUTname + time stamp[YYYY/mm/dd/HH/MM/SS]
    
    file_name=prefix_name+'_normal.csv'
    
    with open(os.path.join(save_path,file_name), 'w', newline='') as file:
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
            
    print("LUT save in "+os.path.join(save_path,file_name))

    return LUT_R,LUT_G,LUT_B

root_dir=r'E:\V161\20230821'
folder= ['20230821']#4A1713_Random,4A1913_Random
for i in folder:
    LUT_R,LUT_G,LUT_B=Demura(os.path.join(root_dir,'{}\DATA'.format(i)),rt_array,gt_array,bt_array,nr,ng,nb)
    print('done')  
