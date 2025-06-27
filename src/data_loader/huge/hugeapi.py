import requests
import pandas as pd

# 1. 기본 정보 설정
API_KEY = '76465a427a7468693537466678464f'  # 디코딩된 KEY
BASE_URL = 'http://openapi.seoul.go.kr:8088'

# 2. URL 생성 함수
def build_url(api_key, service, start, end):
    return f"{BASE_URL}/{api_key}/json/{service}/{start}/{end}"

# 3. 데이터 요청 함수
def fetch_data():
    service_name = 'LOCALDATA_072405'  # ← 이게 실제 '휴게음식점 인허가' 서비스 ID
    start_index = 1
    end_index = 1000

    url = build_url(API_KEY, service_name, start_index, end_index)
    print(f"[DEBUG] 요청 URL: {url}")  # ← 문제 생기면 URL 직접 열어보기

    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            rows = data[service_name]['row']
            df = pd.DataFrame(rows)[['BPLCNM', 'RDNWHLADDR','SNTUPTAENM']]  # ← 컬럼명은 JSON 응답에 따라 조정
            return df
        except Exception as e:
            print("JSON 디코딩 오류:", e)
            print("응답 내용:", response.text[:500])
            return None
    else:
        print(f"API 요청 실패: {response.status_code}")
        print("응답 내용:", response.text)
        return None

# 4. 실행
df = fetch_data()
if df is not None:
    print(df.head())
    df.to_csv('휴게음식점_정제본.csv', index=False, encoding='utf-8-sig')
