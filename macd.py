import pandas as pd

from macd_utils import tdx_raw2_kline, double_macd, jw, duanxian, draw_line

# from lightweight_charts import Chart
from gen_page import gen_html


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


def is_v(data, col, pre_len, post_len, direction):
    # is_v计算周期至少是三个点，所以如果输入pre和post都是1，那么也会计算最近三个点。
    def _is_v_bottom(row, col, pre_len, post_len, direction):
        index = row.name
        if index < pre_len + post_len:
            return False
        values_pre = data[col].iloc[index - pre_len - post_len : index - post_len + 1]
        values_post = data[col].iloc[index - post_len : index + 1]
        if direction == "bottom":
            ret = bool(
                ((values_pre.diff()[-pre_len:] < 0).all())
                & ((values_post.diff()[-post_len:] > 0).all())
            )
        elif direction == "top":
            ret = bool(
                ((values_pre.diff()[-pre_len:] > 0).all())
                & ((values_post.diff()[-post_len:] < 0).all())
            )
        else:
            raise ValueError("is_v函数的direction错误")
        return ret

    ret = data.apply(
        _is_v_bottom,
        axis=1,
        col=col,
        pre_len=pre_len,
        post_len=post_len,
        direction="bottom",
    )
    return ret


def speed(data, col, length):
    ret = data[col].diff(periods=length) / length
    return ret


def condition_or(rules):
    # 多个条件取或
    merged = pd.concat(rules, axis=1, ignore_index=True)
    ret = merged.any(axis=1)
    return ret


def merge_signal(data):
    # 开多仓策略
    long_start_rules = []
    # long_start_rules.append(
    #     (data["m1"] > 0)
    #     & (data["m1"].abs() > 1)
    #     & (is_chuan(data, col="m2", pre_len=1, post_len=1, thresh=0, direction="up"))
    #     & (speed(data, col="m2", length=2) > 0.1)
    # )
    long_start_rules.append(
        (data["m1"] > 0)
        & (data["m1"].abs() > 1)
        & (data["m2"] < 0)
        & (is_v(data, col="m2", pre_len=3, post_len=2, direction="bottom"))
        & (data["m1"].abs() >= 1.1 * data["m2"].abs())
    )
    long_start = condition_or(long_start_rules)

    # 平多仓策略
    long_end_rules = []
    long_end_rules.append(
        (is_chuan(data, col="m2", pre_len=1, post_len=1, thresh=0, direction="down"))
    )
    long_end_rules.append(
        (is_v(data, col="m2", pre_len=3, post_len=2, direction="top"))
    )
    long_end_rules.append(speed(data, col="m2", length=2).abs() < 0.01)
    long_end = condition_or(long_end_rules)

    # 开空仓策略
    short_start_rules = []
    # short_start_rules.append(
    #     (data["m1"] < 0)
    #     & (data["m1"].abs() > 1)
    #     & (is_chuan(data, col="m2", pre_len=1, post_len=1, thresh=0, direction="down"))
    #     & (speed(data, col="m2", length=2) > 0.1)
    # )
    short_start_rules.append(
        (data["m1"] < 0)
        & (data["m1"].abs() > 1)
        & (data["m2"] > 0)
        & (is_v(data, col="m2", pre_len=3, post_len=2, direction="top"))
        & (data["m1"].abs() >= 1.1 * data["m2"].abs())
    )
    short_start = condition_or(short_start_rules)

    # 平空仓策略
    short_end_rules = []
    short_end_rules.append(
        (is_chuan(data, col="m2", pre_len=1, post_len=1, thresh=0, direction="up"))
    )
    short_end_rules.append(
        (is_v(data, col="m2", pre_len=3, post_len=2, direction="bottom"))
    )
    short_end_rules.append(speed(data, col="m2", length=2).abs() < 0.01)
    short_end = condition_or(short_end_rules)

    data["long_start"], data["long_end"], data["short_start"], data["short_end"] = (
        long_start,
        long_end,
        short_start,
        short_end,
    )

    return data


def huice(data):
    (
        data["long_buy"],
        data["long_sell"],
        data["short_buy"],
        data["short_sell"],
        data["profit_rate"],
    ) = (0, 0, 0, 0, 0)
    long_start_indexs = data[data["long_start"] > 0].index
    for index in long_start_indexs:
        find_area = data.iloc[index + 1 :]
        first_end = (
            find_area[find_area["long_end"] == 1].index[0]
            if len(find_area[find_area["long_end"] == 1]) > 0
            else data.index[-1]
        )
        data.loc[index, "long_buy"] = 1
        data.loc[first_end, "long_sell"] = 1
        data.loc[index, "profit_rate"] = (
            data.loc[first_end, "close"] / data.loc[index, "close"] - 1
        )

    short_start_indexs = data[data["short_start"] > 0].index
    for index in short_start_indexs:
        find_area = data.iloc[index + 1 :]
        first_end = find_area[find_area["short_end"] == 1].index[0]
        data.loc[index, "short_buy"] = 1
        data.loc[first_end, "short_sell"] = 1
        data.loc[index, "profit_rate"] = (
            data.loc[index, "close"] - data.loc[first_end, "close"]
        ) / data.loc[index, "close"]
    return data


if __name__ == "__main__":
    code = "TQQQ"
    data = tdx_raw2_kline("./data_tdx_raw/74#" + code + ".txt", period="390min")
    data = double_macd(data)
    data = jw(data)
    data = duanxian(data)
    data = merge_signal(data)
    data = huice(data)
    # data.to_csv('./data_huice/'+code+'.csv')
    draw_line(data, code=code, comment=str(data["profit_rate"].sum()))

    print(1)
    print(data['profit_rate'].sum())
    # data_plot = data[['dt','open','high','low','close','vol','m1']]
    # data_plot.columns=['time','open','high','low','close','volume','m1']
    # data_plot['time'] = data_plot.time.dt.strftime('%Y-%m-%dT%H:%M')
    # chart = Chart(inner_width=1, inner_height=0.7)
    # chart.time_scale(visible=True)
    # chart2 = chart.create_subchart(position='bottom', width=1, height=0.3,sync=True)
    # line = chart2.create_line(name='m1',color='blue')
    # line.set(data_plot)
    # hline = chart2.horizontal_line(0)
    # chart.legend(visible=True, font_size=14)
    # chart2.legend(visible=True, font_size=14)
    # chart2.grid()

    # Columns: time | open | high | low | close | volume

    # chart.set(data_plot)
    # chart.crosshair(mode='normal', vert_color='#FFFFFF', vert_style='dotted',
    #                 horz_color='#FFFFFF', horz_style='dotted')
    # gen_html(data_plot)

    # chart.show(block=True)
