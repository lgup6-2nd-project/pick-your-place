import pandas as pd
import os

# 파일 경로
INPUT_PATH = "CONVE_with_admin_dong.csv"
OUTPUT_DIR = "output_by_uptae"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CSV 불러오기
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

# 업종별로 분리 저장
for uptae, group in df.groupby("SNTUPTAENM"):
    if pd.isna(uptae):
        continue  # 업종명이 없는 경우 제외
    safe_name = str(uptae).replace("/", "_").replace(" ", "_").replace("(", "").replace(")", "")
    output_path = os.path.join(OUTPUT_DIR, f"convenience_{safe_name}.csv")
    group.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 저장 완료: {output_path} ({len(group)}건)")
