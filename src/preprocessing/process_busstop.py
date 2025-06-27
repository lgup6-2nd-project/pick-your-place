# 📄 src/preprocessing/process_busstop.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_loader.busstop_api import fetch_bus_stop_data

import pandas as pd

def load_and_show_bus_stop_data():
    all_data = []

    # 총 11290개 → 1000개씩 반복 호출
    for start in range(1, 11291, 1000):
        end = min(start + 999, 11290)
        rows = fetch_bus_stop_data(start, end)
        all_data.extend(rows)

    # pandas DataFrame으로 변환
    df = pd.DataFrame(all_data)

    # 필요한 컬럼만 선택
    df = df[['STOPS_NO', 'STOPS_NM', 'XCRD', 'YCRD', 'NODE_ID', 'STOPS_TYPE']]
    df.columns = ['stop_no', 'stop_name', 'longitude', 'latitude', 'node_id', 'stop_type']

    # head 출력
    print(df.head())

    return df

# 직접 실행 시
if __name__ == "__main__":
    load_and_show_bus_stop_data()
