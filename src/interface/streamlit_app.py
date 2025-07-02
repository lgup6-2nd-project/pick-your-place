import os
import sys
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.visualization.map_drawer import draw_choropleth
from src.model.rule_based_model_test import load_counts_data, calculate_scores

# 페이지 설정
st.set_page_config(layout="wide")
st.title("서울시 행정동 추천 시스템")

# ✅ 카테고리별 변수 매핑
category_mapping = {
    "transport": ["bus_stop", "subway_station"],
    "living": ["store", "convenience", "market", "library", "center", "park"],
    "medical": ["pharmacy", "hospital"],
    "safety": ["police_office", "cctv", "street_light", "safety_bell", "crime_rate"],
    "education": ["school"],
    "housing": ["real_estate"]
}

# ✅ 초기 세션 상태 설정
if "result_df" not in st.session_state:
    st.session_state["result_df"] = None

# ---------------- 상단: 슬라이더 가로 정렬 ---------------- #
st.markdown("#### 🧭 추천 조건 설정")
st.markdown("6개 카테고리에 대해 중요도를 설정하세요. 입력한 가중치는 해당 범주의 모든 항목에 동일하게 적용됩니다.")

col1, col2, col3 = st.columns(3)
with col1:
    transport_weight = st.slider("🚌 교통 인프라", 0, 10, 5)
    living_weight = st.slider("🏪 생활 인프라", 0, 10, 5)
with col2:
    medical_weight = st.slider("💊 의료 인프라", 0, 10, 5)
    safety_weight = st.slider("🛡️ 안전 인프라", 0, 10, 5)
with col3:
    education_weight = st.slider("🏫 교육 인프라", 0, 10, 5)
    housing_weight = st.slider("🏠 주거 정보", 0, 10, 5)

# weights = {}
# for cat, vars_in_cat in category_mapping.items():
#     cat_weight = {
#         "transport": transport_weight,
#         "living": living_weight,
#         "medical": medical_weight,
#         "safety": safety_weight,
#         "education": education_weight,
#         "housing": housing_weight,
#     }[cat]
#     for var in vars_in_cat:
#         weights[var] = cat_weight

user_input_scores = {
    "transport": transport_weight,
    "living": living_weight,
    "medical": medical_weight,
    "safety": safety_weight,
    "education": education_weight,
    "housing": housing_weight,
}

# 버튼 우측 정렬
button_col = st.columns([6, 1])[1]
with button_col:
    if st.button("✅ 추천 점수 계산"):
        # # st.success("추천 점수 계산 로직은 아직 구현되지 않았습니다.")
        # base_df = load_aggregated_data()
        # result_df = calculate_weighted_scores(base_df, weights)
        # st.dataframe(result_df)

        # data_dir = "data/processed_counts"
        # area_info_path = "model/area_km2.csv"

        with st.spinner("데이터 불러오는 중..."):
            base_df = load_counts_data()  # 팀원 로직 1

        with st.spinner("추천 점수 계산 중..."):
            result_df = calculate_scores(base_df, user_input_scores)  # 팀원 로직 2
            st.session_state["result_df"] = result_df
            st.success("추천 점수 계산 완료!")

# 💡 항상 세션 상태에서 result_df를 꺼내고, 존재할 때만 사용
if "result_df" in st.session_state and st.session_state["result_df"] is not None:
    result_df = st.session_state["result_df"]
    st.dataframe(result_df.head(10))
else:
    st.info("먼저 '추천 점수 계산' 버튼을 눌러주세요.")

# ---------------- 중단: 지도 + 상위 10개 ---------------- #
st.markdown("---")
left_col, right_col = st.columns([2, 1])

clicked_dong_name = None
clicked_code = None
final_score = None
clicked_gu_name = None
result_df = st.session_state["result_df"]

with left_col:
    st.markdown("#### 🗺️ 추천 점수 기반 행정동 지도")

    if result_df is not None:
        try:
            geojson_path = "data/reference/Seoul_HangJeongDong.geojson"
            result_df["dong_code"] = result_df["dong_code"].astype(str)

            m = draw_choropleth(
                geojson_path=geojson_path,
                data_df=result_df,
                value_column="final_score",
                key_column="dong_code"
            )

            map_data = st_folium(m, width=1000, height=650, returned_objects=["last_active_drawing"])

            if map_data and map_data.get("last_active_drawing"):
                props = map_data["last_active_drawing"]["properties"]
                clicked_code = props.get("adm_cd2")
                match = result_df[result_df["dong_code"] == clicked_code]
                if not match.empty:
                    final_score = match.iloc[0]["final_score"]
                    clicked_dong_name = match.iloc[0]["dong_name"]
                    clicked_gu_name = match.iloc[0]["gu_name"]

        except Exception as e:
            st.error(f"지도 렌더링 중 오류 발생: {e}")
    else:
        st.info("먼저 '추천 점수 계산' 버튼을 눌러주세요.")

with right_col:
    st.markdown("#### 🔝 상위 10개 추천 동")
    try:
        # top10_df = result_df.sort_values("final_score", ascending=False).head(10)
        # top10_display = top10_df[["gu_name", "dong_name", "final_score"]].reset_index(drop=True)
        st.dataframe(result_df, use_container_width=True)
    except:
        st.warning("상위 추천 동 정보를 불러올 수 없습니다.")

# ---------------- 하단: 선택한 행정동 정보 ---------------- #
st.markdown("---")
st.markdown("#### 📍 선택한 행정동 정보")
if clicked_code:
    st.write(f"**자치구:** {clicked_gu_name}")
    st.write(f"**행정동:** {clicked_dong_name}")
    if final_score is not None:
        st.write(f"**점수:** {final_score:.2f}")
        
    else:
        st.warning("해당 동의 점수를 찾을 수 없습니다.")
else:
    st.info("지도를 클릭해 행정동을 선택하세요.")
