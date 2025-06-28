import pandas as pd

# 행정동 코드 엑셀 불러오기 (최초 1회)
DONG_CODE_PATH = 'data/reference/KIKcd_H.20250701.xlsx'
dong_df = pd.read_excel(DONG_CODE_PATH, dtype=str)

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


def get_gu_dong_codes(gu: str, dong: str) -> tuple:
    """
    자치구명과 동명을 입력받아 행정동동코드와 법정동코드를 반환.
    '종로5.6가동' 같이 합쳐진 행정동명에 대해서도 동 이름 분해 후 매칭.

    Returns:
        (gu_code, dong_code) or (None, None)
    """
    try:
        candidates = dong_df[dong_df['시군구명'] == gu]

        for _, row in candidates.iterrows():
            raw_dong_name = row['읍면동명']

            if pd.isna(raw_dong_name):
                continue

            # 동 이름 분해 처리
            if '가동' in raw_dong_name:
                base = raw_dong_name.replace('가동', '')
                parts = base.split('.')  # ex: ['종로5', '6']
                # 종로 + 5 → 종로5가, 종로 + 6 → 종로6가
                split_dongs = [f"{''.join(filter(str.isalpha, base))}{p}가" for p in parts]
            else:
                split_dongs = [raw_dong_name]

            if dong in split_dongs:
                dong_code = row['행정동코드']
                gu_code = dong_code[:5]
                return gu_code, dong_code

        # 매칭 실패
        print(f"[코드 매핑 실패] gu={gu}, dong={dong}")
        print("🔍 해당 자치구 동목록:", candidates['읍면동명'].dropna().unique())
        return None, None

    except Exception as e:
        print(f"[오류 발생] {e}")
        return None, None
