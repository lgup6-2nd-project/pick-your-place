# 필요한 컬럼 : 도로명주소, 지번주소, 자치구명, 행정동명, 자치구코드, 행정동코드
# 현재 컬럼 : 메인 키, 기관 코드, 유형1, 대표 기관명, 전체 기관명, 최하위 기관명, 도로명 주소, 행정 시, 행정 구, 행정 동

import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader.center_csv import load_centers_data
from geocoding.vworld_geocode import road_address_to_coordinates, coordinates_to_jibun_address
from geocoding.admin_mapper import extract_gu_and_dong, get_gu_dong_codes

def rename_columns(df):
    # 필요한 컬럼만 남기기 (원본 컬럼명 기준)
    needed_cols = ['도로명 주소', '행정 구', '행정 동']
    df = df[needed_cols].copy()

    return df.rename(columns={
        '도로명 주소': 'road_address',
        '행정 구': 'gu_name',
        '행정 동': 'dong_name',
    })

def mapping_process(df):
    df = rename_columns(df)

    # 1) 도로명 주소 → (경도, 위도)
    coords = df['road_address'].apply(lambda addr: road_address_to_coordinates(addr))
    # 함수 반환 순서가 (경도, 위도)라면 아래와 같이 분리
    df['경도'], df['위도'] = zip(*coords)

    # 2) 위도, 경도 → 지번 주소
    df['jibun_address'] = df.apply(lambda r: coordinates_to_jibun_address(r['경도'], r['위도']), axis=1)

    # 3) 지번 주소 → 자치구명, 행정동명
    df[['gu_name_from_jibun', 'dong_name_from_jibun']] = df['jibun_address'].apply(
        lambda addr: pd.Series(extract_gu_and_dong(addr))
    )

    # 4) 자치구명, 행정동명 → 자치구코드, 행정동코드
    df[['gu_code', 'dong_code']] = df.apply(
        lambda r: pd.Series(get_gu_dong_codes(r['gu_name_from_jibun'], r['dong_name_from_jibun'])), axis=1
    )

    return df

if __name__ == "__main__":
    df = load_centers_data()  # 데이터 불러오기
    df = mapping_process(df)
    
    # 불필요한 컬럼 제거
    df.drop(columns=['위도', '경도'], inplace=True)

    # 저장
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/center__processed.csv"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"저장 완료: {output_path}")

    # 전처리 실패한 행 따로 저장
    failures = df[df['dong_code'].isnull()]
    failures_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/center__failed.csv"))
    failures.to_csv(failures_path, index=False, encoding='utf-8-sig')
    print(f"⚠️ 매핑 실패 데이터 저장 완료: {failures_path}")