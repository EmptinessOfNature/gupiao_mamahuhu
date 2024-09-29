from macd_utils import tdx_raw2_kline
import ta
def getfx(data,index):
    # 如果同时大于80，则返回向上
    if data.loc[index,'xcci']>80 and data.loc[index,'dcci']>80:
        return 0
    # 如果同时小于80,则返回向下
    if data.loc[index,'xcci']<-80 and data.loc[index,'dcci']<-80:
        return 1
    pfx=-1
    nfx=-1
    b0=0
    # 向后遍历,找是否有同时大于80的点
    for i in range(index+1,len(data)):
        if data.loc[i,'xcci']>80 and data.loc[i,'dcci']>80:
            pfx=0
            b0=i
            break
        elif data.loc[i,'xcci']<-80 and data.loc[i,'dcci']<-80:
            pfx=1
            b0=i
            break
    nfx = pfx
    # 如果后面有同时大于80的点(nfx=pfx=0),记录第一个点b0,往前遍历,如果存在xcci小于-80的,那么就返回中性(nfx=-1),否则返回nfx=0向上
    # 如果后面有同时小于-80的点(pfx=nfx=1),记录第一个点b0,往前遍历,如果存在xcci大于80的,那么就返回中性(nfx=-1),否则返回nfx=1向下
    for i in range(b0-1,0):
        if (pfx==0 and data.loc[i,'xcci']<-80) or (pfx==1 and data.loc[i,'xcci']>80):
            nfx=-1
            break
    return nfx


if __name__=='__main__':
    code = "TQQQ"
    data = tdx_raw2_kline("./data_tdx_raw/74#" + code + ".txt", period="5min")
    data['xcci'] = ta.trend.cci(data['high'], data['low'], data['close'], window=144, constant=0.015)
    data['dcci'] = ta.trend.cci(data['high'], data['low'], data['close'], window=55, constant=0.015)
    getfx(data,0)
    print(1)