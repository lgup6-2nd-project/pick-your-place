import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from geocoding.vworld_geocode import road_address_to_coordinates, coordinates_to_jibun_address, road_to_jibun_address
from geocoding.admin_mapper import extract_gu_and_dong, get_gu_dong_codes

def load_market_csv(path: str = "data/raw/market__raw.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"파일이 존재하지 않습니다: {path}")
    
    df = pd.read_csv(path, encoding="utf-8-sig")
    print(f"[로드 완료] {path} - {len(df)}건")
    return df

# 데이터 전처리
def process_market_data(df: pd.DataFrame) -> pd.DataFrame:

    needed_cols = [
        '도로명주소',
        '시군구',
        '시도',
        '시장명',
        '시장코드',
        '지번주소'
    ]

    # 존재하는 컬럼만 필터링
    selected_cols = [col for col in needed_cols if col in df.columns]
    df = df[selected_cols]

    # 영문 컬럼명 매핑
    rename_map = {
        '도로명주소': 'road_address',
        '시군구': 'gu_name',
        '시도': 'si_do',
        '시장명': 'market_name',
        '시장코드': 'market_code',
        '지번주소': 'jibun_address'
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df = df[df['si_do'] == '서울특별시']

    print(f"[전처리 완료] {len(df)}건")
    return df


def mapping_process(df):
    df = process_market_data(df)

    # 지번 주소 → 자치구명, 행정동명
    df[['gu_name_from_jibun', 'dong_name_from_jibun']] = df['jibun_address'].apply(
        lambda addr: pd.Series(extract_gu_and_dong(addr))
    )

    # 자치구명, 행정동명 → 자치구코드, 행정동코드
    df[['gu_code', 'dong_code']] = df.apply(
        lambda r: pd.Series(get_gu_dong_codes(r['gu_name_from_jibun'], r['dong_name_from_jibun'])), axis=1
    )

    return df

# 실행
if __name__ == "__main__":
    print("[실행] 시장 데이터를 전처리하고 저장합니다...")
    df_raw = load_market_csv()
    df = mapping_process(df_raw)

    # 저장
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/market__processed.csv"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"저장 완료: {output_path}")

    # 전처리 실패한 행 따로 저장
    failures = df[df['dong_code'].isnull()]
    failures_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/market__failed.csv"))
    failures.to_csv(failures_path, index=False, encoding='utf-8-sig')
    print(f"⚠️ 매핑 실패 데이터 저장 완료: {failures_path}")