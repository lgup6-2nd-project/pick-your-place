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

# file_path = "../../data/raw/안전비상벨위치정보.xlsx" # row 데이터
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', '안전비상벨위치정보.xlsx'))
print("🔍 절대경로로 확인:", file_path)

df = pd.read_excel(file_path)
df = df[["소재지도로명주소", "소재지지번주소", "WGS84위도", "WGS84경도"]]

results = []

for _, row in tqdm(df.iterrows(), total=len(df)):
    road_address = row["소재지도로명주소"]
    jibun_addres = row["소재지지번주소"]
    lat = row["WGS84위도"]
    lon = row["WGS84경도"]
    
    try:
        # lon, lat = road_address_to_coordinates(road_address)
        kakao_jibun = reverse_geocode(lon, lat)
        road = coordinates_to_road_address(lon, lat)
        jibun = coordinates_to_jibun_address(lon, lat)
        gu, dong = extract_gu_and_dong(jibun)
        gu_code, dong_code = get_gu_dong_codes(gu, dong)
        
        results.append({
            "위도": lat,
            "경도": lon,
            "도로명주소": road,
            "지번주소": jibun,
            "자치구": gu,
            "행정동": dong,
            "자치구코드": gu_code,
            "행정동코드": dong_code
        })
    except Exception as e:
        print(f"Error processing address '{road_address}': {e}")

result_df = pd.DataFrame(results)
output_path = "../../data/processed/safety_bell_processed.xlsx"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
result_df.to_excel(output_path, index=False)

print("저장 완료", output_path)
