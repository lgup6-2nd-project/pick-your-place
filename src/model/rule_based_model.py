import os
import pandas as pd
import numpy as np

# 로그 스케일링
def log_scale(series):
    return np.log1p(series)

# 사용자 가중치 기반 최종 가중치 계산
def calculate_weights(user_scores, base_weights):
    weighted_scores = {k: base_weights.get(k, 0) * user_scores.get(k, 0) for k in base_weights}
    total = sum(weighted_scores.values())
    if total == 0:
        return base_weights
    return {k: v / total for k, v in weighted_scores.items()}

# 🔹 로직 1: count 데이터 통합
def load_counts_data(data_dir, area_info_path):
    df_merged = None
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        feature_name = file.replace("__counts.csv", "")
        df = pd.read_csv(file_path, dtype={'dong_code': str})
        val_col = [col for col in df.columns if col != 'dong_code'][0]
        df = df.rename(columns={val_col: feature_name})
        df[feature_name] = df[feature_name].fillna(0)

        if df_merged is None:
            df_merged = df
        else:
            df_merged = pd.merge(df_merged, df, on='dong_code', how='outer')

    df_merged = df_merged.fillna(0)

    # 면적 및 동이름 정보 붙이기
    area_df = pd.read_csv(area_info_path, dtype={'dong_code': str})
    area_df['area_km2'] = pd.to_numeric(area_df['area_km2'], errors='coerce')

    df_final = pd.merge(df_merged, area_df[['dong_code', 'gu_code', 'gu_name', 'dong_name', 'area_km2']], on='dong_code', how='left')
    return df_final


# 🔹 로직 2: 점수 계산
def calculate_scores(df, user_input_scores):
    # 카테고리 정의
    category_mapping = {
        "transport": ["bus_stop", "subway_station"],
        "living": ["store", "convenience", "market", "library", "bank", "park"],
        "medical": ["pharmacy", "hospital"],
        "safety": ["police_office", "cctv", "street_light", "safety_bell", "crime_rate"],
        "education": ["school"],
        "housing": ["real_estate"]
    }

    feature_to_category = {f: cat for cat, feats in category_mapping.items() for f in feats}
    reverse_features = {'crime_rate', 'real_estate'}
    density_features = {'bus_stop', 'subway_station', 'cctv', 'street_light', 'safety_bell', 'police_office'}

    raw_weights = {
        "transport": 56.0,
        "living": 37.9 + 34.7 + 24.7,
        "medical": 29.7,
        "safety": 44.2,
        "education": 16.7,
        "housing": 33.1
    }

    weights = calculate_weights(user_input_scores, raw_weights)

    category_scores = {}
    for feature, category in feature_to_category.items():
        values = log_scale(df[feature])
        if feature in density_features:
            values = values / df['area_km2'].replace(0, np.nan)
        category_scores.setdefault(category, []).append(values)

    # 카테고리별 합산
    for category in weights:
        if category in category_scores:
            df[category] = np.sum(category_scores[category], axis=0)
        else:
            df[category] = 0.0

    # 정규화 및 역방향 처리
    for category in weights:
        min_val = df[category].min()
        max_val = df[category].max()
        if max_val > min_val:
            norm = (df[category] - min_val) / (max_val - min_val)
            if any(f in reverse_features for f, cat in feature_to_category.items() if cat == category):
                norm = 1 - norm
            df[category + '_norm'] = norm
        else:
            df[category + '_norm'] = 0.5

    # 점수 계산
    df['final_score'] = 0
    for category in weights:
        df['final_score'] += df[category + '_norm'] * weights.get(category, 0)

    df['final_score'] = (df['final_score'] * 100).round(2)

    return df[['gu_code', 'dong_code', 'gu_name', 'dong_name', 'final_score']]\
        .sort_values(by='final_score', ascending=False).reset_index(drop=True)



# ----------------------------- 사용 예시 -------------------------------
# 카테고리 정의
category_mapping = {
    "transport": ["bus_stop", "subway_station"],
    "living": ["store", "convenience", "market", "library", "bank", "park"],
    "medical": ["pharmacy", "hospital"],
    "safety": ["police_office", "cctv", "street_light", "safety_bell", "crime_rate"],
    "education": ["school"],
    "housing": ["real_estate"]
}

# 기본 가중치 (비율 변환 전)
raw_weights = {
    "transport": 56.0,
    "living": 37.9 + 24.7,
    "medical": 29.7,
    "safety": 44.2,
    "education": 16.7,
    "housing": 33.1
}

# 사용자 입력 예시
user_input_scores = {
    "transport": 10,
    "living": 7,
    "safety": 5,
    "education": 3,
    "medical": 8,
    "housing": 2
}

data_dir = "C:/Users/Admin/Desktop/pick-your-place/data/processed_counts"  # *__counts.csv 파일들이 있는 폴더
area_info_path = "C:/Users/Admin/Desktop/pick-your-place/model/area_km2.csv"  # 각 동의 면적 정보 포함 CSV

# 로직 1: count 통합
#df_counts = load_counts_data(data_dir, area_info_path)

# 로직 2: 점수 계산
#result_df = calculate_scores(df_counts, user_input_scores)