import requests
from dotenv import load_dotenv
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm       
import math
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from geocoding import reverse_geocode # 도로명 주소 변환 파일
from geocoding import road_address_to_coordinates, coordinates_to_jibun_address, coordinates_to_road_address
from geocoding import extract_gu_and_dong, get_gu_dong_codes

"""
API 연결
"""
def smart_street_light(page=1, perPage=1000):
    management_num = ''
    latitude = ''
    longitude = ''

    load_dotenv()
    LIGHT_API_KEY = os.getenv("LIGHT_API_KEY")
    url = 'https://api.odcloud.kr/api/15107934/v1/uddi:20b10130-21ed-43f3-8e58-b8692fb8a2ff'
    params = {
        "serviceKey": LIGHT_API_KEY, 
        "returnType": "JSON",
        "perPage": perPage,
        "page": page,
    }
#    print(response.status_code)
#    print(response.json())

    try:
        response = requests.get(url, params=params)
#        print(response)
        if response.status_code == 200:
            smart_street_light_results = [
                {
                'lon' : LIGHT_DATA.get('경도'),
                'lat' : LIGHT_DATA.get('위도'),
                'manage_id' : LIGHT_DATA.get('관리번호')
                } for LIGHT_DATA in response.json().get('data', [])]
            return smart_street_light_results
        else:
            print(f"연결 오류 : {response.status_code}")
        
    except Exception as e:
        print(f"연결 오류 : {e}")
    return []


"""
전체 데이터 수 확인
"""
def get_total_pages(perPage=1000):
   
    load_dotenv()
    LIGHT_API_KEY = os.getenv("LIGHT_API_KEY")
    url = 'https://api.odcloud.kr/api/15107934/v1/uddi:20b10130-21ed-43f3-8e58-b8692fb8a2ff'
    params = {
        "serviceKey": LIGHT_API_KEY,
        "returnType": "JSON",
        "page": 1,
        "perPage": 1
    }
    response = requests.get(url, params=params)
    total_count = response.json().get('totalCount', 0)
    print(f"총 데이터 수: {total_count}")
    return math.ceil(total_count / perPage)

"""
모든 페이지 병렬 요청
"""
def collect_all_light_data():
    perPage = 1000
    total_pages = get_total_pages(perPage)
    smart_street_light_all_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(smart_street_light, page, perPage) for page in range(1, total_pages + 1)]

        for future in tqdm(as_completed(futures), total=len(futures), desc="가로등 데이터 수집 중"):
            result = future.result()
            if result:
                smart_street_light_all_results.extend(result)

    return smart_street_light_all_results

"""
도로명 주소 변환 및 컬럼 추가
"""
def latlon_to_address(df):
    print("도로명 주소 변환 중")
    def safe_reverse(row):
        try:
            if pd.notnull(row['lon']) and pd.notnull(row['lat']):
                return reverse_geocode(row['lon'], row['lat'])
            else:
                return None
        except Exception as e:
            print(f"[예외 발생] {e}")
            return None

    df['road_address'] = df.apply(safe_reverse, axis=1)
    return df

# """
# 도로명주소 → 좌표 → 지번 주소 변환하여 컬럼 추가
# """
# def enrich_with_coords_and_jibun(df: pd.DataFrame) -> pd.DataFrame:
#     print("좌표, 지번 주소 변환 중")
#     longitudes, latitudes, jibun_addrs = [], [], []

#     for addr in tqdm(df['road_address'], desc="도로명주소 → 좌표 → 지번 변환"):
#         if pd.isnull(addr):
#             longitudes.append(None)
#             latitudes.append(None)
#             jibun_addrs.append(None)
#             continue

#         lon, lat = road_address_to_coordinates(addr)
#         longitudes.append(lon)
#         latitudes.append(lat)

#         if lon and lat:
#             jibun_addr = coordinates_to_jibun_address(lon, lat)
#         else:
#             jibun_addr = None

#         jibun_addrs.append(jibun_addr)

#     df['longitude_from_address'] = longitudes
#     df['latitude_from_address'] = latitudes
#     df['jibun_address'] = jibun_addrs

#     return df


if __name__ == "__main__":
    df = pd.DataFrame(collect_all_light_data())
    #    print(df)
    df = latlon_to_address(df) # 도로명 주소 관련 함수
    print("도로명 주소 변환 완료")
    # df = enrich_with_coords_and_jibun(df) # 좌표, 지번 관련 함수
    # print("도로명 주소 → 좌표, 지번 주소 변환 완료")
    
    current_dir = os.path.dirname(__file__)  # 현재 파일 기준 상대경로로 저장
    output_dir = os.path.abspath(os.path.join(current_dir, "../../data/processed"))
    output_file = os.path.join(output_dir, "street_light__processed.csv")
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("CSV 저장 완료: street_lights__processed.csv")
    