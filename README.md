# LocalStoryMap 🗺️
> 지역 이야기를 지도로 공유하는 웹 플랫폼 | 합동 프로젝트

## 📖 프로젝트 소개

LocalStoryMap은 사용자들이 지역의 특별한 이야기와 경험을 지도 위에 표시하고 공유할 수 있는 웹 플랫폼입니다.

## 🛠️ 기술 스택

### Backend
- **Python**: 3.13
- **Django**: 5.2.1
- **Django REST Framework**: 3.16.0
- **PostgreSQL**: 프로덕션 데이터베이스
- **SQLite**: 개발 데이터베이스

### Infrastructure
- **Poetry**: 의존성 관리
- **Gunicorn**: WSGI 서버 (배포용)
- **GitHub Actions**: CI/CD 파이프라인
- **네이버 클라우드 Object Storage**: 정적 파일 저장
- **Discord Webhook**: 배포 알림

### Development Tools
- **PyCharm**: IDE
- **Git**: 버전 관리
- **Postman**: API 테스트 (권장)

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/LocalStoryMap/Oz_Backand.git
cd Oz_Backand/LocalStoryMap
```

### 2. Poetry 설치 및 의존성 설치
```bash
# Poetry 설치 (없는 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install
```

### 3. 환경변수 설정
프로젝트 루트에 `.env` 파일 생성:
```bash
# .env 파일 내용
SECRET_KEY=your-super-secret-key-here
DEBUG=True
```

### 4. 데이터베이스 마이그레이션
```bash
poetry run python manage.py migrate --settings=config.settings.dev
```

### 5. 개발 서버 실행
```bash
poetry run python manage.py runserver --settings=config.settings.dev
```

🎉 **http://127.0.0.1:8000** 에서 확인 가능!

## 🎯 팀원 필수 체크리스트

### 첫 설정 시 확인사항
- [ ] Poetry 설치 완료
- [ ] `.env` 파일 생성 완료
- [ ] `poetry install` 성공
- [ ] 개발 서버 정상 실행 (`runserver`)
- [ ] http://127.0.0.1:8000/admin/ 접속 가능
- [ ] http://127.0.0.1:8000/api/ DRF 화면 확인

### 브랜치 작업 전 체크리스트
- [ ] `git pull origin dev` 최신 코드 받기
- [ ] `feature/기능명` 형식으로 브랜치 생성
- [ ] 커밋 메시지 규칙 준수
- [ ] PR 생성 전 충돌 해결

## 📁 프로젝트 구조

```
LocalStoryMap/
├── config/
│   ├── settings/
│   │   ├── base.py          # 공통 설정
│   │   ├── dev.py           # 개발 환경 설정
│   │   └── prod.py          # 프로덕션 환경 설정
│   ├── urls/
│   │   ├── urls_base.py     # 기본 URL 설정
│   │   ├── urls_dev.py      # 개발용 URL
│   │   └── urls_prod.py     # 프로덕션 URL
│   └── wsgi.py              # WSGI 설정
├── apps/                    # Django 앱들 (개발 예정)
├── static/                  # 개발용 정적 파일
├── staticfiles/             # 수집된 정적 파일 (collectstatic)
├── logs/                    # 로그 파일 (error.log 등)
├── db.sqlite3               # 개발용 SQLite 데이터베이스
├── .github/
│   ├── workflows/
│   │   ├── checks.yml       # CI 품질 검사
│   │   └── deploy.yml       # 자동 배포
│   └── ISSUE_TEMPLATE/      # 이슈 템플릿
├── manage.py
├── pyproject.toml           # Poetry 설정
├── .env                     # 환경변수 (로컬, Git 제외)
└── README.md
```

## 🔧 개발 가이드

### 환경별 설정

#### 개발 환경 (dev)
- SQLite 데이터베이스 사용
- DEBUG = True
- REST API 권한: AllowAny
- 정적 파일: 로컬 서빙

#### 프로덕션 환경 (prod)
- PostgreSQL 데이터베이스 사용
- S3 Object Storage 연동
- 보안 설정 강화
- 로깅 시스템 활성화

### 주요 명령어

```bash
# 개발 서버 실행
poetry run python manage.py runserver --settings=config.settings.dev

# 마이그레이션 생성
poetry run python manage.py makemigrations --settings=config.settings.dev

# 마이그레이션 적용
poetry run python manage.py migrate --settings=config.settings.dev

# 슈퍼유저 생성
poetry run python manage.py createsuperuser --settings=config.settings.dev

# Django Shell 실행
poetry run python manage.py shell --settings=config.settings.dev

