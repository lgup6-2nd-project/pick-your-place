import requests
from dotenv import load_dotenv
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import math
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from geocoding import reverse_geocode
from geocoding import road_address_to_coordinates, coordinates_to_jibun_address, coordinates_to_road_address
from geocoding import extract_gu_and_dong, get_gu_dong_codes, get_gu_code

def calculate_percentages(file_path: str):
    df_all = pd.read_excel(file_path, header=None)

    total_row = df_all.iloc[4]
    raw_total = str(total_row.iloc[2]).replace(",", "")
    total_occurrence = pd.to_numeric(raw_total, errors='coerce')
    if pd.isna(total_occurrence):
        raise ValueError(f"Invalid total crime count: {total_row.iloc[2]}")

    df = df_all.iloc[5:].copy()

    df.columns = [
        "district_category", "district", "total_cases", "total_arrests",
        "murder_cases", "murder_arrests", "robbery_cases", "robbery_arrests",
        "sexual_cases", "sexual_arrests", "theft_cases", "theft_arrests",
        "violence_cases", "violence_arrests"
    ]

    df.drop(columns=[
        "district_category", "total_arrests",
        "murder_arrests", "robbery_arrests",
        "sexual_arrests", "theft_arrests", "violence_arrests"
    ], inplace=True)

    for col in ["total_cases", "murder_cases", "robbery_cases", "sexual_cases", "theft_cases", "violence_cases"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    crime_types = {
        "murder": "murder_cases",
        "robbery": "robbery_cases",
        "sexual": "sexual_cases",
        "theft": "theft_cases",
        "violence": "violence_cases"
    }

    for eng_name, case_col in crime_types.items():
        rate_col = f"{eng_name}_rate(%)"
        df[rate_col] = (df[case_col] / total_occurrence * 100).round(2)
    df["total_rate(%)"] = (df["total_cases"] / total_occurrence * 100).round(2)

    # 자치구 코드 컬럼 추가
    df["gu_code"] = df["district"].apply(get_gu_code)

    # gu_code를 맨 앞으로 이동
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index("gu_code")))  # gu_code 컬럼을 리스트 첫번째 위치로 이동
    df = df[cols]


    output_path_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'crime_rate__processed.csv'))
    df.to_csv(output_path_abs, index=False, encoding="utf-8-sig")
    print(f"[Saved] → {output_path_abs}")

# 실행
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', '5대범죄발생현황.xlsx'))
calculate_percentages(file_path)
