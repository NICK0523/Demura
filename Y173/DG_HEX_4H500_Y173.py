# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 10:29:26 2023

@author: RockCHLin
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

def clama(Rdf,Gdf,Bdf,Wdf,layer):
    a1=Rdf[layer][0]
    b1=Gdf[layer][0]
    c1=Bdf[layer][0]
    d1=Wdf[layer][0]
    a2=Rdf[layer][1]
    b2=Gdf[layer][1]
    c2=Bdf[layer][1]
    d2=Wdf[layer][1]
    a3=Rdf[layer][2]
    b3=Gdf[layer][2]
    c3=Bdf[layer][2]
    d3=Wdf[layer][2]
    delta = np.abs(a1*b2*c3+b1*c2*a3+c1*a2*b3-a3*b2*c1-b3*c2*a1-c3*a2*b1)
    deltaX = np.abs(d1*b2*c3+b1*c2*d3+c1*d2*b3-d3*b2*c1-b3*c2*d1-c3*d2*b1)
    deltaY = np.abs(a1*d2*c3+d1*c2*a3+c1*a2*d3-a3*d2*c1-d3*c2*a1-c3*a2*d1)
    deltaZ = np.abs(a1*b2*d3+b1*d2*a3+d1*a2*b3-a3*b2*d1-b3*d2*a1-d3*a2*b1)
    
    return(deltaX/delta,deltaY/delta,deltaZ/delta)
def NA(M):
    NAN = np.where(np.isnan(M), np.nanmean(M), M)
    return(np.where(np.isinf(NAN), np.mean(NAN[np.isfinite(NAN)]), NAN))




def calibrate_color_ratio_XYZ_model_Wcal(ca410_data,target_L,target_x,target_y):
  
    Rdf=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=261,max_rows=256,usecols=(1,2,3))
    Gdf=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=520,max_rows=256,usecols=(1,2,3))
    Bdf=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=779,max_rows=256,usecols=(1,2,3))
    Wdf=np.loadtxt(ca410_data,delimiter=",",encoding="utf-8",skiprows=1038,max_rows=256,usecols=(1,2,3))
    
    
    r1=[]
    g1=[]
    b1=[]
    Data_layer=[i for i in range(0,256,1)]
    for i in Data_layer:
        
        if i <7:
            r_cal,g_cal,b_cal=1,1,1
        else:
            r_cal,g_cal,b_cal=clama(Rdf,Gdf,Bdf,Wdf,i)
        
        r1.append([NA(Rdf[i][0]*r_cal),NA(Rdf[i][1]*r_cal),NA(Rdf[i][2]*r_cal)])
        g1.append([NA(Gdf[i][0]*g_cal),NA(Gdf[i][1]*g_cal),NA(Gdf[i][2]*g_cal)])
        b1.append([NA(Bdf[i][0]*b_cal),NA(Bdf[i][1]*b_cal),NA(Bdf[i][2]*b_cal)])
                
    
    
    plt.plot(np.array(r1)[:,1],'-r')
    plt.plot(np.array(g1)[:,1],'-g')
    plt.plot(np.array(b1)[:,1],'-b')
    plt.show()
    
    r1=np.array(r1)
    g1=np.array(g1)
    b1=np.array(b1)
    
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
    
    
    
    indexR=nr[[8,16,32,64,96,128,160,192,224,255]]
    indexG=ng[[8,16,32,64,96,128,160,192,224,255]]
    indexB=nb[[8,16,32,64,96,128,160,192,224,255]]
    
    Tgray=[8,16,32,64,96,128,160,192,224,255]
    dg=[]

    wxx=[]
    wyy=[]
    plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    for gray in range(len(indexR)): #r1.Tone.astype(np.int32).values: 
        #plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
        #gray=1
        #0 row -1是找最接近的最後一個
        
        r=indexR[gray]
        g=indexG[gray]
        b=indexB[gray]
        wx=[]
        wy=[]
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
        
        plt.scatter(wx,wy)
        plt.plot(wx,wy)
    #化點
    #dg_df=pd.DataFrame(np.array(dg),columns=['gray','R','G','B'])
    dg_df=np.array(dg)
    fig, ax = plt.subplots()
    ax.plot(dg_df[:,0],rt_array,'--r',label='R Lum Target')
    ax.plot(dg_df[:,0],
            ry_ip1d(dg_df[:,1]),
            '-r',label='R Lum real ca410')
    ax.legend()
    plt.show()
    
    fig, ax = plt.subplots()
    ax.plot(dg_df[:,0],gt_array,'--g',label='G Lum Target')#,marker='^')
    ax.plot(dg_df[:,0],
            gy_ip1d(dg_df[:,2]),
            '-g',label='G Lum Real ca410')
    ax.legend(loc='best')
    plt.show()
    
    fig, ax = plt.subplots()
    ax.plot(dg_df[:,0],bt_array,'--b',label='B Lum Target')#,marker='^')
    ax.plot(dg_df[:,0],
            by_ip1d(dg_df[:,3]),
            '-b',label='B Lum Real ca410')
    ax.legend(loc='best')
    plt.show()
    
    
    plt.plot(Tgray,dg_df[:,1],'-r',marker='.')
    plt.plot(Tgray,dg_df[:,2],'-g',marker='.')
    plt.plot(Tgray,dg_df[:,3],'-b',marker='.')
    plt.xlim(0,255)
    plt.xticks(Tgray)
    plt.show()
  
    
    plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    plt.scatter(wxx,wyy)
    plt.xlim(-0.08, 0.8)
    plt.ylim(-0.08, 0.9)
    plt.show()
    print(np.array([wxx,wyy]))
    
    return rt_array,gt_array,bt_array




