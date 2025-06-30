# 필요한 컬럼 : MGTNO, SITEWHLADDR', 'RDNWHLADDR', 'BPLCNM', 'X', 'Y'

import pandas as pd
import os
import sys
from pyproj import Transformer
import re
from difflib import get_close_matches

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from geocoding.vworld_geocode import road_address_to_coordinates, coordinates_to_jibun_address, road_to_jibun_address
from geocoding.admin_mapper import extract_gu_and_dong, get_gu_dong_codes

def load_store_csv(path: str = "data/raw/store__raw.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"파일이 존재하지 않습니다: {path}")
    
    df = pd.read_csv(path, encoding="utf-8-sig")
    print(f"[로드 완료] {path} - {len(df)}건")
    return df

def process_store_data(df: pd.DataFrame) -> pd.DataFrame:
    # 1) DTLSTATENM이 "영업중"인 데이터만 필터링
    df = df[df['DTLSTATENM'] == '정상영업']

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
        'MGTNO': 'store_code',
        'SITEWHLADDR': 'jibun_address',
        'RDNWHLADDR': 'road_address',
        'BPLCNM': 'store_name',
        'X': 'longitude',
        'Y': 'latitude'
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # 지번주소, X, Y 값이 모두 비어있으면 None으로 처리 (아예 제거하지 않고)
    df['jibun_address'] = df['jibun_address'].replace('', pd.NA)
    df['longitude'] = df['longitude'].replace('', pd.NA)
    df['latitude'] = df['latitude'].replace('', pd.NA)

    # 만약 X, Y 둘 중 하나라도 없으면 좌표도 NaN 처리
    df.loc[df['longitude'].isna() | df['latitude'].isna(), ['longitude', 'latitude']] = pd.NA

    print(f"[INFO] 총 데이터 수: {len(df)}")
    print(f"[INFO] 지번주소 없는 데이터 수: {df['jibun_address'].isna().sum()}")
    print(f"[INFO] 좌표 없는 데이터 수: {df['longitude'].isna().sum()}")

    return df

def normalize_dong_name(name: str, standard_names: list) -> str:
    if not isinstance(name, str):
        return name

    # 예: '불광1동' → '불광제1동'
    normalized = re.sub(r'(\D)(\d)동$', r'\1제\2동', name)

    # 불필요 문자 제거
    simplified = normalized.replace("제", "").replace("·", "")

    # 부분 일치 후보 추출
    candidates = [
        std_name for std_name in standard_names
        if simplified in std_name.replace("제", "").replace("·", "")
    ]

    if len(candidates) == 1:
        return candidates[0]  # 유일한 매칭이면 반환
    elif len(candidates) > 1:
        print(f"[다대일 매핑 경고] '{name}' → 후보: {candidates}")
        return None  # 다중 매칭 → 수동 확인 필요
    else:
        return normalized  # 매칭 없음 → 기본 정규화된 값 반환

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
        # 1. 기존 지번주소가 있으면 그대로 사용
        raw_jibun = row.get('jibun_address', '')
        if isinstance(raw_jibun, str) and raw_jibun.strip():
            return raw_jibun.strip()
        
        # 2. 도로명주소가 있으면 → 좌표 변환 → 지번주소 변환 시도
        road = row.get('road_address', '')
        if isinstance(road, str) and road.strip():
            lon, lat = road_address_to_coordinates(road)
            if lon is not None and lat is not None:
                addr = coordinates_to_jibun_address(lon, lat)
                if addr and '검색결과가 없습니다' not in addr:
                    return addr
        
        # 3. TM 좌표(lon, lat)로 → 지번주소 변환 시도
        lon, lat = row.get('lon'), row.get('lat')
        if lon is not None and lat is not None and not (pd.isna(lon) or pd.isna(lat)):
            addr = coordinates_to_jibun_address(lon, lat)
            if addr and '검색결과가 없습니다' not in addr:
                return addr

        # 4. 모두 실패
        print(f"[⚠️ 지번주소 실패] 스토어: {row.get('store_name')}, 도로명: {road}")
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
    df = process_store_data(df)
    print("[DEBUG] 현재 컬럼명:", df.columns.tolist())

    # TM → 위경도 변환 적용
    df = convert_coords(df, x_col='longitude', y_col='latitude')

    # 위도, 경도 → 지번주소 변환 (좌표 실패 시 도로명주소로 보완)
    df['jibun_address'] = df.apply(safe_jibun_address, axis=1)

    # 지번주소 → 자치구명, 행정동명 추출
    df[['gu_name_from_jibun', 'dong_name_from_jibun']] = df['jibun_address'].apply(safe_extract_gu_dong)

    # ✅ 행정동 이름 정규화
    # 정규화할 기준 동이름 리스트 필요 (ex: 행정동 기준 테이블에서 추출)
    from geocoding.admin_mapper import dong_name_reference_list
    df['dong_name_from_jibun'] = df['dong_name_from_jibun'].apply(
        lambda x: normalize_dong_name(x, standard_names=dong_name_reference_list)
    )

    # 자치구명, 행정동명 → 코드 매핑
    df[['gu_code', 'dong_code']] = df.apply(safe_get_codes, axis=1)

    return df

# 실행
if __name__ == "__main__":
    print("[실행] 시장 데이터를 전처리하고 저장합니다...")
    df_raw = load_store_csv()
    df = mapping_process(df_raw)

    # 저장
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/store__processed.csv"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"저장 완료: {output_path}")

    # 전처리 실패한 행 따로 저장
    failures = df[df['dong_code'].isnull()]
    failures_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/processed/store__failed.csv"))
    failures.to_csv(failures_path, index=False, encoding='utf-8-sig')
    print(f"⚠️ 매핑 실패 데이터 저장 완료: {failures_path}")