from longport_utils import Longport_agent
import numpy as np
import ta

def icci(data,i):
    return 1

def calc_dongli_123(data):
    level = 80
    data['fx'] = np.nan
    data['kys'] = np.nan
    data['cci1'] = ta.trend.cci(data['high'], data['low'], data['close'], window=55, constant=0.015)
    data['cci2'] = ta.trend.cci(data['high'], data['low'], data['close'], window=144, constant=0.015)
    for i in range(len(data)):
        if i>=2:
            lfx = data.loc[i-1,'fx']
            if (lfx==0 and data.loc[i-1,'cci1']<-level and data.loc[i-2,'cci1']>-80): #下穿80
                if data.loc[i-1,'cci2'>-level]:
                    lfx = np.nan
                else:
                    lfx=0
            if (lfx)


if __name__=='__main__':
    agent = Longport_agent()
    data = agent.get_data_1D("TQQQ")
    data['CCI'] = ta.trend.cci(data['high'], data['low'], data['close'], window=14, constant=0.015)
    print(1)