def calibrate_color_ratio_XYZ_model(ca410_data,target_L,target_x,target_y):
    #r1=pd.read_csv(ca410_data,skiprows=260,encoding= 'unicode_escape')[0:256]
    #g1=pd.read_csv(ca410_data,skiprows=519,encoding= 'unicode_escape')[0:256]
    #b1=pd.read_csv(ca410_data,skiprows=778,encoding= 'unicode_escape')[0:256]
    # r1.Y.iloc[0]=0
    # g1.Y.iloc[0]=0
    # b1.Y.iloc[0]=0
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
    
    indexR=nr[[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]
    indexG=ng[[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]
    indexB=nb[[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]
    
    #indexR=nr[[8,16,32,64,96,128,160,192,224,255]]
    #indexG=ng[[8,16,32,64,96,128,160,192,224,255]]
    #indexB=nb[[8,16,32,64,96,128,160,192,224,255]]
    
    #Tgray=[8,16,32,64,96,128,160,192,224,255]
    Tgray=[7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]
    dg=[]
    wxx=[]
    wyy=[]
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
        
        plt.scatter(wx,wy)
        plt.plot(wx,wy)
        
    #化點
    #dg_df=pd.DataFrame(np.array(dg),columns=['gray','R','G','B'])
    dg_df=np.array(dg)
    fig, ax = plt.subplots()
    ax.plot(dg_df[:,0],rt_array,'--r',label='R Lum Target')
    ax.plot(dg_df[:,0],
            ry_ip1d(dg_df[:,1]),
            '-r',label='R Lum real ca410')
    ax.legend()
    plt.show()
    
    fig, ax = plt.subplots()
    ax.plot(dg_df[:,0],gt_array,'--g',label='G Lum Target')#,marker='^')
    ax.plot(dg_df[:,0],
            gy_ip1d(dg_df[:,2]),
            '-g',label='G Lum Real ca410')
    ax.legend(loc='best')
    plt.show()
    
    fig, ax = plt.subplots()
    ax.plot(dg_df[:,0],bt_array,'--b',label='B Lum Target')#,marker='^')
    ax.plot(dg_df[:,0],
            by_ip1d(dg_df[:,3]),
            '-b',label='B Lum Real ca410')
    ax.legend(loc='best')
    plt.show()
    
    
    plt.plot(Tgray,dg_df[:,1],'-r',marker='.')
    plt.plot(Tgray,dg_df[:,2],'-g',marker='.')
    plt.plot(Tgray,dg_df[:,3],'-b',marker='.')
    plt.xlim(0,255)
    plt.xticks(Tgray)
    plt.show()
  
    
    plot_chromaticity_diagram_CIE1931(standalone=False,title="color space",bounding_box=(-0.1, 1, -0.1, 1))
    plt.scatter(wxx,wyy)
    plt.xlim(-0.08, 0.8)
    plt.ylim(-0.08, 0.9)
    plt.show()
    print(np.array([wxx,wyy]))
    return rt_array,gt_array,bt_array,dg




def output_DG(save_path,prefix_name,ca410_data,rt,gt,bt):
    
    rt=np.insert(rt, 0,0)
    gt=np.insert(gt, 0,0)
    bt=np.insert(bt, 0,0)

    #gray=np.array([0,8,16,32,64,96,128,160,192,224,256])*16
    gray=np.array([0,7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255])*4
    r_t_it1d=interp1d(gray,rt,fill_value='extrapolate')
    g_t_it1d=interp1d(gray,gt,fill_value='extrapolate')
    b_t_it1d=interp1d(gray,bt,fill_value='extrapolate')

    nr_t=r_t_it1d([i for i in range(1024)]).clip(0,1023)
    ng_t=g_t_it1d([i for i in range(1024)]).clip(0,1023)
    nb_t=b_t_it1d([i for i in range(1024)]).clip(0,1023)

       
    
    r1=pd.read_csv(ca410_data,skiprows=260,encoding= 'unicode_escape')[0:256]
    g1=pd.read_csv(ca410_data,skiprows=519,encoding= 'unicode_escape')[0:256]
    b1=pd.read_csv(ca410_data,skiprows=778,encoding= 'unicode_escape')[0:256]
    
    r1.Y.iloc[0]=0
    g1.Y.iloc[0]=0
    b1.Y.iloc[0]=0
    b1.Y=np.sort(b1.Y.values.astype(np.float64))
    
    # r_dg=interp1d(r1.Y.values.astype(np.float64),[i*256 for i in range(256)], fill_value='extrapolate')
    # g_dg=interp1d(g1.Y.values.astype(np.float64),[i*256 for i in range(256)], fill_value='extrapolate')
    # b_dg=interp1d(b1.Y.values.astype(np.float64),[i*256 for i in range(256)], fill_value='extrapolate')
    
    r_dg=interp1d(r1.Y.values.astype(np.float64),[i*16 for i in range(256)], fill_value='extrapolate')
    g_dg=interp1d(g1.Y.values.astype(np.float64),[i*16 for i in range(256)], fill_value='extrapolate')
    b_dg=interp1d(b1.Y.values.astype(np.float64),[i*16 for i in range(256)], fill_value='extrapolate')
    
    
    R=r_dg(nr_t).astype('uint32').clip(0,4095)
    G=g_dg(ng_t).astype('uint32').clip(0,4095)
    B=(b_dg(nb_t).astype('uint32')).clip(0,4095)
    
    DGR=[]
    for i in range(len(R)):
        DGR.append(hex(R[i]//256)[2:].upper().zfill(2)+hex(R[i]%256)[2:].upper().zfill(2))
    DGG=[]    
    for i in range(len(R)):        
        DGG.append(hex(G[i]//256)[2:].upper().zfill(2)+hex(G[i]%256)[2:].upper().zfill(2))

    DGB=[]    
    for i in range(len(R)):
        DGB.append(hex(B[i]//256)[2:].upper().zfill(2)+hex(B[i]%256)[2:].upper().zfill(2))
    
    
    DG=[]
    for i in range(1,len(DGR),2):
        for j in range(0,5,2):
            DG.append((DGR[i-1][1:]+DGR[i][1:])[j:j+2])
    
    for i in range(1,len(DGG),2):
        for j in range(0,5,2):
            DG.append((DGG[i-1][1:]+DGG[i][1:])[j:j+2])
            
    for i in range(1,len(DGB),2):
        for j in range(0,5,2):
            DG.append((DGB[i-1][1:]+DGB[i][1:])[j:j+2])
    
    
    
    
    addr=['@'+hex(i)[2:].upper()+" " for i in range(113152,117760,1)]
    lut=''
    for i in range(len(addr)):
        tmp=addr[i]+DG[i]+'\n'
        if i == len(addr)-1:
            tmp=addr[i]+DG[i]
        
        lut=lut+tmp
    
    #lut=lut+'\n'+'@021B 10'
    #save_path=r'D:\RD Lab\Y173_data\20230922\AG'
    file_name=prefix_name+'.DESIGN_HEX_ROM'
    text_file = open(os.path.join(save_path,file_name), "w")
    text_file.write(lut)
    text_file.close()
    print("LUT save in "+os.path.join(save_path,file_name))
    return R,G,B



save_path=r'E:\V161\L4A\DG_HEX'
file_name='test3'
ca410_data=r'D:\RD Lab\Y173_data\20230922\AG\GammaMeasData_AG_02.csv'
rt,gt,bt,dg=calibrate_color_ratio_XYZ_model(ca410_data,1200,0.313,0.329)
R,G,B=output_DG(save_path,file_name,ca410_data,rt,gt,bt)



# root=r'E:\V161\L4A\CA410'
# ca410_file=os.listdir(r'E:\V161\L4A\CA410')
# save_path=r'E:\V161\L4A\DG_HEX'
# for i in ca410_file:
#     if i.startswith('GammaMeasData'):
#         path=os.path.join(root,i)
    
#         file_name=path.split('GammaMeasData')[-1].split('.')[0].split('_')[-1].zfill(3)
#         R,G,B=output_DG(save_path,file_name,path,rt,gt,bt)


# root=r'D:\UserShare\Demura_V161\20230712\DG_tuning'
# ca410_file=os.listdir(root)
# R=[]
# G=[]
# B=[]
# W=[]

# for i in ca410_file:
#     if i.endswith('demura.csv'):
        

#         Rdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=261,max_rows=256,usecols=(1,2,3))
#         Gdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=520,max_rows=256,usecols=(1,2,3))
#         Bdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=779,max_rows=256,usecols=(1,2,3))
#         Wdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=1038,max_rows=256,usecols=(1,2,3))
#         R.append(np.array([Rdf[8,1],Rdf[16,1],Rdf[32,1],Rdf[64,1],Rdf[192,1]]))
#         G.append(np.array([Gdf[8,1],Gdf[16,1],Gdf[32,1],Gdf[64,1],Gdf[192,1]]))
#         B.append(np.array([Bdf[8,1],Bdf[16,1],Bdf[32,1],Bdf[64,1],Bdf[192,1]]))
#         W.append(np.array([Wdf[8,1],Wdf[16,1],Wdf[32,1],Wdf[64,1],Wdf[192,1]]))
        
        
#         plt.plot([j for j in range(256)],Bdf[:,1],label=i.split('_')[1])
#     plt.title('B LED after Demura')
#     plt.legend()
    
# R=np.array(R)
# G=np.array(G)
# B=np.array(B)

# root=r'D:\UserShare\Demura_V161\20230712\DG_tuning'
# ca410_file=os.listdir(root)
# R=[]
# G=[]
# B=[]
# W=[]

# for i in ca410_file:
#     if i.endswith('demura_DG.csv'):
        

#         Rdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=261,max_rows=256,usecols=(1,2,3))
#         Gdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=520,max_rows=256,usecols=(1,2,3))
#         Bdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=779,max_rows=256,usecols=(1,2,3))
#         Wdf=np.loadtxt(os.path.join(root,i),delimiter=",",encoding="utf-8",skiprows=1038,max_rows=256,usecols=(1,2,3))
#         R.append(np.array([Rdf[8,1],Rdf[16,1],Rdf[32,1],Rdf[64,1],Rdf[192,1]]))
#         G.append(np.array([Gdf[8,1],Gdf[16,1],Gdf[32,1],Gdf[64,1],Gdf[192,1]]))
#         B.append(np.array([Bdf[8,1],Bdf[16,1],Bdf[32,1],Bdf[64,1],Bdf[192,1]]))
#         W.append(np.array([Wdf[8,1],Wdf[16,1],Wdf[32,1],Wdf[64,1],Wdf[192,1]]))
        
        
#         plt.plot([j for j in range(256)],Wdf[:,1],label=i.split('_')[1])
#     plt.title('W LED same DG code')
#     plt.legend()
    
# R=np.array(R)
# G=np.array(G)
# B=np.array(B)