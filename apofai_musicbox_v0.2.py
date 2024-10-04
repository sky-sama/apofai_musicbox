from mido import MidiFile
import numpy as np
import os.path as pth
import time
import sys

VER="v0.2"
A4=440

def print_progress(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', unfill=' ', done='已完成'):
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
        print(done)

class pathiterator:
    '''核心 序列生成器'''
    def __init__(self, note:int, offset:float) -> None:
        self.note=note
        self.gap=1/(A4*2**((note-69)/12))
        self.next=offset
    def iteratenext(self) -> float:
        self.next+=self.gap
        return self.gap

def make(peak:np.ndarray,path:str,exdescription="",wavname="",rate=1,bpm:int=None):
    '''通用型直达式谱面生成器可能是最终版。将时间序列(numpy:array)直接转换为adofai谱面文件。
    peak:时间序列。要求必须升序排列。降序的值会被强制移到先前最大的值之后。相同值会被转换为0.01度伪双押。
    path:文件将要保存的路径（可以包含一部分文件名）。如果填写了音频文件名，则此路径必须是音频文件所在的路径。
    exdescription:额外描述。作为后缀添加到文件名末尾。
    wavname:音频文件名称。请不要使用完整路径。
    rate:时间序列的单位精度。单位：hz。如，若时间序列以秒为单位，则填1（可缺省）；若时间序列频率为44100hz，则填44100。
    bpm:指定谱面bpm。缺省自动填写（不一定合适）bpm'''
    if len(peak)==0:
        print("你干嘛，怎么一个音也没有，老子不干了！")
        return
    offset=peak/rate
    #np.savetxt(f"{name}_{val}_data.txt",offset)
    if bpm==None:
        if len(peak)==1:
            print("你干嘛，怎么只有一个音，这让我怎么算BPM")
            return
        offset0=offset[1:]-offset[:-1]
        bpmdt=np.median(offset0)
        bpm=np.int32(64/bpmdt)
    bpmdt=60/bpm
    offseti=offset[0]
    offset=offset-offseti
    overangle=offset/bpmdt*180
    for i in range(len(overangle)-1):
        if overangle[i+1]-overangle[i]<0.01:
            overangle[i+1]=overangle[i]+0.01
    if len(overangle)%2==0:
        all=np.reshape(overangle,(2,-1),"F")
        fire=np.concatenate((all[0][1:],[0]))
        ice=all[1]
        even=False
    else:
        all=np.reshape(overangle[1:],(2,-1),"F")
        ice=all[0]
        fire=all[1]
        even=True
    combineangle=np.array([ice,fire])
    deltaangle=overangle-np.concatenate(([0],overangle[:-1]))
    extraround=np.floor(deltaangle/360-1e-126)*2
    for i in range(len(combineangle[0])-1):
        if (deltaangle[2*i+1])%360==0 and extraround[2*i+1]!=0:
            extraround[2*i+1]+=1
    combineangle=np.array([(180-combineangle[0])%360,
                           (360-combineangle[1])%360
                          ])
    tmp=combineangle.reshape(-1,order="F")
    if not even:
        tmp=tmp[:-1]
    angledata=", ".join(str(i) for i in tmp)
  
    tmpstr="{\n\
	\"angleData\": [0, "+f"{angledata}"+"], \n\
	\"settings\":\n\
	{\n\
		\"version\": 13 ,\n\
		\"artist\": \"\", \n\
		\"specialArtistType\": \"None\", \n\
		\"artistPermission\": \"\", \n\
		\"song\": \"\", \n\
		\"author\": \"apofaiautomaker\", \n\
		\"separateCountdownTime\": true, \n\
		\"previewImage\": \"\", \n\
		\"previewIcon\": \"\", \n\
		\"previewIconColor\": \"003f52\", \n\
		\"previewSongStart\": 0, \n\
		\"previewSongDuration\": 10, \n\
		\"seizureWarning\": false, \n\
		\"levelDesc\": \"\", \n\
		\"levelTags\": \"\", \n\
		\"artistLinks\": \"\", \n\
		\"speedTrialAim\": 0, \n\
		\"difficulty\": 1, \n\
		\"requiredMods\": [],\n\
		\"songFilename\": \""+f"{wavname}"+"\", \n\
		\"bpm\": "+f"{bpm}"+", \n\
		\"volume\": 100, \n\
		\"offset\": "+f"{np.int32(offseti*1000)}"+", \n\
		\"pitch\": 100, \n\
		\"hitsound\": \"Kick\", \n\
		\"hitsoundVolume\": 100, \n\
		\"countdownTicks\": 4,\n\
		\"trackColorType\": \"Rainbow\", \n\
		\"trackColor\": \"debb7b\", \n\
		\"secondaryTrackColor\": \"ffffff\", \n\
		\"trackColorAnimDuration\": 2, \n\
		\"trackColorPulse\": \"Forward\", \n\
		\"trackPulseLength\": 100, \n\
		\"trackStyle\": \"NeonLight\", \n\
		\"trackTexture\": \"\", \n\
		\"trackTextureScale\": 1, \n\
		\"trackGlowIntensity\": 100, \n\
		\"trackAnimation\": \"None\", \n\
		\"beatsAhead\": 3, \n\
		\"trackDisappearAnimation\": \"Shrink\", \n\
		\"beatsBehind\": 0,\n\
		\"backgroundColor\": \"000000\", \n\
		\"showDefaultBGIfNoImage\": true, \n\
		\"showDefaultBGTile\": true, \n\
		\"defaultBGTileColor\": \"101121\", \n\
		\"defaultBGShapeType\": \"Default\", \n\
		\"defaultBGShapeColor\": \"ffffff\", \n\
		\"bgImage\": \"\", \n\
		\"bgImageColor\": \"ffffff\", \n\
		\"parallax\": [100, 100], \n\
		\"bgDisplayMode\": \"FitToScreen\", \n\
		\"imageSmoothing\": true, \n\
		\"lockRot\": false, \n\
		\"loopBG\": false, \n\
		\"scalingRatio\": 100,\n\
		\"relativeTo\": \"Player\", \n\
		\"position\": [0, 0], \n\
		\"rotation\": 0, \n\
		\"zoom\": 150, \n\
		\"pulseOnFloor\": true,\n\
		\"bgVideo\": \"\", \n\
		\"loopVideo\": false, \n\
		\"vidOffset\": 0, \n\
		\"floorIconOutlines\": false, \n\
		\"stickToFloors\": true, \n\
		\"planetEase\": \"Linear\", \n\
		\"planetEaseParts\": 1, \n\
		\"planetEasePartBehavior\": \"Mirror\", \n\
		\"defaultTextColor\": \"ffffff\", \n\
		\"defaultTextShadowColor\": \"00000050\", \n\
		\"congratsText\": \"\", \n\
		\"perfectText\": \"\",\n\
		\"legacyFlash\": false ,\n\
		\"legacyCamRelativeTo\": false ,\n\
		\"legacySpriteTiles\": false \n\
	},\n\
	\"actions\":\n\
	["
    for i in range(len(extraround)):
        if extraround[i]!=0:
            tmpstr+="\n		{ \"floor\": "+f"{i+1}"+", \"eventType\": \"Pause\", \"duration\": "+f"{extraround[i]}"+", \"countdownTicks\": 0, \"angleCorrectionDir\": -1 },"
    tmpstr+="\n\
	],\n\
	\"decorations\":\n\
	[\n\
	]\n\
}"
    with open(f"{path}_{exdescription}.adofai","wt",1,"utf-8") as file:
        file.write(tmpstr)
        print(f"谱面文件已保存至{path}_{exdescription}.adofai")

print(f"apofai音乐盒{VER}\n\
作者：@bilibili自己想柠檬\n\
关注柠檬喵~关注柠檬谢谢喵~\n\
--------------------------------------------------\n\
本程序会将分轨MIDI文件的不同轨道分别输出到不同的adofai文件。\n\
若有需求或能力，请自行选择前期合并单轨或后期合成音频，或者催更新功能（\n\
（注：由于本程序生成谱面物量动辄上万，暂时建议搭配adopac食用）\n\
--------------------------------------------------")
path=input("请输入MIDI文件路径>")
if path[0] == "'" or path[0] == "\"":
    path=path[1:-1]
if not pth.isfile(path):
    path=None
    while path==None:
        path=input("不是一个有效的路径，请重试>")
        if path[0] == "'" or path[0] == "\"":
            path=path[1:-1]
        if not pth.isfile(path):
            path=None
mid = MidiFile(path)



tempo=None
for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    total=len(track)
    timebound=0
    timenow=0
    pathiters=[]
    tile=[]
    for j, msg in enumerate(track):
        zerovelocity=False
        if msg.time!=0:
            if tempo==None:
                print("Err:定义bpm前出现不为0的时间")
                time.sleep(3)
                raise SyntaxError
            timebound+=msg.time/mid.ticks_per_beat*tempo*1e-6
        if msg.type=="note_on":
            if msg.velocity>0:
                for k, pathiter in enumerate(pathiters):
                    if pathiter.note==msg.note:
                        pathiters.pop(k)
                pathiters.append(pathiterator(msg.note, timebound))
            else:
                zerovelocity=True
        if len(pathiters)!=0:
            while timenow<timebound:
                minoffset=1e132
                index=0
                for k, pathiter in enumerate(pathiters):
                    if pathiter.next<minoffset:
                        minoffset=pathiter.next
                        index=k
                tile.append(timenow)
                if timenow>=minoffset:
                    timenow+=1e-12
                else:
                  timenow=minoffset
                pathiters[index].iteratenext()
        if msg.type=="note_off" or zerovelocity:
            has=False
            for k, pathiter in enumerate(pathiters):
                if pathiter.note==msg.note:
                    pathiters.pop(k)
                    has=True
                    break
            if not has:
                pass
        if msg.type=="set_tempo" and tempo==None:
            tempo=msg.tempo
        print_progress(j+1, total, done=f" Track {i} 读取完毕，正在生成谱面文件")
    if len(tile)>0:
        make(np.array(tile),path,f"Track {i}")
    else:
        print("该音轨无内容")
print("所有音轨处理完毕。10秒后退出。")
time.sleep(10)
sys.exit()