import pandas as pd
import os
import re

df = pd.read_csv('휴게음식점_정제본.csv', encoding='utf-8-sig')

def extract_gu(address):
    if not isinstance(address, str):
        return None
    match = re.search(r'서울특별시\s*(\S+구)', address)
    if match:
        return match.group(1)
    return None



df['자치구'] = df['RDNWHLADDR'].apply(extract_gu)  # ❗ 주석 풀기

print("자치구 목록:", df['자치구'].unique())
print(df[['RDNWHLADDR', '자치구']].head())

os.makedirs('구별_CSV', exist_ok=True)

for gu_name, gu_df in df.groupby('자치구'):
    if pd.isna(gu_name):
        continue
    filename = f"{gu_name}.csv"
    gu_df.to_csv(os.path.join('구별_CSV', filename), index=False, encoding='utf-8-sig')
    print(f"✅ 저장 완료: {filename}")
