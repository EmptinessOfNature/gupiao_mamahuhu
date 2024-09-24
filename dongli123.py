from longport_utils import Longport_agent
import numpy as np
import ta

def calc_cci_jibie(data,jibie,period):
    if jibie=='m5':
        data=data
    elif jibie=='m15':
        data=data[15]
    ret = ta.trend.cci(data['high'], data['low'], data['close'], window=period, constant=0.015)
    return ret

# zdtf是一个数组，存放的是不同级别，比如1h，4h，1d，2d，1w
# getfx是核心，通过getfx返回的值来确定颜色,结果存在tffx[i]=getfx(i,0);中
# xhdcci[tfxh]和dhdcci[tfxh]记录了所有级别的cci，通过tfxh来区分


def calc_dongli_123(data):
    zdtf = ['m5','m15','m30','h1','h4','d1']
    xhdcci = []
    dhdcci = []
    for i in range(6):
        xhdcci[i] = calc_cci_jibie(data,zdtf[i],55)
        dhdcci[i] = calc_cci_jibie(data,zdtf[i],144)

    def getfx(data,jibie_num,index):
        xcci = xhdcci[jibie_num]
        dcci = dhdcci[jibie_num]
        if index>=len(xcci):
            return -1
        if(xcci[index]>level and dcci[index]>level):
            return 0
        if(xcci[index]<-level and dcci[index]<-level):
            return 1

        pfx = -1
        nfx = -1
        b0 = 0
        for i in range(index+1,len(data)):
            




    level = 80
    data['fx'] = np.nan
    data['kys'] = np.nan
    data['cci1'] = ta.trend.cci(data['high'], data['low'], data['close'], window=55, constant=0.015)
    data['cci2'] = ta.trend.cci(data['high'], data['low'], data['close'], window=144, constant=0.015)
    for i in range(len(data)):
        if i>=2:
            lfx = data.loc[i-1,'fx']
            if (lfx==0 and data.loc[i-1,'cci1']<-level and data.loc[i-2,'cci1']>-level): #下穿-80
                if data.loc[i-1,'cci2']>-level:
                    lfx = np.nan
                else:
                    lfx=0
            if (lfx==1 and data.loc[i-1,'cci1']>level and data.loc[i-2,'cci1']<level): # 上穿80
                if data.loc[i-1,'cci2']<level:
                    lfx = np.nan
                else:
                    lfx=0
        if ((data.loc[i,'cci1']>level and data.loc[i,'cci2']>level) or (data.loc[i,'cci1']>-level and lfx==0)):
            data.loc[i,'kys']=0
            data.loc[i,'fx']=0

        if ((data.loc[i,'cci1']<-level and data.loc[i,'cci2']<-level) or (data.loc[i,'cci1']<level and lfx==1)):
            data.loc[i,'kys']=1
            data.loc[i,'fx']=1
    for i in range(len(data)):
        tffx[i] = getfx(i, 0)


if __name__=='__main__':
    agent = Longport_agent()
    data = agent.get_data_1D("TQQQ")
    data['CCI'] = ta.trend.cci(data['high'], data['low'], data['close'], window=14, constant=0.015)
    print(1)