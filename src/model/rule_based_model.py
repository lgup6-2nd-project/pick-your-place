# rule_based.py
import os
import pandas as pd
import numpy as np

# ======= 고정값: 카테고리 정의 & 기본 가중치 =======
category_mapping = {
    "transport": ["bus_stop", "subway_station"],
    "living": ["store", "convenience", "market", "library", "bank", "park"],
    "medical": ["pharmacy", "hospital"],
    "safety": ["police_office", "cctv", "street_light", "safety_bell", "crime_rate"],
    "education": ["school"],
    "housing": ["real_estate"]
}

raw_weights = {
    "transport": 56.0,
    "living": 37.9 + 34.7 + 24.7,
    "medical": 29.7,
    "safety": 44.2,
    "education": 16.7,
    "housing": 33.1
}

# ======= 설정 =======
reverse_features = {'crime_rate', 'real_estate'}
density_features = {'cctv', 'street_light', 'safety_bell', 'police_office', 'bus_stop', 'subway_station'}


# ======= 함수 =======

def log_scale(series):
    return np.log1p(series)

def calculate_weights(user_scores):
    weighted_scores = {k: raw_weights.get(k, 0) * user_scores.get(k, 0) for k in raw_weights}
    total = sum(weighted_scores.values())
    if total == 0:
        return raw_weights
    return {k: v / total for k, v in weighted_scores.items()}

def compute_score(df, feature_to_category, weights):
    category_scores = {}

    for feature, category in feature_to_category.items():
        values = log_scale(df[feature])
        if feature in density_features:
            values = values / df['area'].replace(0, np.nan)
        category_scores.setdefault(category, []).append(values)

    for category in weights:
        if category in category_scores:
            df[category] = np.sum(category_scores[category], axis=0)
        else:
            df[category] = 0.0

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

    df['final_score'] = 0
    for category in weights:
        df['final_score'] += df[category + '_norm'] * weights.get(category, 0)

    df['final_score'] = (df['final_score'] * 100).round(2)
    return df

def load_and_score_counts(count_dir, processed_dir, area_path, user_input_scores):
    feature_to_category = {feature: cat for cat, features in category_mapping.items() for feature in features}
    df_merged = None

    # (1) count 파일 불러오기
    for file in os.listdir(count_dir):
        if file.endswith("__counts.csv"):
            feature = file.replace("__counts.csv", "")
            df = pd.read_csv(os.path.join(count_dir, file), dtype={'dong_code': str})
            
            # 컬럼이 'dong_code', 'count'라고 가정할 때
            count_col = [col for col in df.columns if col != 'dong_code'][0]
            df = df.rename(columns={count_col: feature})
            
            df[feature] = df[feature].fillna(0)
            df_merged = df if df_merged is None else pd.merge(df_merged, df, on='dong_code', how='outer')

    # (2) processed 파일 추가
    for file in os.listdir(processed_dir):
        if file.endswith("__processed.csv"):
            feature = file.replace("__processed.csv", "")
            if feature == "real_estate":
                file_path = os.path.join(processed_dir, "real_estate_dong_avg__processed.csv")
            else:
                file_path = os.path.join(processed_dir, file)
            df = pd.read_csv(file_path, dtype={'dong_code': str})
            df = df.rename(columns={col: feature for col in df.columns if col != 'dong_code'})
            df[feature] = df[feature].fillna(0)
            df_merged = pd.merge(df_merged, df, on='dong_code', how='outer')

    df_merged = df_merged.fillna(0)

    # (3) 면적 병합
    area_df = pd.read_csv(area_path, dtype={'dong_code': str})
    area_df['area'] = pd.to_numeric(area_df['area_km2'], errors='coerce')
    area_df = area_df[['dong_code', 'gu_code', 'gu_name', 'dong_name', 'area']]
    df_merged = pd.merge(df_merged, area_df, on='dong_code', how='left')


    # (4) 가중치 계산 + 점수 계산
    weights = calculate_weights(user_input_scores)
    df_scored = compute_score(df_merged, feature_to_category, weights)

    # (5) 출력 형식 정리
    return df_scored[['gu_code', 'dong_code', 'gu_name', 'dong_name', 'final_score']].sort_values(by='final_score', ascending=False)

__all__ = ['load_and_score_counts', 'category_mapping', 'raw_weights']
