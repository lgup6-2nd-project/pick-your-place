import os
import pandas as pd

# 입력 폴더와 출력 폴더
INPUT_DIR = "output_by_uptae"
OUTPUT_DIR = "data/processed_counts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 모든 CSV 파일 처리
for file_name in os.listdir(INPUT_DIR):
    if file_name.endswith(".csv"):
        input_path = os.path.join(INPUT_DIR, file_name)
        output_path = os.path.join(OUTPUT_DIR, f"counts_{file_name}")

        # CSV 읽기
        df = pd.read_csv(input_path, encoding="utf-8-sig")

        # 코드 정수형 처리
        df["gu_code"] = pd.to_numeric(df["gu_code"], errors="coerce").astype("Int64")
        df["dong_code"] = pd.to_numeric(df["dong_code"], errors="coerce").astype("Int64")

        # 행정동 기준 개수 집계
        count_df = (
            df.groupby(["gu_code", "dong_code", "gu_name", "dong_name"])
            .size()
            .reset_index(name="counts")
        )

        # 저장
        count_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"[✅ 저장 완료] {output_path}")
