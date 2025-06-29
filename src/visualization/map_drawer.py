import folium
from folium import Choropleth, GeoJson, GeoJsonTooltip
import json

def draw_choropleth(geojson_path, data_df, value_column="final_score"):
    m = folium.Map(location=[37.5665, 126.978], zoom_start=11)

    # GeoJSON 로드
    with open(geojson_path, encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Choropleth 계층 시각화
    Choropleth(
        geo_data=geojson_data,
        data=data_df,
        columns=["adm_cd", value_column],  # df에는 adm_cd 컬럼 필요
        key_on="feature.properties.adm_cd",  # GeoJSON과 매핑
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name="추천 점수"
    ).add_to(m)

    # 툴팁 추가 (동이름과 점수)
    GeoJson(
        geojson_data,
        tooltip=GeoJsonTooltip(
            fields=["adm_nm"],
            aliases=["행정동"],
            localize=True,
            sticky=False
        ),
        style_function=lambda x: {
            "fillOpacity": 0,
            "color": "black",
            "weight": 0.3
        }
    ).add_to(m)

    return m
