import pandas as pd
import numpy as np

# 创建示例 K 线数据
data = {
    'time': pd.date_range(start='2023-08-01', periods=10, freq='D').strftime('%Y-%m-%d'),
    'open': np.random.randint(100, 200, size=10),
    'high': np.random.randint(200, 300, size=10),
    'low': np.random.randint(50, 100, size=10),
    'close': np.random.randint(100, 200, size=10),
}

df = pd.DataFrame(data)

# 确保 'high' >= 'open' 和 'close'，'low' <= 'open' 和 'close'
df['high'] = df[['open', 'close']].max(axis=1) + np.random.randint(0, 50, size=10)
df['low'] = df[['open', 'close']].min(axis=1) - np.random.randint(0, 50, size=10)

def gen_html(df):
    # 创建 HTML 文件
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>K线图示例</title>
        <style>
            #chart {{
                position: relative;
                width: 100%;
                height: 500px;
            }}
        </style>
        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
                width: window.innerWidth,
                height: 500,
            }});
    
            const candlestickSeries = chart.addCandlestickSeries({{
                upColor: 'green',
                downColor: 'red',
                borderUpColor: 'green',
                borderDownColor: 'red',
                wickUpColor: 'green',
                wickDownColor: 'red',
            }});
    
            const data = {df.to_json(orient='records')};
            const formattedData = data.map(item => {{
                return {{
                    time: item.time,
                    open: item.open,
                    high: item.high,
                    low: item.low,
                    close: item.close,
                }};
            }});
    
            candlestickSeries.setData(formattedData);
        </script>
    </body>
    </html>
    """

    # 保存为 HTML 文件
    with open("candlestick_chart.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML 文件 'candlestick_chart.html' 已生成。")