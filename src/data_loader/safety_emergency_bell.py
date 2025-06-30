import requests
from dotenv import load_dotenv
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm       
import math

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', '안전비상벨위치정보.xlsx'))
print("절대경로로 확인:", file_path)

df = pd.read_excel(file_path)
df = df[["소재지지번주소"]] # 소재지지번주소만 가져옴"

result_df = pd.DataFrame(df)
output_path = "../../data/processed/safety_bell_raw.csv"
result_df.to_csv(output_path, index=False)

print("저장 완료", output_path)
