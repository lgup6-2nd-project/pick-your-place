import pandas as pd

# 행정동 코드 엑셀 불러오기 (최초 1회)
DONG_CODE_PATH = 'data/reference/KIKcd_H.20250701.xlsx'
MIX_MAPPING_PATH = 'data/reference/KIKmix.20250701.xlsx'

dong_df = pd.read_excel(DONG_CODE_PATH, dtype=str)
mix_df = pd.read_excel(MIX_MAPPING_PATH, dtype=str)

def extract_gu_and_dong(address: str) -> tuple:
    """
    지번주소 문자열에서 자치구와 동명을 추출
    예: '서울특별시 종로구 종로6가 70-6' → ('종로구', '종로6가')
    """
    try:
        parts = address.strip().split()
        gu = next((p for p in parts if p.endswith('구')), None)
        dong = next((p for p in parts if p.endswith('동') or p.endswith('가')), None)
        return gu, dong
    except Exception as e:
        print(f"[주소 파싱 실패] {address} → {e}")
        return None, None


# 매핑 테이블 정리
mix_df = mix_df.rename(columns={
    "시군구명": "gu_name",
    "동리명": "legal_dong",
    "읍면동명": "admin_dong",
    "행정동코드": "admin_code"
}).dropna(subset=["gu_name", "legal_dong", "admin_dong", "admin_code"])

def get_gu_dong_codes(gu: str, dong: str) -> tuple:
    """
    자치구 + 법정동 기준으로 행정동 이름 → 코드 반환
    """
    try:
        # (1) 법정동 → 행정동명 매핑
        match = mix_df[(mix_df["gu_name"] == gu) & (mix_df["legal_dong"] == dong)]

        if match.empty:
            print(f"[법정→행정 매핑 실패] gu={gu}, dong={dong}")
            return None, None

        admin_dong = match.iloc[0]["admin_dong"]

        # (2) 행정동명 → 코드 조회
        code_row = dong_df[
            (dong_df["시군구명"] == gu) & (dong_df["읍면동명"] == admin_dong)
        ]

        if not code_row.empty:
            dong_code = code_row.iloc[0]["행정동코드"]
            gu_code = dong_code[:5]
            return gu_code, dong_code
        else:
            print(f"[행정동 코드 조회 실패] {gu} {admin_dong}")
            return None, None

    except Exception as e:
        print(f"[오류 발생] {e}")
        return None, None
    