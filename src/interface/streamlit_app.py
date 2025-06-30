# import os
# import sys
# # src 경로 추가 (루트 기준 상대경로)
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# import pandas as pd
# import streamlit as st
# from streamlit_folium import st_folium

# from src.visualization.map_drawer import draw_choropleth

# # 페이지 레이아웃 설정
# st.set_page_config(layout="wide")
# st.title("서울시 행정동 추천 지도")

# # 데이터 및 geojson 경로
# geojson_path = "data/reference/Seoul_HangJeongDong.geojson"
# score_df = pd.read_csv("data/processed/dongjak_dong_scores.csv")
# score_df["adm_cd"] = score_df["adm_cd"].astype(str)

# # 지도 생성
# map_obj = draw_choropleth(geojson_path, score_df)

# # 지도 중앙 정렬 및 유동적 크기 지정
# col1, col2, col3 = st.columns([1, 6, 1])
# with col2:
#     map_data = st_folium(map_obj, width="100%", height=600, returned_objects=["last_active_drawing"])


# # feature 출력
# if map_data and map_data.get("last_active_drawing"):
#     props = map_data["last_active_drawing"]["properties"]
#     clicked_adm_nm = props.get("adm_nm")
#     clicked_code = props.get("adm_cd2")
    
#     st.markdown("### 📍 선택한 행정동 정보")
#     st.write(f"**행정동 이름:** {clicked_adm_nm}")
    
#     # 점수 데이터에서 매칭
#     match = score_df[score_df["adm_cd"] == clicked_code]
#     if not match.empty:
#         score = match.iloc[0]["final_score"]
#         st.write(f"**추천 점수:** {score:.2f}")
#     else:
#         st.warning("선택한 행정동의 점수 정보가 없습니다.")

import os
import sys
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# src 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.visualization.map_drawer import draw_choropleth

# 페이지 레이아웃
st.set_page_config(layout="wide")
st.title("서울시 행정동 추천 시스템")

# 탭 생성
tab1, tab2 = st.tabs(["📋 조건 선택", "🗺️ 지역 추천 지도"])

# ---------------- Tab 1 ---------------- #
with tab1:
    st.header("추천 조건을 설정하세요.")
    st.write("예: 선택 필터, 분석 실행 버튼 등을 여기에 추가합니다.")

# ---------------- Tab 2 ---------------- #
with tab2:
    st.header("추천 점수 기반 행정동 지도")

    try:
        # 데이터 로딩
        geojson_path = "data/reference/Seoul_HangJeongDong.geojson"
        score_path = "data/processed/dongjak_dong_scores.csv"

        score_df = pd.read_csv(score_path)
        score_df["adm_cd"] = score_df["adm_cd"].astype(str)

        # 지도 생성
        m = draw_choropleth(geojson_path, score_df)

        # 지도 렌더링 (주의: width는 정수)
        map_data = st_folium(m, width=1000, height=600, returned_objects=["last_active_drawing"])

        # 클릭한 feature 정보 표시
        if map_data and map_data.get("last_active_drawing"):
            props = map_data["last_active_drawing"]["properties"]
            clicked_adm_nm = props.get("adm_nm")
            clicked_code = props.get("adm_cd2")

            st.markdown("### 📍 선택한 행정동 정보")
            st.write(f"**행정동 이름:** {clicked_adm_nm}")

            match = score_df[score_df["adm_cd"] == clicked_code]
            if not match.empty:
                score = match.iloc[0]["final_score"]
                st.write(f"**추천 점수:** {score:.2f}")
            else:
                st.warning("선택한 행정동의 점수 정보가 없습니다.")

    except Exception as e:
        st.error(f"지도 렌더링 중 오류 발생: {e}")
