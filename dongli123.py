from longport_utils import Longport_agent
import numpy as np

def calc_dongli_123(data):
    data['fx'] = np.nan
    data['kys'] = np.nan
    for i in range(len(data)):
        if i>=2:
            lfx = data.loc[i-1,'fx']
            if (lfx==0 and )



if __name__=='__main__':
    agent = Longport_agent()
    data = agent.get_data_1D("TQQQ")
    calc_dongli_123(data)