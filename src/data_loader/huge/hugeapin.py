import pandas as pd
import os

# 1. 전체 파일 로드 (기존에 저장했던 csv)
df = pd.read_csv('휴게음식점_정제본.csv', encoding='utf-8-sig')  # 인코딩은 저장했던 방식에 맞춰

# 2. 업태구분명 기준으로 그룹핑
if 'SNTUPTAENM' not in df.columns:
    raise ValueError("CSV에 '업태구분명' 컬럼이 없습니다. 컬럼명을 다시 확인해주세요.")

# 3. 저장할 디렉토리 생성
output_dir = "업태별_CSV"
os.makedirs(output_dir, exist_ok=True)

# 4. 업태구분명으로 분할 저장
for 업태명, 업태_df in df.groupby('SNTUPTAENM'):
    filename = f"{업태명}.csv".replace("/", "_")  # 슬래시가 있는 경우 방지
    save_path = os.path.join(output_dir, filename)
    업태_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"저장 완료: {save_path}")
