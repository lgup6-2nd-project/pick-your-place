# pick-your-place

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
