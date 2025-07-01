import os
import pandas as pd
import numpy as np

# ------------------ 기본 함수 정의 ------------------ #
def log_scale(series):
    return np.log1p(series)

def calculate_weights(user_scores, base_weights):
    weighted_scores = {k: base_weights.get(k, 0) * user_scores.get(k, 0) for k in base_weights}
    total = sum(weighted_scores.values())
    if total == 0:
        return base_weights
    return {k: v / total for k, v in weighted_scores.items()}

# ------------------ 로직 1: count 데이터 통합 ------------------ #
def load_combined_counts(counts_dir, processed_dir):
    df_merged = None
    feature_to_category = {}

    # 카테고리 매핑
    category_mapping = {
        "transport": ["bus_stop", "subway_station"],
        "living": ["store", "convenience", "market", "library", "park", "bank"],
        "medical": ["pharmacy", "hospital"],
        "safety": ["police_office", "cctv", "street_light", "safety_bell", "crime_rate"],
        "education": ["school"],
        "housing": ["real_estate"]
    }

    # 모든 개별 시설과 해당 카테고리를 연결
    for cat, features in category_mapping.items():
        for f in features:
            feature_to_category[f] = cat

    # 1) __counts.csv 처리
    for fname in os.listdir(counts_dir):
        if not fname.endswith("__counts.csv"):
            continue

        feature = fname.replace("__counts.csv", "")
        file_path = os.path.join(counts_dir, fname)
        df = pd.read_csv(file_path, dtype={'dong_code': str})

        # count 컬럼이 있는 경우
        if 'count' in df.columns:
            df = df[['dong_code', 'gu_code', 'gu_name', 'dong_name', 'count']]
            df = df.rename(columns={'count': feature})
        else:
            continue

        if df_merged is None:
            df_merged = df
        else:
            df_merged = pd.merge(df_merged, df, on=['dong_code', 'gu_code', 'gu_name', 'dong_name'], how='outer')

    # 2) crime_rate 추가
    crime_file = os.path.join(processed_dir, "crime_rate__processed.csv")
    if os.path.exists(crime_file):
        df_crime = pd.read_csv(crime_file, dtype={'dong_code': str})
        df_crime = df_crime[['dong_code', 'crime_rate']]
        df_merged = pd.merge(df_merged, df_crime, on='dong_code', how='left')

    # 3) real_estate 추가
    real_file = os.path.join(processed_dir, "real_estate_dong_avg__processed.csv")
    if os.path.exists(real_file):
        df_real = pd.read_csv(real_file, dtype={'dong_code': str})
        df_real = df_real[['dong_code', 'real_estate']]
        df_merged = pd.merge(df_merged, df_real, on='dong_code', how='left')

    return df_merged, feature_to_category

# ------------------ 로직 2: 점수 계산 ------------------ #
def calculate_scores(df, feature_to_category, user_input_scores, base_weights):
    reverse_features = {'crime_rate', 'real_estate'}
    density_features = {'cctv', 'street_light', 'safety_bell', 'police_office', 'bus_stop', 'subway_station'}

    # 가중치 계산
    weights = calculate_weights(user_input_scores, base_weights)

    # 카테고리별 초기화
    category_scores = {}
    for feature, category in feature_to_category.items():
        if feature not in df.columns:
            continue
        values = log_scale(df[feature].fillna(0))
        if feature in density_features:
            if 'area_km2' in df.columns:
                values = values / df['area_km2'].replace(0, np.nan)
        category_scores.setdefault(category, []).append(values)

    # 카테고리별 합산
    for category in weights:
        if category in category_scores:
            df[category] = np.sum(category_scores[category], axis=0)
        else:
            df[category] = 0.0

    # 정규화 + 역방향 처리
    for category in weights:
        min_val = df[category].min()
        max_val = df[category].max()
        if max_val > min_val:
            norm = (df[category] - min_val) / (max_val - min_val)
            if any(f in reverse_features for f, c in feature_to_category.items() if c == category):
                norm = 1 - norm
            df[category + '_norm'] = norm
        else:
            df[category + '_norm'] = 0.5

    # 최종 점수 계산
    df['final_score'] = 0
    for category in weights:
        df['final_score'] += df[category + '_norm'] * weights.get(category, 0)

    df['final_score'] = (df['final_score'] * 100).round(2)

    return df[['gu_code', 'dong_code', 'gu_name', 'dong_name', 'final_score']].sort_values(by='final_score', ascending=False)

# ------------------ 사용 예시 ------------------ #
if __name__ == "__main__":
    counts_dir = "C:/Users/Admin/Desktop/pick-your-place/data/processed_counts"
    processed_dir = "C:/Users/Admin/Desktop/pick-your-place/data/processed"

    base_weights = {
        "transport": 56.0,
        "living": 37.9 + 24.7,
        "medical": 29.7,
        "safety": 44.2,
        "education": 16.7,
        "housing": 33.1
    }

    user_input_scores = {
        "transport": 8,
        "living": 9,
        "medical": 5,
        "safety": 7,
        "education": 4,
        "housing": 3
    }

    # Step 1: 통합된 df + feature to category
    df_counts, feature_to_category = load_combined_counts(counts_dir, processed_dir)

    # Step 2: 점수 계산
    result_df = calculate_scores(df_counts, feature_to_category, user_input_scores, base_weights)

    print(result_df.head(10))
