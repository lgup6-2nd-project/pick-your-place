import numpy as np

category_mapping = {
    "transport": ["bus_stop", "subway_station"],
    "living": ["store", "convenience", "market", "library", "center", "park"],
    "medical": ["pharmacy", "hospital"],
    "safety": ["police_office", "cctv", "street_light", "safety_bell", "crime_rate"],
    "education": ["school"],
    "housing": ["real_estate"]
} 

# 기본 가중치 생성
raw_weights = {
    "transport": 56.0,
    "living": 37.9 + 34.7 + 24.7,
    "medical": 29.7,
    "safety": 44.2,
    "education": 16.7,
    "housing": 33.1
}

total = sum(raw_weights.values())
basic_weights = {k: v / total for k, v in raw_weights.items()}
print("기본 가중치(비율):", basic_weights)

# 사용자 점수 반영 가중치 계산 함수
def calculate_weights(user_scores, base_weights):
    """
    user_scores: dict, ex) {"transport": 8, "living": 10, "safety": 5, "residence_edu": 7}
    base_weights: dict 기본 가중치(비율)
    """
    weighted_scores = {k: base_weights.get(k, 0) * user_scores.get(k, 0) for k in base_weights.keys()}
    total = sum(weighted_scores.values())
    if total == 0:
        return base_weights  # 기본값 유지
    return {k: v / total for k, v in weighted_scores.items()}

# 점수 계산 함수
def compute_score(df, category_mapping, weights):
    # 카테고리별 count 합치기
    for cat, cols in category_mapping.items():
        df[cat] = df[cols].sum(axis=1)

    # 정규화 (min-max scaling) <- 해당 부분 더 생각해보기.. 컬럼 간 개수 조정!
    for cat in category_mapping.keys():
        min_val = df[cat].min()
        max_val = df[cat].max()
        if max_val > min_val:
            df[cat + '_norm'] = (df[cat] - min_val) / (max_val - min_val)
        else:
            df[cat + '_norm'] = 0.0

    # 가중치 적용 후 점수 합산
    df['score'] = 0
    for cat in category_mapping.keys():
        df['score'] += df[cat + '_norm'] * weights.get(cat, 0)

    # 0~100 점수로 변환
    df['score'] = (df['score'] * 100).round(1)

    return df


# 사용자 입력 예 (0~10 점)
user_input_scores = {
    "transport": 8,
    "living": 10,
    "safety": 5,
    "residence_edu": 7,
}

# 1) 가중치 계산 (사용자 입력 반영)
weights = calculate_weights(user_input_scores, basic_weights)

# 2) 데이터프레임 로드 (예시 경로)
import pandas as pd
df_counts = pd.read_csv("C:/Users/Admin/Desktop/pick-your-place/data/processed_counts/counts.csv")

# 3) 점수 계산
df_result = compute_score(df_counts, weights, category_mapping)

# 4) 상위 추천지 10개 출력
print(df_result[['gu_name', 'dong_name', 'score']].sort_values(by='score', ascending=False).head(10))
