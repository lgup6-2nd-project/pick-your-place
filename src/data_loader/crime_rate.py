import os
import pandas as pd

def calculate_percentages(file_path: str):
    df_all = pd.read_excel(file_path, header=None)

    # '합계' 행 인덱스 찾기 (index=4인 행)
    total_row = df_all.iloc[4]

    raw_total = str(total_row.iloc[2]).replace(",", "")
    total_occurrence = pd.to_numeric(raw_total, errors='coerce')
    if pd.isna(total_occurrence):
        raise ValueError(f"총 발생 건수가 유효하지 않음: {total_row.iloc[2]}")

    # 자치구별 데이터는 5번째 행부터
    df = df_all.iloc[5:].copy()

    # 컬럼 이름 지정
    df.columns = ["자치구_대분류", "자치구", "발생", "검거", "살인_발생", "살인_검거", 
                  "강도_발생", "강도_검거", "강간_발생", "강간_검거", 
                  "절도_발생", "절도_검거", "폭력_발생", "폭력_검거"]

    # 불필요한 컬럼 제거
    df.drop(columns=["자치구_대분류", "검거", "살인_검거", "강도_검거", "강간_검거", "절도_검거", "폭력_검거"], inplace=True)

    # 숫자 변환
    for col in ["발생", "살인_발생", "강도_발생", "강간_발생", "절도_발생", "폭력_발생"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 발생률 계산
    for crime in ["살인", "강도", "강간", "절도", "폭력"]:
        col_name = f"{crime}_발생"
        rate_col = f"{crime}_발생률(%)"
        df[rate_col] = (df[col_name] / total_occurrence * 100).round(2)

    df["자치구_총발생률(%)"] = (df["발생"] / total_occurrence * 100).round(2)

    output_path_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'crime_rate__processed.csv'))
    df.to_csv(output_path_abs, index=False, encoding="utf-8-sig")
    print(f"[저장 완료] → {output_path_abs}")

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', '5대범죄발생현황.xlsx'))
calculate_percentages(file_path)
