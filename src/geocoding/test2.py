"""
📌 버스정류장 데이터의 dong_name (법정동)을 기반으로
    행정동 코드(dong_code), 자치구 코드(gu_code), 자치구명(gu_name)을
    admin_mapper.get_gu_dong_codes() 함수로 재매핑하는 스크립트입니다.
"""

import pandas as pd
import os
import sys

# 📁 경로 설정
INPUT_PATH = "data/processed/bus_stop__processed.csv"
OUTPUT_PATH = "data/processed/bus_stop__processed_2.csv"

# 📌 sys.path에 src 경로 추가
sys.path.append(os.path.abspath("src"))

# ✅ 매핑 함수 import
from geocoding.admin_mapper import get_gu_dong_codes

# 📥 데이터 불러오기
df = pd.read_csv(INPUT_PATH, dtype=str)
df["dong_name"] = df["dong_name"].str.strip()
df["gu_name"] = df["gu_name"].str.strip()

# 🔍 매핑 함수 정의
def map_codes(row):
    gu = row["gu_name"]
    dong = row["dong_name"]
    gu_code, dong_code = get_gu_dong_codes(gu, dong)
    return pd.Series([gu_code, dong_code])

# 🧩 매핑 적용
df[["gu_code", "dong_code"]] = df.apply(map_codes, axis=1)

# 🧹 서울 외 지역 제거
before = len(df)
df = df[df["dong_code"].str.startswith("11", na=False)]
after = len(df)
print(f"🚫 서울 외 지역 제거됨: {before - after}건")

# ✅ 컬럼 순서 재정렬
first_cols = ["gu_code", "dong_code", "gu_name", "dong_name"]
df = df[first_cols + [col for col in df.columns if col not in first_cols]]

# 💾 저장
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"✅ 매핑 및 저장 완료: {OUTPUT_PATH} (총 {len(df)}행)")
