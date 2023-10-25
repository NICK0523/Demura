# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 09:18:08 2023

@author: NickNHHuang
"""

import numpy as np
import os
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from colour.plotting import plot_chromaticity_diagram_CIE1931
#####################################################################################################################
def extrapolate_RGB(root_path):
    Rdf1=np.loadtxt(root_path,delimiter=",",encoding="utf-8",skiprows=1,max_rows=256,usecols=(1,2,3,4,5))
    Gdf1=np.loadtxt(root_path,delimiter=",",encoding="utf-8",skiprows=258,max_rows=256,usecols=(1,2,3,4,5))
    Bdf1=np.loadtxt(root_path,delimiter=",",encoding="utf-8",skiprows=515,max_rows=256,usecols=(1,2,3,4,5))
    
    R=Rdf1[::-1]
    G=Gdf1[::-1]
    B=Bdf1[::-1]
    
    
    return R,G,B
def calibrate_color_ratio_XYZ_model(R_DATA,G_DATA,B_DATA,target_L,target_x,target_y):
    
    r1=R_DATA
    g1=G_DATA
    b1=B_DATA
    
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
    
#    indexR=nr[[11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]
#    indexG=ng[[11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]
#    indexB=nb[[11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]]  
#    Tgray=[11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255]
    
    indexR=nr[[i for i in range(7,256,4)]]
    indexG=ng[[i for i in range(7,256,4)]]
    indexB=nb[[i for i in range(7,256,4)]]
    Tgray=[i for i in range(7,256,4)]
    
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
def output_DG(save_path,prefix_name,R_DATA,G_DATA,B_DATA,rt,gt,bt):
    
    rt=np.insert(rt, 0,0)
    gt=np.insert(gt, 0,0)
    bt=np.insert(bt, 0,0)

#    gray=np.array([0,7,11,15,23,31,39,47,63,79,95,111,127,143,159,175,191,207,215,223,231,239,243,247,255])*16    
    gray=np.array([i for i in range(7,256,4)])*16
    gray=np.insert(gray, 0,0)
    
    r_t_it1d=interp1d(gray,rt,fill_value='extrapolate')
    g_t_it1d=interp1d(gray,gt,fill_value='extrapolate')
    b_t_it1d=interp1d(gray,bt,fill_value='extrapolate')

    nr_t=r_t_it1d([i for i in range(4096)]).clip(0,4095)
    ng_t=g_t_it1d([i for i in range(4096)]).clip(0,4095)
    nb_t=b_t_it1d([i for i in range(4096)]).clip(0,4095)

       
    
    r1=R_DATA
    g1=G_DATA
    b1=B_DATA
    
#    r1.Y.iloc[0]=0
#    g1.Y.iloc[0]=0
#    b1.Y.iloc[0]=0
#    b1.Y=np.sort(b1.Y.values.astype(np.float64))
    
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
    
    lut='@021B 10'+'\n'+lut
        
    file_name=prefix_name+'.DESIGN_HEX_ROM'
    text_file = open(os.path.join(save_path,file_name), "w")
    text_file.write(lut)
         
    print("LUT save in "+os.path.join(save_path,file_name))
    return R,G,B
##########################################################################################################################

root_path=r'U:\gamma curve_admesy\gamma curve_admesy\prometheus\RU.csv'
r1,g1,b1=extrapolate_RGB(root_path)
rr,gg,bb,dg=calibrate_color_ratio_XYZ_model(r1,g1,b1,800,0.30,0.31)

root=r'U:\gamma curve_admesy\gamma curve_admesy\prometheus'
ca410_file=os.listdir(root)
save_path=r'U:\gamma curve_admesy\gamma curve_admesy\prometheus\DG_HEX'
for i in ca410_file:
    if i.startswith('GammaMeasDataLU'):
        path=os.path.join(root,i)
    
#        file_name=path.split('GammaMeasData')[-1].split('.')[0].split('_')[-1].zfill(3)
        file_name='LD'
        R,G,B=output_DG(save_path,file_name,r1,g1,b1,rr,gg,bb)