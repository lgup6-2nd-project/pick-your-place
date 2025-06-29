import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from src.visualization.map_drawer import draw_choropleth
import pandas as pd
from streamlit_folium import st_folium

st.title("서울시 행정동 추천 지도")

geojson_path = "data/reference/Seoul_HangJeongDong.geojson"
score_df = pd.read_csv("data/processed/dongjak_dong_scores.csv")
score_df["adm_cd"] = score_df["adm_cd"].astype(str)

map_obj = draw_choropleth(geojson_path, score_df)
st_folium(map_obj, width=800, height=600)
