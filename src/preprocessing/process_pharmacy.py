# 지번주소가 없는 데이터 많음..
# 도로명주소도 지맘대로

import pandas as pd
import os
import sys
from pyproj import Transformer
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from geocoding.vworld_geocode import road_address_to_coordinates, coordinates_to_jibun_address, road_to_jibun_address
from geocoding.admin_mapper import extract_gu_and_dong, get_gu_dong_codes

def load_pharmacy_csv(path: str = "data/raw/pharmacy__raw.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"파일이 존재하지 않습니다: {path}")
    
    df = pd.read_csv(path, encoding="utf-8-sig")
    print(f"[로드 완료] {path} - {len(df)}건")
    return df


def process_pharmacy_data(df: pd.DataFrame) -> pd.DataFrame:
    # 1) DTLSTATENM이 "영업중"인 데이터만 필터링
    df = df[df['DTLSTATENM'] == '영업중']

    # 2) 필요한 컬럼만 추출 & 영문 컬럼명 매핑
    needed_cols = [
        'MGTNO',
        'SITEWHLADDR',
        'RDNWHLADDR',
        'BPLCNM',
        'X',
        'Y'
    ]

    # 존재하는 컬럼만 필터링
    selected_cols = [col for col in needed_cols if col in df.columns]
    df = df[selected_cols]

    rename_map = {
        'MGTNO': 'pharmacy_code',
        'SITEWHLADDR': 'jibun_address',
        'RDNWHLADDR': 'road_address',
        'BPLCNM': 'pharmacy_name',
        'X': 'longitude',
        'Y': 'latitude'
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    print(f"[전처리 완료] {len(df)}건")
    return df

def clean_road_address(raw_address: str) -> str:
    if not isinstance(raw_address, str):
        return ""

    # 괄호 안 제거 (ex. (합정동))
    addr = re.sub(r"\([^)]*\)", "", raw_address)

    # 지하, 지상, 층수, 호수 등 제거
    addr = re.sub(r"(지하\s*\d*층?|B\d+층?)", "", addr)
    addr = re.sub(r"\d+층", "", addr)
    addr = re.sub(r"\d+호", "", addr)

    # 합정역, 강남역 등 ‘역’ 관련 제거 (필요에 따라 선택적으로 적용)
    addr = re.sub(r"\b\w*역\b", "", addr)

    # 콤마 제거 + 다중 공백 정리
    addr = addr.replace(",", " ")
    addr = re.sub(r"\s+", " ", addr)

    return addr.strip()

# TM좌표계(EPSG:5181) → 위경도(WGS84: EPSG:4326)
def tm_to_lonlat(x, y):
    try:
        transformer = Transformer.from_crs("epsg:5181", "epsg:4326", always_xy=True)
        lon, lat = transformer.transform(x, y)
        return lon, lat
    except Exception as e:
        print(f"[좌표 변환 실패] X={x}, Y={y}, 에러: {e}")
        return None, None

# TM 좌표를 위경도로 변환 (좌표 오류시 None 처리)
def convert_coords(df: pd.DataFrame, x_col='longitude', y_col='latitude'):
    def safe_convert(row):
        try:
            return tm_to_lonlat(row[x_col], row[y_col])
        except Exception as e:
            print(f"[⚠️ 변환 실패] X: {row.get(x_col)}, Y: {row.get(y_col)} → {e}")
            return (None, None)

    coords = df.apply(safe_convert, axis=1)
    df['lon'], df['lat'] = zip(*coords)
    return df

# 위도, 경도 → 지번 주소 (좌표 실패 시 도로명주소로 보완)
def safe_jibun_address(row):
    try:
        lon, lat = row.get('lon'), row.get('lat')
        # 1. 좌표 유효하면 좌표 → 지번주소 시도
        if lon is not None and lat is not None and not (pd.isna(lon) or pd.isna(lat)):
            addr = coordinates_to_jibun_address(lon, lat)
            if addr and "검색결과가 없습니다" not in addr:
                return addr

        # 2. 기존 지번주소가 있으면 그대로 사용
        raw_jibun = row.get('jibun_address', '')
        if isinstance(raw_jibun, str) and raw_jibun.strip():
            return raw_jibun.strip()
        
        # 3. 도로명주소 → 지번주소 보완 시도
        road = row.get('road_address', '')
        if isinstance(road, str) and road.strip():
            cleaned_address = clean_road_address(road)
            addr = road_to_jibun_address(cleaned_address)
        if addr and addr.strip():
            return addr

        # 4. 모두 실패
        print(f"[⚠️ 지번주소 실패] 약국: {row.get('pharmacy_name')}, 도로명: {road}")
        return None

    except Exception as e:
        print(f"[❌ 예외] 지번주소 변환 실패 - {e}")
        return None

# 지번 주소 → 자치구명, 행정동명
def safe_extract_gu_dong(addr):
    try:
        return pd.Series(extract_gu_and_dong(addr)) if addr else pd.Series([None, None])
    except Exception as e:
        print(f"[주소 파싱 실패] {addr} → {e}")
        return pd.Series([None, None])
    
# 자치구명, 행정동명 → 코드 매핑
def safe_get_codes(row):
    try:
        return pd.Series(get_gu_dong_codes(row['gu_name_from_jibun'], row['dong_name_from_jibun']))
    except Exception as e:
        print(f"[법정→행정 매핑 실패] gu={row['gu_name_from_jibun']}, dong={row['dong_name_from_jibun']}")
        return pd.Series([None, None])

def mapping_process(df):
    df = process_pharmacy_data(df)
    print("[DEBUG] 현재 컬럼명:", df.columns.tolist())

    # TM → 위경도 변환 적용
    df = convert_coords(df, x_col='longitude', y_col='latitude')

    # 위도, 경도 → 지번주소 변환 (좌표 실패 시 도로명주소로 보완)
    df['jibun_address'] = df.apply(safe_jibun_address, axis=1)

    # 지번주소 → 자치구명, 행정동명 추출
    df[['gu_name_from_jibun', 'dong_name_from_jibun']] = df['jibun_address'].apply(safe_extract_gu_dong)

    # 자치구명, 행정동명 → 코드 매핑
    df[['gu_code', 'dong_code']] = df.apply(safe_get_codes, axis=1)

    return df

# 실행
if __name__ == "__main__":
    print("[실행] 시장 데이터를 전처리하고 저장합니다...")
    df_raw = load_pharmacy_csv()
    df = mapping_process(df_raw)

    # 저장
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/pharmacy__processed.csv"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"저장 완료: {output_path}")

    # 전처리 실패한 행 따로 저장
    failures = df[df['dong_code'].isnull()]
    failures_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/pharmacy__failed.csv"))
    failures.to_csv(failures_path, index=False, encoding='utf-8-sig')
    print(f"⚠️ 매핑 실패 데이터 저장 완료: {failures_path}")