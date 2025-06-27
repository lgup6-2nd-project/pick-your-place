import requests
from dotenv import load_dotenv
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm       
import math

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
        "perPage": perPage
    }
#    print(response.status_code)
#    print(response.json())

    try:
        response = requests.get(url, params=params)
#        print(response)
        if response.status_code == 200:
            smart_street_light_results = [
                {
                '경도' : LIGHT_DATA.get('경도'),
                '위도' : LIGHT_DATA.get('위도'),
                '관리번호' : LIGHT_DATA.get('관리번호')
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


if __name__ == "__main__":
    df = pd.DataFrame(collect_all_light_data())
#    print(df)
    df.to_csv("../../data/processed/street_lights.csv", index=False, encoding="utf-8-sig")
    print("CSV 저장 완료: street_lights.csv")


