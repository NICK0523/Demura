# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 13:08:28 2024

@author: NickNHHuang
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import csv
##############################################################################################################
path=r'D:\UserShare\L4A\VKV3757681A0113\DATA(NEW)'
chipID='VKV3757681A0113'
#Red
R24=(np.loadtxt(os.path.join(path,'Red24.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R28=(np.loadtxt(os.path.join(path,'Red28.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R32=(np.loadtxt(os.path.join(path,'Red32.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R40=(np.loadtxt(os.path.join(path,'Red40.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R48=(np.loadtxt(os.path.join(path,'Red48.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R56=(np.loadtxt(os.path.join(path,'Red56.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R60=(np.loadtxt(os.path.join(path,'Red60.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R64=(np.loadtxt(os.path.join(path,'Red64.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R80=(np.loadtxt(os.path.join(path,'Red80.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R96=(np.loadtxt(os.path.join(path,'Red96.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R128=(np.loadtxt(os.path.join(path,'Red128.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R160=(np.loadtxt(os.path.join(path,'Red160.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R192=(np.loadtxt(os.path.join(path,'Red192.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R224=(np.loadtxt(os.path.join(path,'Red224.csv'),delimiter=",",encoding="utf-8")).flatten('C')
R255=(np.loadtxt(os.path.join(path,'Red255.csv'),delimiter=",",encoding="utf-8")).flatten('C')

#Green
G24=(np.loadtxt(os.path.join(path,'Green24.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G28=(np.loadtxt(os.path.join(path,'Green28.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G32=(np.loadtxt(os.path.join(path,'Green32.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G40=(np.loadtxt(os.path.join(path,'Green40.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G48=(np.loadtxt(os.path.join(path,'Green48.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G56=(np.loadtxt(os.path.join(path,'Green56.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G60=(np.loadtxt(os.path.join(path,'Green60.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G64=(np.loadtxt(os.path.join(path,'Green64.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G80=(np.loadtxt(os.path.join(path,'Green80.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G96=(np.loadtxt(os.path.join(path,'Green96.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G128=(np.loadtxt(os.path.join(path,'Green128.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G160=(np.loadtxt(os.path.join(path,'Green160.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G192=(np.loadtxt(os.path.join(path,'Green192.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G224=(np.loadtxt(os.path.join(path,'Green224.csv'),delimiter=",",encoding="utf-8")).flatten('C')
G255=(np.loadtxt(os.path.join(path,'Green255.csv'),delimiter=",",encoding="utf-8")).flatten('C')
#Blue
B24=(np.loadtxt(os.path.join(path,'Blue24.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B28=(np.loadtxt(os.path.join(path,'Blue28.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B32=(np.loadtxt(os.path.join(path,'Blue32.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B40=(np.loadtxt(os.path.join(path,'Blue40.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B48=(np.loadtxt(os.path.join(path,'Blue48.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B56=(np.loadtxt(os.path.join(path,'Blue56.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B60=(np.loadtxt(os.path.join(path,'Blue60.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B64=(np.loadtxt(os.path.join(path,'Blue64.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B80=(np.loadtxt(os.path.join(path,'Blue80.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B96=(np.loadtxt(os.path.join(path,'Blue96.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B128=(np.loadtxt(os.path.join(path,'Blue128.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B160=(np.loadtxt(os.path.join(path,'Blue160.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B192=(np.loadtxt(os.path.join(path,'Blue192.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B224=(np.loadtxt(os.path.join(path,'Blue224.csv'),delimiter=",",encoding="utf-8")).flatten('C')
B255=(np.loadtxt(os.path.join(path,'Blue255.csv'),delimiter=",",encoding="utf-8")).flatten('C')
#################################################################################################################
#Total
R=np.array([R24,R28,R32,R40,R48,R56,R60,R64,R80,R96,R128,R160,R192,R224,R255])
G=np.array([G24,G28,G32,G40,G48,G56,G60,G64,G80,G96,G128,G160,G192,G224,G255])
B=np.array([B24,B28,B32,B40,B48,B56,B60,B64,B80,B96,B128,B160,B192,B224,B255])
#################################################################################################################
Rmean = np.mean(R255)
Gmean = np.mean(G255)
Bmean = np.mean(B255)
Rmax = np.max(R255)
Gmax = np.max(G255)
Bmax = np.max(B255)
ratio=0.7
targetR=180
targetG=500
targetB=50

start=0
end=129600
countR=0
locationR=np.random.randint(1,size=(50,2))
print(chipID)
print("Red")
for i in range(start,end,1):
     plt.plot(R[:,i],'-',markersize=4,color=(1,0,0))
#    if R[14,i]<(targetR*ratio):
#        locationR[countR]=[int(i/540),i%540]
#        print("x",int(i/540),"y",i%540)
#        countR=countR+1
#print(countR)    
plt.xlim(0,14)
plt.title('Gamma per pixel')
plt.xlabel('Gray Level')
plt.ylabel('nits')
plt.grid()            
plt.show()

#for i in range(0,240,1):    
#    for j in range(0,540,1):
#        #plt.plot(R[:,i,j],'-',markersize=4,color=(1,0,0))
#        if R[14,i,j]<150:
#            locationR[z]=[i,j]
#            print("x",i,"y",j)
#            z=z+1
#        elif R[14,i,j]>150:
#            locationR[z]=[i,j]
#            print("x",i,"y",j)
#            z=z+1
#print(z)            
#plt.show()      
     
countG=0
locationG=np.random.randint(1,size=(50,2))              
print("Green")
for i in range(start,end,1):
    plt.plot(G[:,i],'-',markersize=4,color=(0,1,0))
#    if G[14,i]<(targetG*ratio):
#        locationG[countG]=[int(i/540),i%540]
#        print("x",int(i/540),"y",i%540)
#        countG=countG+1
print(countG)  
plt.xlim(0,14)
plt.title('Gamma per pixel')
plt.xlabel('Gray Level')
plt.ylabel('nits')
plt.grid()            
plt.show()

#for i in range(0,240,1):    
#    for j in range(0,540,1):
#        #plt.plot(G[:,i,j],'-',markersize=4,color=(0,1,0))
#        if G[14,i,j]<300:
#            locationG[z]=[i,j]
#            print("x",i,"y",j)
#            z=z+1      
#print(z) 
#plt.show()   

countB=0
locationB=np.random.randint(1,size=(50,2))        
print("Blue")
for i in range(start,end,1):
    plt.plot(B[:,i],'-',markersize=4,color=(0,0,1))
#    if B[14,i]<(targetB*ratio):
#        locationB[countB]=[int(i/540),i%540]
#        print("x",int(i/540),"y",i%540)
#        countB=countB+1
print(countB)
plt.xlim(0,14)
plt.title('Gamma per pixel')
plt.xlabel('Gray Level')
plt.ylabel('nits')
plt.grid()            
plt.show()  

#for i in range(0,240,1):    
#    for j in range(0,540,1):
#        #plt.plot(B[:,i,j],'-',markersize=4,color=(0,0,1))  
#        if B[14,i,j]<20:
#            locationB[z]=[i,j]
#            print("x",i,"y",j)
#            z=z+1          
#print(z) 
#plt.show()      
locationRGB=np.hstack((locationR,locationG,locationB))        
##############################################################################################################
#with open("Defect_Location_VKV3757682A1413.csv", "w", newline="") as file:  
#    mywriter = csv.writer(file, delimiter=",")
#    mywriter.writerow(['Red',' ','Green',' ','Blue'])
#    mywriter.writerow(['Total',countR,'Total',countG,'Total',countB])
#    mywriter.writerow(np.array(['X','Y','X','Y','X','Y']))
#    mywriter.writerows(locationRGB)
#file.close()