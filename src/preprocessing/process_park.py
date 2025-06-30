import os
import sys
import pandas as pd
from tqdm import tqdm

# ✅ src 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.geocoding.vworld_geocode import coordinates_to_jibun_address
from src.geocoding.admin_mapper import extract_gu_and_dong, get_gu_dong_codes

# 경로 설정
INPUT_PATH = "data/raw/park__raw.csv"
OUTPUT_PATH = "data/processed/park__processed.csv"

# 사용할 컬럼 정의
usecols = [
    "P_IDX", "P_PARK", "P_ZONE", "P_ADDR", "P_ADMINTEL",
    "LONGITUDE", "LATITUDE"
]

# 데이터 불러오기
df = pd.read_csv(INPUT_PATH, usecols=usecols)
df = df.dropna(subset=["LONGITUDE", "LATITUDE"]).copy()

# 결과 컬럼 추가
df["jibun_address"] = None
df["gu_name"] = None
df["dong_name"] = None
df["gu_code"] = None
df["dong_code"] = None

# 주소 및 코드 매핑
for idx, row in tqdm(df.iterrows(), total=len(df)):
    lat = row["LATITUDE"]
    lon = row["LONGITUDE"]

    try:
        # ① 위경도 → 지번주소
        jibun_address = coordinates_to_jibun_address(lat, lon)
        if jibun_address is None:
            continue

        # ② 지번주소 → 자치구명, 행정동명
        gu_name, dong_name = extract_gu_and_dong(jibun_address)
        if gu_name is None or dong_name is None:
            continue

        # ③ 자치구명, 행정동명 → 코드
        gu_code, dong_code = get_gu_dong_codes(gu_name, dong_name)

        # ④ 결과 저장
        df.at[idx, "jibun_address"] = jibun_address
        df.at[idx, "gu_name"] = gu_name
        df.at[idx, "dong_name"] = dong_name
        df.at[idx, "gu_code"] = gu_code
        df.at[idx, "dong_code"] = dong_code

    except Exception as e:
        print(f"[{idx}] 예외 발생: {e}")
        continue

# 저장
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"✅ 공원 전처리 완료: {OUTPUT_PATH}")
