import os
import sys
import pandas as pd
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.geocoding.admin_mapper import extract_gu_and_dong, get_gu_dong_codes
# 파일 경로 설정
CONVE_PATH = 'src/data_loader/huge/convenience_filtered.csv'
DONG_CODE_PATH = 'data/reference/KIKcd_H.20250701.xlsx'
MIX_MAPPING_PATH = 'data/reference/KIKmix.20250701.xlsx'

# CSV 불러오기
df = pd.read_csv(CONVE_PATH)

# 행정동 코드 및 매핑 테이블 불러오기
dong_df = pd.read_excel(DONG_CODE_PATH, dtype=str)
mix_df = pd.read_excel(MIX_MAPPING_PATH, dtype=str)

# 매핑 테이블 컬럼 정리
mix_df = mix_df.rename(columns={
    "시군구명": "gu_name",
    "동리명": "legal_dong",
    "읍면동명": "admin_dong",
    "행정동코드": "admin_code"
}).dropna(subset=["gu_name", "legal_dong", "admin_dong", "admin_code"])

# 행정동 추출 함수
def smart_parse_gu_and_dong(address: str):
    try:
        gu_match = re.search(r"서울특별시\s+(\S+?구)", address)
        gu = gu_match.group(1) if gu_match else None

        dong = None
        bracket_match = re.search(r"\(([^)]+)\)", address)
        if bracket_match:
            candidate = bracket_match.group(1)
            if re.search(r"(동|가)$", candidate):
                dong = candidate.strip()

        if not dong:
            address_cleaned = re.sub(r"\(.*?\)", "", address)
            after_gu = address_cleaned.split(gu)[-1] if gu else address_cleaned
            tokens = after_gu.strip().split()
            for token in tokens:
                token_clean = re.sub(r"[0-9\-]+.*", "", token)
                if token_clean.endswith("동") or token_clean.endswith("가"):
                    dong = token_clean.strip()
                    break

        if gu and dong:
            return gu, dong
        else:
            return None, None

    except Exception:
        return None, None

# 코드 매핑 함수
# def get_gu_dong_codes(gu: str, dong: str):
#     try:
#         direct = dong_df[
#             (dong_df["시군구명"] == gu) & (dong_df["읍면동명"] == dong)
#         ]
#         if not direct.empty:
#             dong_code = direct.iloc[0]["행정동코드"]
#             gu_code = dong_code[:5]
#             return gu_code, dong_code

#         match = mix_df[(mix_df["gu_name"] == gu) & (mix_df["legal_dong"] == dong)]
#         if match.empty:
#             return None, None

#         admin_dong = match.iloc[0]["admin_dong"]
#         code_row = dong_df[
#             (dong_df["시군구명"] == gu) & (dong_df["읍면동명"] == admin_dong)
#         ]
#         if not code_row.empty:
#             dong_code = code_row.iloc[0]["행정동코드"]
#             gu_code = dong_code[:5]
#             return gu_code, dong_code
#         else:
#             return None, None

#     except Exception:
#         return None, None

# 매핑 적용
def enrich_gu_dong_info(row):
    address = row['지번주소']
    gu, dong = extract_gu_and_dong(address)
    if gu and dong:
        gu_code, dong_code = get_gu_dong_codes(gu, dong)
        return pd.Series([gu, dong, gu_code, dong_code])
    else:
        return pd.Series([None, None, None, None])

# 새 컬럼 추가
df[['gu_name', 'dong_name', 'gu_code', 'dong_code']] = df.apply(enrich_gu_dong_info, axis=1)

# 저장 (선택)
df.to_csv("CONVE_with_admin_dong.csv", index=False, encoding="utf-8-sig")
