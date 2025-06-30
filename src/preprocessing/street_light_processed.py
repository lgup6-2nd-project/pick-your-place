import os
import sys
import math
import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# 경로 설정 및 모듈 import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from geocoding import reverse_geocode
from geocoding import road_address_to_coordinates, coordinates_to_jibun_address, coordinates_to_road_address
from geocoding import extract_gu_and_dong, get_gu_dong_codes

def street_light_processed(file_path: str, output_path: str):
    df = pd.read_csv(file_path)

    gu_list = []
    road_list = []
    dong_list = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        lat, lon = row[0], row[1]
        print("위도, 경도: ", lat, lon)
        try:
            road = reverse_geocode(lon, lat)
            gu, dong = extract_gu_and_dong(road)
            road_list.append(road)
            gu_list.append(gu)
            dong_list.append(dong)
        except Exception as e:
            print(f"Error processing {lon}, {lat}: {e}")
            print("도로명: ", road)
            print("행정동: ", gu, dong)
            road_list.append(None)
            gu_list.append(None)
            dong_list.append(None)

    df['road_address'] = road_list
    df['gu_name'] = gu_list
    df['dong_name'] = dong_list

    gu_counts = df['gu_name'].value_counts()
    print("\n자치구별 가로등 개수:\n", gu_counts)

    output_path_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'street_light__processed.csv'))
    gu_counts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'street_ight_gu_counts.csv'))
    
    # # 코드 돌리고 주석 처리할 것 
    # # 경로 디렉토리 없으면 생성
    # os.makedirs(os.path.dirname(output_path_abs), exist_ok=True)
    # os.makedirs(os.path.dirname(gu_counts_path), exist_ok=True)
    
    gu_counts.to_csv(gu_counts_path, encoding="utf-8-sig")
    df.to_csv(output_path_abs, index=False, encoding="utf-8-sig")

    return gu_counts

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'street_light__raw.csv'))
# print("절대경로로 확인:", file_path)

street_light_processed(
    file_path,                                          # raw 데이터
    "../../data/processed/street_light__processed.csv"  # processed 데이터
)