# 정적 파일 수집 (프로덕션)
poetry run python manage.py collectstatic --settings=config.settings.prod
```

### API 개발

REST API는 Django REST Framework를 사용합니다:
- **Base URL**: `/api/`
- **Admin Panel**: `/admin/`
- **API Auth**: `/api-auth/`

## 🌿 브랜치 전략

### 브랜치 구조
- `main`: 프로덕션 배포용 브랜치
- `dev`: 개발 통합 브랜치
- `feature/*`: 기능 개발용 브랜치

### 워크플로우
1. `dev` 브랜치에서 `feature/기능명` 브랜치 생성
2. 기능 개발 완료 후 `dev`로 PR 생성
3. 코드 리뷰 후 `dev`에 머지
4. `dev`에서 테스트 완료 후 `main`으로 머지

## 🚀 배포

### 자동 배포
- **개발 서버**: `dev` 브랜치 push 시 자동 배포
- **프로덕션 서버**: `main` 브랜치 push 시 자동 배포
- **서버 주소**: http://223.130.152.69:8000
- **배포 알림**: Discord 채널에서 실시간 확인

### CI/CD 파이프라인

#### Pull Request 시 (Quality Checks)
- ✅ Python 3.13 환경 설정
- ✅ Poetry 의존성 설치
- ✅ 개발 설정 배포 방지 검사
- ✅ 마이그레이션 누락 검사
- ⏳ 테스트 실행 (준비 중)

#### Push 시 (Auto Deploy)
- 🔄 Git 코드 동기화
- 🏗️ Poetry 환경 설정
- 📦 의존성 설치
- 🔧 환경변수 자동 설정
- 📤 정적 파일 S3 업로드
- 🗃️ 데이터베이스 마이그레이션
- 🔄 서버 재시작
- 📢 Discord 배포 알림

## 🤝 기여 가이드

### 1. 이슈 생성
새로운 기능이나 버그는 GitHub Issues를 통해 등록해주세요.

### 2. 브랜치 생성
```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### 3. 개발 및 커밋
```bash
git add .
git commit -m "feat: 새로운 기능 추가"
```

### 4. Pull Request
- PR 템플릿을 사용해서 상세한 설명 작성
- 연관된 이슈 번호 명시
- 스크린샷 첨부 (UI 변경 시)

### 커밋 메시지 규칙
- `feat:` 새로운 기능
- `fix:` 버그 수정
- `docs:` 문서 수정
- `style:` 코드 스타일 변경
- `refactor:` 코드 리팩토링
- `test:` 테스트 추가/수정
- `chore:` 빌드 및 설정 변경

## ⚠️ 주의사항

1. **환경변수**: `.env` 파일은 Git에 커밋하지 마세요
2. **마이그레이션**: 모델 변경 시 반드시 마이그레이션 생성
3. **설정**: 프로덕션에 개발 설정이 들어가지 않도록 주의
4. **의존성**: 새로운 패키지 설치 시 `poetry add package-name` 사용
5. **브랜치**: feature 브랜치에서 작업 후 PR 생성

## 🐛 트러블슈팅

### 자주 발생하는 문제들

#### 1. Poetry 관련 오류
```bash
# Poetry 환경 초기화
poetry env remove --all
poetry install
```

#### 2. 마이그레이션 오류
```bash
# 마이그레이션 초기화 (주의: 데이터 손실 가능)
rm -rf apps/*/migrations/0*.py
poetry run python manage.py makemigrations --settings=config.settings.dev
```

#### 3. 정적 파일 문제
```bash
# 정적 파일 재수집
poetry run python manage.py collectstatic --clear --settings=config.settings.dev
```

#### 4. PyCharm에서 파일이 갈색으로 보일 때
```
환경설정 → 버전 관리 → Git → "VCS에서 무시된 파일 숨기기" 체크
```

## 📞 연락처

- **팀장**: [GitHub 이슈](https://github.com/LocalStoryMap/Oz_Backand/issues)로 문의
- **급한 문의**: Discord 채널 활용
- **배포 상태**: Discord에서 실시간 확인

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## 📈 개발 현황

- [O] 프로젝트 기초 설정
- [O] CI/CD 파이프라인 구축
- [O] 개발/프로덕션 환경 분리
- [O] 데이터베이스 설정
- [O] 정적 파일 S3 연동
- [O] 로깅 시스템 구축
- [O] Discord Webhook 연동
- [ ] 사용자 인증 시스템
- [ ] 지도 API 연동
- [ ] 스토리 CRUD API
- [ ] 프론트엔드 개발

**현재 진행률**: 45% 완료

---

## 🎯 다음 개발 목표

### Phase 1: 기초 기능 개발
- [ ] User 모델 및 인증 시스템
- [ ] Story 모델 및 CRUD API
- [ ] 지도 좌표 연동 기능

### Phase 2: 고급 기능
- [ ] 이미지 업로드 및 관리
- [ ] 검색 및 필터링
- [ ] 좋아요 및 댓글 기능

### Phase 3: 최적화
- [ ] 성능 최적화
- [ ] 모바일 반응형
- [ ] SEO 최적화

---

**Happy Coding! 🎉**
