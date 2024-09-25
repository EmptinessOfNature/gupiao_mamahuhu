from macd_utils import tdx_raw2_kline
import ta
def getfx():
    pass

if __name__=='__main__':
    code = "TQQQ"
    data = tdx_raw2_kline("./data_tdx_raw/74#" + code + ".txt", period="5min")
    data['xcci'] = ta.trend.cci(data['high'], data['low'], data['close'], window=144, constant=0.015)
    data['dcci'] = ta.trend.cci(data['high'], data['low'], data['close'], window=55, constant=0.015)

    print(1)