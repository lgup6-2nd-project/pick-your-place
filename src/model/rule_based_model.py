rule_based_model.py 
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
    "living": 37.9 + 24.7,
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
        if feature not in df.columns:
            continue # 음..
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

    # (0) 면적 및 행정동명 먼저 로딩
    area_df = pd.read_csv(area_path, dtype={'dong_code': str, 'gu_code': str})
    area_df['area'] = pd.to_numeric(area_df['area_km2'], errors='coerce')
    area_df = area_df[['dong_code', 'gu_code', 'gu_name', 'dong_name', 'area']]

    # (1) count 파일 불러오기
    for file in os.listdir(count_dir):
        if file == "cctv_gu__counts.csv":
            file_path = os.path.join(count_dir, file)
            df_gu = pd.read_csv(file_path, dtype={'gu_code': str})
            print(f"[DEBUG] Special handling for gu-level file: {file}")

            # gu_code별 dong 목록 가져오기
            dongs_per_gu = area_df[['gu_code', 'dong_code', 'gu_name', 'dong_name']]

            # CCTV를 자치구 내 동 수로 나눠 분배
            cctv_rows = []
            for _, row in df_gu.iterrows():
                gu_code = str(row['gu_code'])  # str 변환 보장
                gu_name = row['gu_name']
                total_cctv = row['counts']

                dongs = dongs_per_gu[dongs_per_gu['gu_code'] == gu_code]
                num_dongs = len(dongs)

                if num_dongs == 0:
                    print(f"[WARNING] {gu_name}({gu_code})에 속한 동이 없습니다. CCTV 무시")
                    continue

                cctv_per_dong = total_cctv / num_dongs
                for _, dong_row in dongs.iterrows():
                    cctv_rows.append({
                        'gu_code': gu_code,
                        'dong_code': str(dong_row['dong_code']),
                        'gu_name': dong_row['gu_name'],
                        'dong_name': dong_row['dong_name'],
                        'cctv': cctv_per_dong
                    })

            df = pd.DataFrame(cctv_rows)

            # 중복 제거
            df['gu_code'] = df['gu_code'].astype(str)
            df['dong_code'] = df['dong_code'].astype(str)
            df = df.drop_duplicates(subset=['gu_code', 'dong_code'])

            
            # df_merged 초기 None 여부 확인 후 병합 전 중복 제거
            if df_merged is not None:
                df_merged['gu_code'] = df_merged['gu_code'].astype(str)
                df_merged['dong_code'] = df_merged['dong_code'].astype(str)
                df_merged = df_merged.drop_duplicates(subset=['gu_code', 'dong_code'])

            # 병합
            if df_merged is None:
                df_merged = df
            else:
                df_merged = pd.merge(df_merged, df, on=['gu_code', 'dong_code', 'gu_name', 'dong_name'], how='outer')

            continue  # 이 파일은 일반 루프에서 다시 처리하지 않게 스킵

        elif file.endswith("__counts.csv"):
            file_path = os.path.join(count_dir, file)
            feature = file.replace("__counts.csv", "")
        
            df = pd.read_csv(file_path, dtype={'dong_code': str, 'gu_code': str})

            # 필수 컬럼 체크
            required_cols = ['gu_code', 'dong_code', 'gu_name', 'dong_name', 'counts']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"[WARNING] 필수 컬럼 {missing_cols} 누락되어 파일 스킵: {file}")
                continue  # 누락 시 병합에서 제외

            # 'counts' 컬럼 -> feature명 변경
            df = df.rename(columns={'counts': feature})

            # 병합 전 타입 일치 보장
            df['gu_code'] = df['gu_code'].astype(str)
            df['dong_code'] = df['dong_code'].astype(str)
            if df_merged is not None:
                df_merged['gu_code'] = df_merged['gu_code'].astype(str)
                df_merged['dong_code'] = df_merged['dong_code'].astype(str)
            
            # 첫 파일이면 그냥 할당
            if df_merged is None:
                df_merged = df
            else:
                df_merged = pd.merge(df_merged, df, on=['gu_code', 'dong_code', 'gu_name', 'dong_name'], how='outer')


    # crime_rate__processed.csv에서 'total_rate' 컬럼을 'crime_rate'로 사용 (향후 컬럼명 변경 가능성 있음)
    # real_estate_dong_avg__processed.csv에서 '평당금액(원)' 컬럼을 'real_estate'로 사용

    # (2) processed 중 필요한 파일만 명시적 로딩
    # crime_rate 파일: 'total_rate' 컬럼 -> 'crime_rate'로 변경
    crime_file = os.path.join(processed_dir, "crime_rate__processed.csv")
    if os.path.exists(crime_file):
        df_crime = pd.read_csv(crime_file, dtype={'gu_code': str})
        df_crime = df_crime.rename(columns={'total_rate': 'crime_rate'})
        df_crime = df_crime[['gu_code', 'crime_rate']]
        df_crime['gu_code'] = df_crime['gu_code'].astype(str)
        df_merged['gu_code'] = df_merged['gu_code'].astype(str)
        df_merged = pd.merge(df_merged, df_crime, on='gu_code', how='left')

    # real_estate 파일: '평당금액(원)' 컬럼 -> 'real_estate'로 변경
    real_estate_file = os.path.join(processed_dir, "real_estate_dong_avg__processed.csv")
    if os.path.exists(real_estate_file):
        df_real = pd.read_csv(real_estate_file, dtype={'dong_code': str})
        df_real = df_real.rename(columns={'평당금액(원)': 'real_estate'})
        df_real = df_real[['dong_code', 'real_estate']]
        df_real['dong_code'] = df_real['dong_code'].astype(str)
        df_merged['dong_code'] = df_merged['dong_code'].astype(str)
        df_merged = pd.merge(df_merged, df_real, on='dong_code', how='left')

    df_merged = df_merged.fillna(0)

    # (3) 면적 및 행정동명 병합
    df_merged = pd.merge(df_merged, area_df, on='dong_code', how='left')

    # (4) 가중치 계산 및 점수 산출
    weights = calculate_weights(user_input_scores)
    df_scored = compute_score(df_merged, feature_to_category, weights)

    # (5) 최종 출력 컬럼 정리 및 정렬
    return df_scored[['gu_code', 'dong_code', 'gu_name', 'dong_name', 'final_score']].sort_values(by='final_score', ascending=False)

__all__ = ['load_and_score_counts', 'category_mapping', 'raw_weights']