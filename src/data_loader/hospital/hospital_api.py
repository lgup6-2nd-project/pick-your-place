import requests
import pandas as pd
import os

# 기본 설정
API_KEY = '576d4c655874686937394d67724649'
SERVICE_NAME = 'TbHospitalInfo'
BASE_URL = 'http://openapi.seoul.go.kr:8088'
START_INDEX = 1
END_INDEX = 1000
TYPE = 'json'

SAVE_DIR = 'src/data_loader/hospital'  # 저장 폴더

def fetch_hospital_data():
    url = f"{BASE_URL}/{API_KEY}/{TYPE}/{SERVICE_NAME}/{START_INDEX}/{END_INDEX}"
    print(f"📡 요청 URL: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ 요청 실패: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    items = data['TbHospitalInfo']['row']
    df = pd.DataFrame(items)

    # ✅ 정확한 컬럼명 반영 (DUTYDIVNAM ← OK)
    df = df[['DUTYNAME', 'DUTYADDR', 'WGS84LAT', 'WGS84LON', 'DUTYDIVNAM']].copy()
    df.rename(columns={
        'DUTYNAME': 'hospital_name',
        'DUTYADDR': 'address',
        'WGS84LAT': 'latitude',
        'WGS84LON': 'longitude',
        'DUTYDIVNAM': 'hospital_type'
    }, inplace=True)

    return df


def save_by_hospital_type(df: pd.DataFrame):
    os.makedirs(SAVE_DIR, exist_ok=True)

    grouped = df.groupby('hospital_type')
    for hospital_type, group in grouped:
        filename = f"{hospital_type}.csv"
        filepath = os.path.join(SAVE_DIR, filename)
        group.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"✅ 저장 완료: {filepath} ({len(group)}건)")


if __name__ == "__main__":
    df = fetch_hospital_data()
    if df is not None:
        save_by_hospital_type(df)