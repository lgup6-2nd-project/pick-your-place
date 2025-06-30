import folium
from folium import Choropleth, GeoJson, GeoJsonTooltip
import json

def draw_choropleth(geojson_path, data_df, value_column="final_score"):
    """
    주어진 GeoJSON 파일과 데이터프레임을 바탕으로 서울시 행정동 단위 Choropleth(단계 구분도)를 시각화합니다.

    Parameters:
    - geojson_path (str): GeoJSON 파일 경로. 'adm_cd2' 속성을 포함해야 함.
    - data_df (pd.DataFrame): 시각화 대상 데이터프레임. 'adm_cd' 컬럼과 value_column을 포함해야 함.
    - value_column (str): Choropleth 색상값으로 사용할 컬럼명 (기본값: 'final_score')

    Returns:
    - folium.Map 객체: HTML로 출력 가능한 지도 객체
    """

    # folium 지도 객체 생성 (서울 중심 좌표 기준, 줌레벨 11)
    m = folium.Map(
        location=[37.5642135, 127.0016985],  # 서울 중심 좌표
        zoom_start=11,                      # 초기 확대 수준
        width=1000,                       # 지도의 가로 크기 - 반응형 설정
        height=600,                      # 지도의 세로 크기 - 반응형 설정
        control_scale=True                  # 축척 컨트롤 추가
    )

    # GeoJSON 파일 로드 (서울시 행정동 경계 정보 포함)
    with open(geojson_path, encoding="utf-8") as f:
        geojson_data = json.load(f)

    # 단계 구분도 계층(Choropleth) 추가
    Choropleth(
        geo_data=geojson_data,                  # 경계 데이터
        data=data_df,                           # 점수 데이터프레임
        columns=["adm_cd", value_column],       # (key, value) 매핑 컬럼
        key_on="feature.properties.adm_cd2",    # GeoJSON의 행정동 코드 속성 (adm_cd2)
        fill_color="Blues",                    # 색상 스케일
        fill_opacity=0.7,                       # 색상 투명도
        line_opacity=0.3,                       # 경계선 투명도
        legend_name="추천 점수"                 # 범례 제목
    ).add_to(m)

    # 마우스오버 시 툴팁(행정동 이름) 보여주는 GeoJSON 레이어
    GeoJson(
        geojson_data,
        tooltip=GeoJsonTooltip(
            fields=["adm_nm"],          # 표시할 속성 필드 (행정동 이름)
            aliases=["행정동"],          # 필드명 별칭
            localize=True,              # 현지화
            sticky=False                # 툴팁 고정 여부
        ),
        style_function=lambda x: {
            "fillOpacity": 0,           # 색상 없음 (투명)
            "color": "black",           # 경계선 색
            "weight": 0.3               # 경계선 두께
        },
        highlight_function=lambda x: {
            'color': 'blue',            # 마우스오버 시 경계선 색
            'weight': 3,                # 마우스오버 시 경계선 두께
            'fillOpacity': 0.3          # 마우스오버 시 배경 투명도
        }
    ).add_to(m)

    # 완성된 지도 객체 반환
    return m
