import geopandas as gpd
import os

# 경로 설정
INPUT_PATH = "data/reference/HangJeongDong_ver20250401.geojson"
OUTPUT_PATH = "data/reference/Seoul_HangJeongDong.geojson"

# GeoJSON 파일 읽기
gdf = gpd.read_file(INPUT_PATH)

# 서울특별시만 필터링
seoul_gdf = gdf[gdf["sidonm"] == "서울특별시"].copy()

# geometry 단순화 (시각화 속도 개선용)
seoul_gdf["geometry"] = seoul_gdf["geometry"].simplify(0.0003)

# 저장 (GeoJSON)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
seoul_gdf.to_file(OUTPUT_PATH, driver="GeoJSON")

print(f"저장 완료: {OUTPUT_PATH}")
