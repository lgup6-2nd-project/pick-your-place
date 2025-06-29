import os
import sys
import pandas as pd
from tqdm import tqdm

# ✅ src 경로 등록
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# ✅ 내부 모듈 import
from src.geocoding.admin_mapper import extract_gu_and_dong, get_gu_dong_codes

# 경로 설정
INPUT_PATH = "data/raw/park__raw.csv"
OUTPUT_PATH = "data/processed/park__processed.csv"

# 사용할 컬럼
usecols = ["P_IDX", "P_PARK", "P_ZONE", "P_ADDR", "P_ADMINTEL"]
df = pd.read_csv(INPUT_PATH, usecols=usecols)
df = df.dropna(subset=["P_ADDR"]).copy()

# 결과 컬럼 추가
df["gu_name"] = None
df["dong_name"] = None
df["gu_code"] = None
df["dong_code"] = None

# 주소 기반 추출
for idx, row in tqdm(df.iterrows(), total=len(df)):
    try:
        address = row["P_ADDR"]

        # ① 자치구명, 동명 추출
        gu_name, dong_name = extract_gu_and_dong(address)
        if gu_name is None or dong_name is None:
            continue

        # ② 코드 매핑
        gu_code, dong_code = get_gu_dong_codes(gu_name, dong_name)

        # ③ 저장
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
