import requests
from dotenv import load_dotenv
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import math
import sys


"""
전체 데이터 수 확인 및 api 연결
"""
def real_estate(page: int, per_page: int):
    load_dotenv()
    PROPERTY_API_KEY = os.getenv("PROPERTY_API_KEY")

    start_index = (page - 1) * per_page + 1
    end_index = page * per_page

    api_url = f"http://openapi.seoul.go.kr:8088/{PROPERTY_API_KEY}/json/tbLnOpendataRtmsV/{start_index}/{end_index}/"

    response = requests.get(api_url)
    response.raise_for_status()

    try:
        result_json = response.json()
    except Exception as e:
        print(f"JSON 변환 오류: {e}")
        print(f"응답 내용: {response.text}")
        raise

    total_count = result_json.get('tbLnOpendataRtmsV', {}).get('list_total_count')
    total_pages = math.ceil(total_count / per_page) if total_count else None

    data = result_json.get('tbLnOpendataRtmsV', {}).get('row', [])

    return data, total_pages


"""
병렬 수집
"""
def collect_all_property_data(per_page=1000):
    _, total_pages = real_estate(1, per_page)
    all_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(real_estate, page, per_page) for page in range(1, total_pages + 1)]


        for future in tqdm(as_completed(futures), total=len(futures), desc="부동산 데이터 수집 중"):
            try:
                result, _ = future.result()
                if result:
                    all_results.extend(result)
            except Exception as e:
                print(f"에러 발생: {e}")
                continue

    return all_results


"""CSV 저장 함수"""
def save_to_csv(data, filename):
    df = pd.DataFrame(data)

    current_dir = os.path.dirname(__file__)  # 현재 스크립트 위치
    output_dir = os.path.abspath(os.path.join(current_dir, "../../data/raw"))
    output_file = os.path.join(output_dir, filename)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"CSV 저장 완료: {output_file}")


if __name__ == "__main__":
    try:
        raw_data = collect_all_property_data()
        save_to_csv(raw_data, "real_estate__raw.csv")
    
    except Exception as e:
        print(f"전체 처리 중 에러 발생: {e}")

