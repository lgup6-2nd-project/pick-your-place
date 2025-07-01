import re
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
        # (0) 이미 행정동이면 바로 코드 조회
        direct = dong_df[
            (dong_df["시군구명"] == gu) & (dong_df["읍면동명"] == dong)
        ]
        if not direct.empty:
            dong_code = direct.iloc[0]["행정동코드"]
            gu_code = dong_code[:5]
            return gu_code, dong_code
        
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
    

def smart_parse_gu_and_dong(address: str):
    """
    주소 문자열에서 자치구, 법정동명을 추출
    - 괄호 안에 동/가 있으면 사용
    - 없으면 전체 주소에서 추출
    - 숫자/번지 제거 포함
    """
    try:
        # ① 자치구 추출
        gu_match = re.search(r"서울특별시\s+(\S+?구)", address)
        gu = gu_match.group(1) if gu_match else None

        dong = None

        # ② 괄호 안에서 동/가로 끝나는 단어 추출
        bracket_match = re.search(r"\(([^)]+)\)", address)
        if bracket_match:
            candidate = bracket_match.group(1)
            # 괄호 안에서 동/가로 끝나는 단어만 허용
            if re.search(r"(동|가)$", candidate):
                dong = candidate.strip()

        # ③ fallback: 괄호 안 실패 시 전체 주소에서 추출
        if not dong:
            # 괄호 제외한 주소에서 동명 찾기
            address_cleaned = re.sub(r"\(.*?\)", "", address)
            after_gu = address_cleaned.split(gu)[-1] if gu else address_cleaned
            tokens = after_gu.strip().split()
            for token in tokens:
                token_clean = re.sub(r"[0-9\-]+.*", "", token)  # 번지 제거
                if token_clean.endswith("동") or token_clean.endswith("가"):
                    dong = token_clean.strip()
                    break

        # ④ 결과 반환
        if gu and dong:
            return gu, dong
        else:
            print(f"[동명 추출 실패] {address}")
            return None, None

    except Exception as e:
        print(f"[파싱 예외] {address} → {e}")
        return None, None

# 자치구 코드 매핑 파일 경로
GU_CODE_PATH = "data/reference/gu_code.csv"
# 자치구 코드 매핑 로드
gu_code_df = pd.read_csv(GU_CODE_PATH, dtype=str, encoding='cp949')

def get_gu_code(gu_name: str) -> str:
    """
    자치구 이름을 자치구 코드로 변환
    예: '강남구' → '111261'
    """
    try:
        match = gu_code_df[gu_code_df["측정소명"] == gu_name]
        if not match.empty:
            return match.iloc[0]["측정소코드"]
        else:
            print(f"[자치구 코드 매핑 실패] gu_name={gu_name}")
            return None
    except Exception as e:
        print(f"[오류 발생] {gu_name} → {e}")
        return None
