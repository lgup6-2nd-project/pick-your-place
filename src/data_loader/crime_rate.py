import pandas as pd

def calculate_percentages(file_path: str, output_path: str):
    df_all = pd.read_excel(file_path, skiprows=0)
    total_row = df_all.iloc[0]
    df = pd.read_excel(file_path, skiprows=2) # 자치구 데이터만 (3번째 행부터)

    # 이름 재정의
    df.columns = ["자치구", "소계", "발생", "검거", "살인_발생", "살인_검거", "강도_발생", "강도_검거",
                  "강간_발생", "강간_검거", "절도_발생", "절도_검거", "폭력_발생", "폭력_검거"]

    total_occurrence = total_row[2] # 전체 '발생 소계' (자치구별 발생총합)

    # 범죄별 발생 소계
    total_by_crime = {
        "살인_발생": total_row[4],
        "강도_발생": total_row[6],
        "강간_발생": total_row[8],
        "절도_발생": total_row[10],
        "폭력_발생": total_row[12]
    }

    # 자치구별 범죄 발생률 계산: 자치구 해당 범죄 / 전체 발생 소계
    for crime in ["살인", "강도", "강간", "절도", "폭력"]:
        col_name = f"{crime}_발생"
        rate_col = f"{crime}_발생률(%)"
        df[rate_col] = (df[col_name] / total_occurrence * 100).round(2)

    # 자치구별 전체 발생률 (전체 자치구 발생 / 전체 발생 소계)
    df["자치구_총발생률(%)"] = (df["발생"] / total_occurrence * 100).round(2)

    df.to_excel(output_path, index=False)
    print(f"저장 완료: {output_path}")

calculate_percentages("../../data/raw/5대 범죄 발생현황.xlsx", "../../data/processed/crime_rate__processed.xlsx")
