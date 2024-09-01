import pandas as pd

from macd_utils import tdx_raw2_kline, double_macd, jw, duanxian


def is_chuan(data, col, pre_len, post_len, thresh, direction):
    def _is_chuan_up(row, col, pre_len, post_len, thresh):
        index = row.name
        if index < pre_len + post_len - 1:
            return False
        else:
            values_pre = data[col].iloc[
                index - pre_len - post_len + 1 : index - post_len + 1
            ]
            values_post = data[col].iloc[index - post_len + 1 : index + 1]
            ret = bool(((values_pre <= thresh).all()) & ((values_post > thresh).all()))
            return ret

    def _is_chuan_down(row, col, pre_len, post_len, thresh):
        index = row.name
        if index < pre_len + post_len - 1:
            return False
        else:
            values_pre = data[col].iloc[
                index - pre_len - post_len + 1 : index - post_len + 1
            ]
            values_post = data[col].iloc[index - post_len + 1 : index + 1]
            ret = bool(((values_pre >= thresh).all()) & ((values_post < thresh).all()))
            return ret

    if direction == "up":
        ret = data.apply(
            _is_chuan_up,
            axis=1,
            col=col,
            pre_len=pre_len,
            post_len=post_len,
            thresh=thresh,
        )
    elif direction == "down":
        ret = data.apply(
            _is_chuan_down,
            axis=1,
            col=col,
            pre_len=pre_len,
            post_len=post_len,
            thresh=thresh,
        )
    else:
        raise ValueError("direction错误")
    return ret

def is_v(data,col,pre_len,post_len,direction):
    # is_v计算周期至少是三个点，所以如果输入pre和post都是1，那么也会计算最近三个点。
    def _is_v_bottom(row,col,pre_len,post_len,direction):
        index = row.name
        if index < pre_len + post_len:
            return False
        values_pre = data[col].iloc[
                     index - pre_len - post_len : index - post_len+1
                     ]
        values_post = data[col].iloc[index - post_len: index + 1]
        if direction=='bottom':
            ret = bool(((values_pre.diff()[-pre_len:]<0).all()) & ((values_post.diff()[-post_len:]>0).all()))
        elif direction=='top':
            ret = bool(((values_pre.diff()[-pre_len:]>0).all()) & ((values_post.diff()[-post_len:]<0).all()))
        else:
            raise ValueError("is_v函数的direction错误")
        return ret

    ret = data.apply(_is_v_bottom,axis=1,col=col,pre_len=pre_len,post_len=post_len,direction='bottom')
    return ret


def speed(data, col, length):
    ret = data[col].diff(periods=length) / length
    return ret

def condition_or(rules):
    # 多个条件取或
    merged = pd.concat(rules,axis=1,ignore_index=True)
    ret = merged.any(axis=1)
    return ret


def merge_signal(data):
    # 开多仓策略
    long_start_rules = []
    long_start_rules.append(
        (data["m1"] > 0)
        & (data["m1"].abs() > 1)
        & (is_chuan(data, col="m2", pre_len=1, post_len=1, thresh=0, direction="up"))
        & (speed(data, col="m2", length=2) > 0.1)
    )
    long_start_rules.append(
        (data["m1"] > 0)
        & (data["m1"].abs() > 1)
        & (data['m2']<0)
        & (is_v(data,col='m2',pre_len=3,post_len=3,direction='bottom'))
        & (data['m1'].abs()>=2*data['m2'].abs())
    )
    long_start = condition_or(long_start_rules)

    # 平多仓策略
    long_end_rules = []
    long_end_rules.append((is_chuan(data,col='m2',pre_len=1,post_len=1,thresh=0,direction='down')))
    long_end_rules.append((is_v(data,col='m2',pre_len=3,post_len=3,direction='top')))
    long_end_rules.append(speed(data,col='m2',length=2).abs()<0.01)
    long_end = condition_or(long_end_rules)

    # # 做空开单条件
    #
    # short_rules.append(
    #     data.loc[i, "m1"] < 0
    #     and abs(data.loc[i, "m1"]) > 1
    #     and is_chuan(data, i, "m2", 1, 1, "down", 0)
    #     and speed_abs(data, i, "m2", 2) > 0.1
    # )
    # short_rules.append(
    #     data.loc[i, "m1"] < 0
    #     and abs(data.loc[i, "m1"]) > 1
    #     and data.loc[i, "m2"] > 0
    #     and is_v(data, i, "m2", 3, 3, "top")
    #     and abs(data.loc[i, 'm2']) > 0.5
    #     and abs(data.loc[i, "m1"]) >= 2 * abs(data.loc[i, "m2"])
    # )
    # # 做空止盈止损条件
    #
    # short_stop_rules.append(is_chuan(data, i, "m2", 1, 1, "up", 0))
    # short_stop_rules.append(is_v(data, i, "m2", 3, 3, "bottom"))
    # short_stop_rules.append(speed_abs(data, i, "m2", 2) < 0.01)
    #
    # 空仓开仓策略


    return data


if __name__ == "__main__":
    code = "TQQQ"
    data = tdx_raw2_kline("./data_tdx_raw/74#" + code + ".txt", period="390min")
    data = double_macd(data)
    data = jw(data)
    data = duanxian(data)
    data = merge_signal(data)
    print(1)
