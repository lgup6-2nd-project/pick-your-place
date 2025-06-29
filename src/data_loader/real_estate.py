import requests
from dotenv import load_dotenv
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import math
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from geocoding import reverse_geocode
from geocoding import road_address_to_coordinates, coordinates_to_jibun_address, coordinates_to_road_address
from geocoding import extract_gu_and_dong, get_gu_dong_codes

"""
전체 데이터 수 확인 및 api 연결
"""
def real_estate(page: int, per_page: int):
    load_dotenv()
    PROPERTY_API_KEY = os.getenv("PROPERTY_API_KEY")
    api_url = 'http://openapi.seoul.go.kr:8088/{PROPERTY_API_KEY}/xml/tbLnOpendataRtmsV/1/5/'

    params = {
        "serviceKey": PROPERTY_API_KEY,
        "returnType": "JSON",
        "page": page,
        "perPage": per_page
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()
    result_json = response.json()

    total_count = result_json.get('totalCount')
    total_pages = math.ceil(total_count / per_page) if total_count else None

    return result_json.get("data", []), total_pages

"""
병렬 수집
"""
def collect_all_property_data(per_page=1000):
    total_pages = real_estate(per_page)
    all_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(property, page, per_page) for page in range(1, total_pages + 1)]

        for future in tqdm(as_completed(futures), total=len(futures), desc="부동산 데이터 수집 중"):
            try:
                result = future.result()
                if result:
                    all_results.extend(result)
            except Exception as e:
                print(f"에러 발생: {e}")
                continue

    return all_results


"""단가 계산 함수"""
def calc_price_per_m2(thing_amt_million_won, arch_area_m2):
    if arch_area_m2 and arch_area_m2 != 0:
        price_per_m2 = (thing_amt_million_won * 10000) / arch_area_m2
        return round(price_per_m2, 2)
    else:
        return None

"""데이터 필터링 및 계산"""
def process_data(items):
    filtered_data = []
    for item in items:
        filtered_item = {
            "자치구코드": item.get("CGG_CD"),
            "자치구명": item.get("CGG_NM"),
            "법정동코드": item.get("STDG_CD"),
            "법정동명": item.get("STDG_NM"),
            "지번구분": item.get("LOTNO_SE"),
            "본번": item.get("MNO"),
            "부번": item.get("SNO"),
            "건물명": item.get("BLDG_NM"),
            "물건금액(만원)": item.get("THING_AMT"),
            "건물면적(m^2)": item.get("ARCH_AREA"),
        }
        filtered_item["1m2당물건금액(원)"] = calc_price_per_m2(
            filtered_item["물건금액(만원)"],
            filtered_item["건물면적(m^2)"]
        )
        filtered_data.append(filtered_item)
    return filtered_data

"""CSV 저장 함수"""
def save_to_csv(data, filename):
    df = pd.DataFrame(data)

    current_dir = os.path.dirname(__file__)  # 현재 스크립트 위치
    output_dir = os.path.abspath(os.path.join(current_dir, "../../data/processed"))
    output_file = os.path.join(output_dir, filename)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"CSV 저장 완료: {output_file}")


if __name__ == "__main__":
    try:
        raw_data = collect_all_property_data()
        processed_data = process_data(raw_data)
        save_to_csv(processed_data, "real_estate__processed.csv")
    
    except Exception as e:
        print(f"전체 처리 중 에러 발생: {e}")

