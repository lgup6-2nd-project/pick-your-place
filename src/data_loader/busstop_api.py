from dotenv import load_dotenv
import os
import requests

load_dotenv()

try: 
    SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
    if SEOUL_API_KEY is None:
        raise ValueError("'.env' 파일에 'SEOUL_API_KEY'가 정의되어 있지 않습니다.")
except Exception as e:
    print(f"[환경 변수 오류] {e}")
    SEOUL_API_KEY = None  # 방어적으로 None 설정

def fetch_bus_stop_data(start: int = 1, end: int = 11290) -> list:
    """
    서울시 버스정류소 위치 데이터를 JSON으로 수집하여 리스트 형태로 반환
    """
    url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/busStopLocationXyInfo/{start}/{end}/"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            return data['busStopLocationXyInfo']['row']
        
        except (KeyError, ValueError):
            print("데이터 파싱 오류 발생")
            return []
    else:
        print(f"API 호출 실패: {response.status_code}")
        return []
