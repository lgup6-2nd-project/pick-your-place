import os
import sys
import pandas as pd
from tqdm import tqdm
import re

# src 경로 등록
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 내부 함수 import
from src.geocoding.admin_mapper import (
    smart_parse_gu_and_dong,
    extract_gu_and_dong,
    get_gu_dong_codes,
)
from src.geocoding.vworld_geocode import coordinates_to_jibun_address

# 경로 설정
INPUT_PATH = "data/raw/park__raw.csv"
OUTPUT_PATH = "data/processed/park__processed.csv"

usecols = ["P_IDX", "P_PARK", "P_ZONE", "P_ADDR", "LATITUDE", "LONGITUDE"]
df = pd.read_csv(INPUT_PATH, usecols=usecols).dropna(subset=["P_ADDR"]).copy()

df["gu_name"] = None
df["dong_name"] = None
df["gu_code"] = None
df["dong_code"] = None

for idx, row in tqdm(df.iterrows(), total=len(df)):
    addr = row["P_ADDR"]
    lat = row["LATITUDE"]
    lon = row["LONGITUDE"]

    # ① 주소에서 동명 추출 시도
    gu, dong = smart_parse_gu_and_dong(addr)

    # ② 실패 시: 위경도 → 지번주소 → 동 추출
    if not gu or not dong:
        try:
            jibun_addr = coordinates_to_jibun_address(lat, lon)
            gu, dong = extract_gu_and_dong(jibun_addr)
        except Exception as e:
            print(f"[좌표 fallback 실패] idx={idx}, lat={lat}, lon={lon} → {e}")
            continue

    # ③ gu, dong으로 코드 매핑
    if gu and dong:
        gu_code, dong_code = get_gu_dong_codes(gu, dong)
        df.at[idx, "gu_name"] = gu
        df.at[idx, "dong_name"] = dong
        df.at[idx, "gu_code"] = gu_code
        df.at[idx, "dong_code"] = dong_code
    else:
        print(f"[동명 최종 실패] {addr}")

# 저장
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"✅ 공원 전처리 최종 완료 (with 좌표 fallback): {OUTPUT_PATH}")
