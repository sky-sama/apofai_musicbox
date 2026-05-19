import sys
from tkinter import filedialog

import concurrent.futures
from pygame.math import Vector2 as Vec2
import numpy as np
import datamgr
import scipy.io.wavfile as wav

def print_progress(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', unfill=' ', done='已完成\n'):
    """
    在控制台打印进度条
    iteration: 当前迭代次数
    total: 总迭代次数
    prefix: 进度条前缀字符串
    suffix: 进度条后缀字符串
    decimals: 进度的小数点位数
    length: 进度条的总长度
    fill: 进度条的填充字符
    unfill: 进度条的空白字符
    done: 完成时的额外显示
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + unfill * (length - filled_length)
    sys.stdout.write('\r%s[%s] %s%%%s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    # 在完成时打印新行
    if iteration == total:
        sys.stdout.write(done)
        

def subprocess(args):
    p,angledata,bpm,deltaoffset,hold,triple,pause,deltax,deltay,path=args
    angledata=",".join(str(i) for i in angledata)
    bpm=",".join(str(i) for i in bpm)
    deltaoffset=",".join(str(i) for i in deltaoffset)
    hold=",".join(str(i) for i in hold)
    triple=",".join(str(i) for i in triple)
    pause=",".join(str(i) for i in pause)
    deltax=",".join(str(i) for i in deltax)
    deltay=",".join(str(i) for i in deltay)

    sys.stdout.write('正在写入文件……\r')
    name=path.split("\\")[-1][:-7]
    with open(path[:-7]+f'-{p}.adopac',"wt",1,"GBK") as file:
        file.write(f"\n{name}_hitsound.wav\n\
    0\n\
    0\n\
    {angledata}\n")
        file.write(f"\
    {bpm}\n")
        file.write(f"\
    0,{deltaoffset}\n")
        file.write(f"\
    {hold}\n")
        file.write(f"\
    {triple}\n")
        file.write(f"\
    {pause}\n")
        file.write(f"\
    {deltax}\n")
        file.write(f"\
    {deltay}\n\
    -999999999,Player:0,Linear,0.00,0.00,0.00,100.00,0.00\n")
    print(f"谱面文件已保存至{path[:-3]+'pac'}")
    
def gen_sound(args):
    p,offset,volume=args
    _,beat=wav.read("hit.wav")
    beat= (beat[:,0]+beat[:,1])/2
    pin=np.int32(offset[1:]*48000)
    hitsound=[0.0]*(pin[-1]+len(beat))
    hitsound=np.array(hitsound)
    x=1
    for i in pin:
        hitsound[i:i+len(beat)]+=beat*volume[x]
        x+=1
        print_progress(i, pin.max(),f'正在生成打拍音:{p}')
    #hitsound=np.arcsinh(hitsound)
    hitsound=np.int16(hitsound/hitsound.max()*32767)
    return hitsound

if __name__ == "__main__":
    path = filedialog.askopenfilename(defaultextension=".adofai")

    Datamgr=datamgr.ApofaiDtmgr(path)
    if not Datamgr.success:
        print("读取失败")
        exit()
    sys.stdout.write('正在整理数据：(1/8)angledata\r')
    angledata=[i.angle for i in Datamgr.tiles]
    sys.stdout.write('正在整理数据：(2/8)bpm\r')
    bpm=np.array([i.bpm for i in Datamgr.tiles])
    clock_wise=np.array([i.clock_wise for i in Datamgr.tiles])
    bpm*=clock_wise*2-1
    sys.stdout.write('正在整理数据：(3/8)offset\r')
    offset=np.array([i.offset for i in Datamgr.tiles])
    deltaoffset=offset[1:]-offset[:-1]
    deltaoffset=np.int32(deltaoffset*1000000000)
    sys.stdout.write('正在整理数据：(4/8)hold\r')
    hold=[1 if i.hold else 0 for i in Datamgr.tiles]
    sys.stdout.write('正在整理数据：(5/8)triple\r')
    triple=[0 for i in Datamgr.tiles]
    sys.stdout.write('正在整理数据：(6/8)pause\r')
    pause=[i.pause for i in Datamgr.tiles]
    sys.stdout.write('正在整理数据：(7/8)deltapos\r')
    deltapos=[i.deltapos for i in Datamgr.tiles]
    deltax=[i.x for i in deltapos]
    deltay=[i.y for i in deltapos]
    sys.stdout.write('正在整理数据：(8/8)volume\r')
    cam='-999999999,Player:0,Linear,0.00,0.00,0.00,100.00,0.00'
    volume=[i.volume for i in Datamgr.tiles]

    '''sys.stdout.write('正在转换为文本……\r')
    angledata=",".join(str(i) for i in angledata)
    bpm=",".join(str(i) for i in bpm)
    deltaoffset=",".join(str(i) for i in deltaoffset)
    hold=",".join(str(i) for i in hold)
    triple=",".join(str(i) for i in triple)
    pause=",".join(str(i) for i in pause)
    deltax=",".join(str(i) for i in deltax)
    deltay=",".join(str(i) for i in deltay)

    sys.stdout.write('正在写入文件……\r')
    name=path.split("\\")[-1][:-7]
    with open(path[:-3]+'pac',"wt",1,"GBK") as file:
        file.write(f"\n{name}_hitsound.wav\n\
    0\n\
    0\n\
    {angledata}\n")
        file.write(f"\
    {bpm}\n")
        file.write(f"\
    0,{deltaoffset}\n")
        file.write(f"\
    {hold}\n")
        file.write(f"\
    {triple}\n")
        file.write(f"\
    {pause}\n")
        file.write(f"\
    {deltax}\n")
        file.write(f"\
    {deltay}\n\
    -999999999,Player:0,Linear,0.00,0.00,0.00,100.00,0.00\n")
    print(f"谱面文件已保存至{path[:-3]+'pac'}")


    _,beat=wav.read("hit.wav")
    beat= (beat[:,0]+beat[:,1])/2
    #beat=np.sinh(beat*1e-10)
    #beat=beat*0+32767.0
    pin=np.int32(offset[1:]*44100)
    hitsound=[0.0]*(pin[-1]+len(beat))
    hitsound=np.array(hitsound)
    x=1
    for i in pin:
        hitsound[i:i+len(beat)]+=beat*volume[x]
        x+=1
        print_progress(i, pin.max(),'正在生成打拍音')
    #hitsound=np.arcsinh(hitsound)
    hitsound=np.int16(hitsound/hitsound.max()*32767)
    wav.write(f"{path[:-7]}_hitsound.wav",44100,hitsound)'''

    #args_list=[(p,angledata[p*100000:(p+1)*100000-1],bpm[p*100000:(p+1)*100000-1],deltaoffset[p*100000:(p+1)*100000-1],hold[p*100000:(p+1)*100000-1],triple[p*100000:(p+1)*100000-1],pause[p*100000:(p+1)*100000-1],deltax[p*100000:(p+1)*100000-1],deltay[p*100000:(p+1)*100000-1],path) for p in range(len(angledata)//100000+1)]

    sound_args_list=[(p,offset[p*100000:(p+1)*100000-1],volume[p*100000:(p+1)*100000-1]) for p in range(len(angledata)//100000+1)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(gen_sound, sound_args_list))
    
    '''with concurrent.futures.ProcessPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(subprocess, args_list))'''
    finnal_result=[]
    #倒序读取
    for result in results[::-1]:
        if len(finnal_result)==0:
            finnal_result=result
        else:
            finnal_result[:len(result)]+=result
    wav.write(f"{path[:-7]}_hitsound.wav",48000,finnal_result)