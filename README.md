
# PICK-YOUR-PLACE

**LG U+ WHY NOT SW CAMP 6기**  

---

## 💡 프로젝트 주제  
서울시로 이사·이주를 고려하는 많은 사람들을 위한 적합한 거주지를 추천 시스템

---

## 📌 서비스 소개  
서울시로 이주하려는 시민들을 대상으로, 다양한 인프라 요소(교통, 의료, 교육, 생활, 안전, 주거 등)를 종합 분석하여 맞춤형 거주지 추천 서비스를 제공하는 플랫폼

각 행정동 단위로 수집된 데이터를 대상으로 반영한 가중치를 점수 기반의 분석을 통해 거주지의 종합 점수를 시각적으로 비교 가능.

Streamlit과 GeoPandas를 활용한 웹 대시보드 상에서 서울시 지도를 기반으로 원하는 동을 선택, 해당 지역의 인프라 지표와 추천 점수를 한눈에 확인할 수 있도록 구성.

이 시스템은 1인 가구나 특정 연령층이 아닌, 서울로 이사하는 일반 시민 누구나 객관적인 기준으로 거주지를 탐색할 수 있도록 설계

---

## 📅 프로젝트 일정

| 날짜            | 주요 작업                          | 담당자               |
|-----------------|-----------------------------------|----------------------|
| 06.26           | 아이디어 회의, 기획안 초안 작성       | 전원 참여             |
| 06.26~06.27     | 데이터 수집 및 정제, 단위 정의        | 김채린, 이찬웅, 강민혁, 조선영 |
| 06.27~06.30     | 통계 로직 설계 (범죄, 교통 등 6종)     | 각 항목별 담당자        |
| 06.30           | 최종 점수 계산 및 DB 저장            | 강민혁               |
| 07.01           | Streamlit 기반 프론트 UI 구현        | 강민혁               |
| 07.01           | 지도 시각화 구현                    | 김채린               |
| 07.01           | 백엔드 지역 추천 로직 완성            | 이찬웅               |
| 07.01           | 예외 상황 대응 및 입력값 테스트        | 김채린, 조선영         |
| 07.01~07.02     | PPT 제작, 발표 준비                  | 전체                 |
| 07.02           | 최종 발표                            | 전체                 |


---

## 👥 팀원 소개

| 이름     | 주요 역할                                                   |
|----------|-------------------------------------------------------------|
| 강민혁   | 팀장<br>- 데이터 수집 및 정제<br>- DB 설계<br>- 데이터 정의서 작성<br>- 아키텍처 설계 |
| 김채린   | - 데이터 수집 및 정제<br>- 지역 추천 로직 설계<br>- 점수 계산 모형 설계<br>- 기획안 작성 |
| 이찬웅   | - 데이터 수집 및 정제<br>- 요구사항정의서 작성<br>- 플로우차트 작성<br>- GIT README 작성 |
| 조선영   | - 데이터 수집 및 정제<br>- 부동산 거래가 로직 설계<br>- WBS 작성<br>- 데이터 연동 정의서 작성<br>- PPT 제작 |


## 파일구조 예시
```text
📦 pick-your-place/
│
├── 📁 data/
│   ├── processed/          # 전처리 완료된 동 단위 데이터
│   ├── raw/                # API/CSV 수집한 원본
│   └── reference/          
│
├── 📁 src/
│   ├── 📁 config/             # 아직 미생성성
│   │   └── settings.py         # API key, 경로, 기준값 등
│   │
│   ├── 📁 data_loader/
│   │   ├── __init__.py
│   │   └── 
│   │
│   ├── 📁 geocoding/
│   │   ├── __init__.py
│   │   ├── admin_mapper.py  
│   │   ├── latlon_to_dong.py   # 위도/경도 → 행정동 코드 매핑 함수
│   │   └── vworld_geocode.py
│   │
│   └── 📁 interface/
│   │   └── streamlit_app.py
│   │
│   ├── 📁 notebooks/
│   │   └──
│   │
│   ├── 📁 preprocessing/
│   │   ├── __init__.py
│   │   └── generate_seoul_geojson.py
│   │
│   └── 📁 visualization/
│       ├── __init__.py
│       └── map_drawer.py
│
├── .env
├── .ignore
├── README.md
└── requirements.txt
```

---

## 브랜치 생성, 수정, 병합

1. 브랜치 생성
```bash
git checkout dev # 브랜치 이동
git pull origin dev
git checkout -b feature/mh-api
```

2. 개발

3. Git에 push
```bash
git add .
git commit -m "[feature] API 연동"
git push origin feature/mh-api
```

4. dev로 merge
```bash
git checkout dev
git merge origin feature/mh-api
git push origin dev
```

5. merge 오류 시 로컬 최신화 (선택)

**상황 예시**
1. 당신: `feature/mh-api` 브랜치 생성 → 작업 시작
2. 다른 팀원: 먼저 `feature/jh-heatmap` → `dev`에 머지 완료
3. 당신: 아직 예전 `dev` 기준으로 작업함
4. → 이 상태에서 PR하려 하니 **dev와 코드가 안 맞음 (conflict)**

**해결방법 (dev → 내 브랜치로 최신화)**
```bash
# 1. dev로 이동해서 최신 코드 가져오기
git checkout dev
git pull origin dev

# 2. 내 작업 브랜치로 이동
git checkout feature/mh-api

# 3. dev를 내 브랜치에 병합 (중요!)
git merge dev
```

🔁 만약 충돌(conflict)이 발생하면?
```bash
# 충돌 파일 수동 수정
# 충돌 부위: <<<<<<< HEAD ~ ======= ~ >>>>>>> dev
# 수정 완료 후:

git add .
git commit -m "[fix] dev 병합 충돌 해결"
```

✅ 최종적으로 다시 push
```bash
git push origin feature/mh-api
```

6. 브랜치 정리
```bash
git branch -d feature/my-api
git push origin --delete feature/mh-api
```

---
