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
from geocoding import extract_gu_and_dong, get_gu_dong_codes

"""단가 계산 함수"""
def calc_price_per_m2(thing_amt_million_won, arch_area_m2):
    if arch_area_m2 and arch_area_m2 != 0:
        price_per_m2 = (thing_amt_million_won * 10000) / arch_area_m2
        return round(price_per_m2, 2)
    else:
        return None
    

"""데이터 필터링 및 계산"""
def process_data(df):
    processed_list = []
    for _, item in df.iterrows():
        row = {
            "gu_code": item.get("CGG_CD"),
            "gu_name": item.get("CGG_NM"),
            "bu_code": item.get("STDG_CD"),
            "bu_name": item.get("STDG_NM"),
            "jibun_address": item.get("LOTNO_SE"),
            "building_name": item.get("BLDG_NM"),
            "물건금액(만원)": item.get("THING_AMT"),
            "건물면적(m^2)": item.get("ARCH_AREA"),
        }
        row["1m2당물건금액(원)"] = calc_price_per_m2(
            row["물건금액(만원)"],
            row["건물면적(m^2)"]
        )
        processed_list.append(row)
    return pd.DataFrame(processed_list)


"""파일 읽어오기"""
def real_estate_processed(file_path: str, output_path: str):
    df = pd.read_csv(file_path)
    processed_df = process_data(df)

    # 자치구별 1m^2당 평균 물건금액 계산
    gu_avg_price = processed_df.groupby("gu_name")["1m2당물건금액(원)"].mean().sort_values(ascending=False)
    print("\n[자치구별 1m^2당 평균 물건금액 (원)]\n", gu_avg_price)

    processed_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    gu_avg_price.to_csv("../../data/processed/real_estate_gu_avg__processed.csv", encoding="utf-8-sig")

    return gu_avg_price


# 절대 경로 설정 및 실행
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'real_estate__raw.csv'))
print("절대경로로 확인:", file_path)

real_estate_processed(
    file_path,
    "../../data/processed/real_estate__processed.csv"
)
