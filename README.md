# 마이데이터 더미데이터 제작 프로젝트

### 선택 더미 데이터 목록

1. 은행 업권 정보제공 API 규격
2. 카드 업권 정보제공 API 규격


### 기술 스택
- 백엔드 : faspAPI
- 데이터베이스 : PostgreSQL

### 프로젝트 개요
1. 디렉토리 구조
```
mydata_project/
├── app/
│   ├── main.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── core/
├── scripts/
├── alembic/ (추후 생성)
├── .env
├── requirements.txt
```

2. 제작 과정
 1) 필요한 테이블 정의 및 선정
 2) FastAPI + PostgreSQL 환경 구축
    2-1. 기본 테이블 구조 생성 
        - 더미데이터 테스트 (seed script)
    2-2. 응답 형식 리팩토링
    2-3.