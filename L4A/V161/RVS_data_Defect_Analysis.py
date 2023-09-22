import numpy as np
import os,cv2
import pandas as pd
import matplotlib.pyplot as plt
import PIL.Image


resolution_y=240
resolution_x=540
root_path=r'\\auo\rd\Platform\COMMON\LAB\RRCBB3\TEMP\L4A\0911'
defect_folder=os.listdir(root_path)
root_save_path=r'\\auo\rd\Platform\COMMON\LAB\RRCBB3\TEMP\L4A\0911\Defect_MAP'
root_save_path2=r'\\auo\rd\Platform\COMMON\LAB\RRCBB3\TEMP\L4A\0911\Defect_MAP_G4'


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



###On dot 計算####
dot_RGB=[]
for folder in defect_folder:
    
    print(folder)

    
    try:
        R_ondot=np.rot90(np.array(PIL.Image.open(os.path.join(root_path,folder,'cpimg','mark_R.bmp')).convert('RGB'))[:,:,0],1).flatten()
        Rdot=len(np.where(R_ondot==0)[0])
    except:
        Rdot=0
        
    try:
        G_ondot=np.rot90(np.array(PIL.Image.open(os.path.join(root_path,folder,'cpimg','mark_G.bmp')).convert('RGB'))[:,:,1],1).flatten()
        Gdot=len(np.where(G_ondot==0)[0])
    except:
        Gdot=0
        
    try:
        B_ondot=np.rot90(np.array(PIL.Image.open(os.path.join(root_path,folder,'cpimg','mark_B.bmp')).convert('RGB'))[:,:,2],1).flatten()
        Bdot=len(np.where(B_ondot==0)[0])
    except:
        Bdot=0
    dot_RGB.append((folder,Rdot,Gdot,Bdot))
        
pd.DataFrame(dot_RGB,columns=['CHIP ID','R Pts','G Pts','B Pts']).to_csv(os.path.join(root_save_path, 'brigthtdot_pts.csv'))
