import requests
import os
from dotenv import load_dotenv

# .env에서 API 키 로드
load_dotenv()
VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")

def road_address_to_coordinates(road_addr: str) -> tuple:
    """
    도로명 주소 → (경도, 위도) 좌표 반환

    Args:
        road_addr (str): 예) '서울특별시 종로구 율곡로 283'

    Returns:
        (longitude, latitude): tuple or (None, None)
    """
    try:
        url = "https://apis.vworld.kr/new2coord.do"
        params = {
            "q": road_addr,
            "output": "json",
            "epsg": "epsg:4326",
            "apiKey": VWORLD_API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        print("응답 내용:", response.text)

        if response.status_code == 200 and 'EPSG_4326_X' in data and 'EPSG_4326_Y' in data:
            return float(data['EPSG_4326_X']), float(data['EPSG_4326_Y'])
        else:
            print(f"[주소→좌표 실패] {road_addr}")
            return None, None
    except Exception as e:
        print(f"[예외 발생 - 주소→좌표] {e}")
        return None, None


def coordinates_to_jibun_address(longitude: float, latitude: float) -> str:
    """
    좌표 → 지번주소 반환 (VWorld API 사용)
    """
    try:
        url = "https://apis.vworld.kr/coord2jibun.do"
        params = {
            "x": longitude,
            "y": latitude,
            "output": "json",
            "epsg": "epsg:4326",
            "apiKey": VWORLD_API_KEY
        }
        response = requests.get(url, params=params)
        print("지번 응답:", response.text)  # 디버깅용

        data = response.json()

        addr = data.get("ADDR", None)
        if response.status_code == 200 and addr:
            return addr
        else:
            print(f"[좌표→지번주소 실패] ({longitude}, {latitude})")
            return None
    except Exception as e:
        print(f"[예외 발생 - 좌표→지번주소] {e}")
        return None

# 순서 : 경도 위도
# 1. 도로명 주소 → 좌표
lon, lat = road_address_to_coordinates("서울특별시 종로구 율곡로 283")
print("좌표:", lon, lat)

# 2. 좌표 → 지번주소
if lon and lat:
    jibun = coordinates_to_jibun_address(lon, lat)
    print("지번주소:", jibun)
