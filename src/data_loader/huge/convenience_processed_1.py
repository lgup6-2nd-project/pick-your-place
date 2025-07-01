# # import pandas as pd
# # import os

# # # 📥 입력 & 출력 경로
# # INPUT_PATH = "서울시 휴게음식점 인허가 정보.csv"
# # OUTPUT_PATH = "convenience_filtered.csv"

# # # ❌ 제외할 업태 목록
# # exclude_types = ["전통찻집", "키즈카페", "철도역구내", "관광호텔", "유원지", "떡카페", "푸드트럭", "다방"]

# # # 📄 CSV 불러오기 (인코딩 주의)
# # df = pd.read_csv(INPUT_PATH, encoding_errors='ignore')

# # print(f"📋 전체 행 수: {len(df)}")

# # # 📌 필요한 컬럼만 선택 (있는 경우에만)
# # required_cols = ["사업장명", "지번주소", "업태구분명", "영업상태명"]
# # df = df[[col for col in required_cols if col in df.columns]].copy()

# # # 🧹 폐업 제거
# # df = df[df["영업상태명"]!= "폐업"]

# # # 🧹 제외할 업태 제거
# # df = df[~df["업태구분명"].isin(exclude_types)]

# # # 💾 저장
# # df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
# # print(f"✅ 필터링 후 저장 완료: {OUTPUT_PATH} ({len(df)}건)")

# ####

import os
import pandas as pd

# 📥 입력 파일 경로 설정
file_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'data', 'raw', '서울시 휴게음식점 인허가 정보.csv'))
print("절대경로로 확인:", file_path)

# ❌ 제외할 업태 목록
exclude_types = ["전통찻집", "키즈카페", "철도역구내", "관광호텔", "유원지", "떡카페", "푸드트럭", "다방"]

# 📄 파일 열기 (cp949 + 깨진 문자 대체)
with open(file_path, 'r', encoding='cp949', errors='replace') as f:
    df = pd.read_csv(f)

# ✅ 필요한 컬럼만 선택 (혹시 없으면 자동 필터링)
required_cols = ["사업장명", "지번주소", "업태구분명", "영업상태명"]
df = df[[col for col in required_cols if col in df.columns]].copy()

# ❌ 폐업 및 휴업 업소 제거
df = df[~df["영업상태명"].isin(["폐업", "휴업"])]

# ❌ 제외 업태 제거
df = df[~df["업태구분명"].isin(exclude_types)]

# 💾 결과 저장 경로 설정
output_path = "../../../data/raw/convenience_filtered.csv"
output_path_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), output_path))

# 📁 디렉토리 없으면 생성
os.makedirs(os.path.dirname(output_path_abs), exist_ok=True)

# 💾 저장 (Excel에서 한글 깨짐 방지용 UTF-8-SIG)
df.to_csv(output_path_abs, index=False, encoding="utf-8-sig")
print("✅ 저장 완료:", output_path_abs)
