# 🚀 AllInOneMCP - 지능형 파일 시스템 서버

완전한 하이브리드 서버: FastAPI (HTTP REST) + MCP (JSON-RPC over stdio)  
**🎯 AI 도구 추천 시스템** + **🔧 개선된 Git 도구** + **📊 라인 수 변화 감지** + 고급 파일 편집 도구

## ✨ 새로운 핵심 기능

### 🔧 **개선된 Git 도구 시스템**
- **9개 완전한 Git 도구**: GitPython 기반 안전한 Git 작업
- **Git 명령어 대체**: shell/command Git 실행 오류 해결을 위해 라이브러리 기반으로 전환
- **포괄적 기능**: 저장소 관리, 브랜치 작업, 커밋 관리 등 모든 기본 Git 작업 지원
- **에러 핸들링**: 상세한 오류 메시지와 해결 방안 제시

### 🎯 **AI 도구 추천 시스템**
- `tool_guide` - 상황별 최적 도구 추천 및 사용 가이드
- **⚡ EXPERT** / **🔧 ADVANCED** / **📝 BASIC** 우선순위 체계
- 복잡한 작업 전 자동으로 효율적인 도구 제안
- 작업 유형별 맞춤 추천 (text_replace, line_edit, file_read, code_format)

### 📊 **라인 수 변화 감지**
- 모든 편집 도구에서 **실시간 라인 번호 변화 추적**
- 후속 라인들의 이동 방향과 양 자동 알림
- 안전한 연속 편집을 위한 정확한 라인 위치 정보
- 총 라인 수 변화 요약 (before → after)

## 🛠️ **도구 카테고리 (우선순위별)**

### ⚡ **EXPERT 도구 (8개) - 최고 효율성**
- `backup_file` - 타임스탬프 백업 생성 (위험 작업 전 필수)
- `file_exists` - 초고속 존재 확인 (Yes/No만 반환)
- `analyze_project` - 대형 프로젝트 구조 분석 (compact overview)
- `file_info` - 파일 메타데이터만 조회 (내용 읽지 않음)
- `get_file_section` - 특정 라인만 읽기 (대용량 파일 최적화)
- `regex_replace` - 패턴 기반 고급 교체 (그룹 캡처 지원)
- `smart_indent` - 자동 들여쓰기 조정 (수십 라인 순식간에)
- `patch_apply` - 여러 편집 원자적 처리 (라인 번호 충돌 방지)

### 🔧 **ADVANCED 도구 (21개) - 고급 기능**

**파일 조작:**
- `copy_file` - OS 명령어 기반 고속 복사
- `move_file` - 이동/이름변경 단일 작업
- `delete_file` - 안전한 삭제 (확인 옵션)

**디렉토리 분석:**
- `list_allowed_directories` - 서버 권한 이해 필수
- `count_files` - 확장자별 통계 (수동 카운팅 대비)
- `get_directory_size` - 용량 분석 (자동 계산 대비)
- `get_recent_files` - 최신 변경 추적

**Git 도구 (GitPython 기반):**
- `git_status` - 상세한 저장소 상태 (modified, staged, untracked 파일 분석)
- `git_add` - 파일 스테이징 (단일/다중 파일 지원)
- `git_commit` - 변경사항 커밋 (해시 반환)
- `git_push` - 원격 저장소 푸시 (브랜치/리모트 지정 가능)
- `git_pull` - 원격 저장소 풀 (최신 변경사항 병합)
- `git_clone` - 저장소 복제 (URL에서 로컬로)
- `git_branch` - 브랜치 관리 (생성/전환/목록/삭제)
- `git_log` - 커밋 히스토리 (작성자, 날짜, 메시지 포함)
- `git_init` - 새 저장소 초기화

**시스템 & 텍스트:**
- `execute_command` - 시스템 명령어 (Git 명령 차단, 기능 강화)
- `append_to_file` - 파일 끝 효율적 추가
- `count_occurrences` - 텍스트 패턴 검색
- `insert_at_position` - 바이트 단위 정밀 삽입
- `replace_line_range` - 다중 라인 교체
- `delete_lines` - 라인 범위 삭제

### 📝 **BASIC 도구 (5개) - 간단한 작업**
- `read_file` - 전체 파일 읽기 (get_file_section 우선 고려)
- `write_file` - 파일 쓰기 (append_to_file로 추가 가능)
- `list_directory` - 디렉토리 목록 (analyze_project로 개요 가능)
- `create_directory` - 디렉토리 생성 (단순 신뢰성)
- `find_and_replace` - 단순 텍스트 교체 (regex_replace 우선 고려)
- `insert_line` - 한 줄 삽입 (patch_apply로 다중 작업 가능)

### 🎯 **ESSENTIAL 도구 (2개) - 가이드 & 분석**
- `tool_guide` - 도구 선택 가이드 및 최적화 추천
- `tool_comparison` - 두 도구 직접 비교 분석

## 🔧 **Git 명령어 대체 시스템**

### **shell/command 실행 오류 해결**
```bash
# ❌ 실행 오류가 발생하는 명령어들
execute_command "git status"           # 오류 발생
execute_command "git add ."            # 오류 발생  
execute_command "git commit -m 'test'" # 오류 발생
execute_command "git && malicious"     # 오류 발생

# ✅ 안전한 대안 도구들
git_status                             # 권장
git_add --files=["file1.txt"]         # 권장
git_commit --message="test"           # 권장
```

### **오류 패턴 감지**
- 직접 `git` 명령어
- 명령어 체이닝 (`&&`, `;`, `|`)
- 백틱/서브셸 내 git 명령어
- 다양한 주입 공격 패턴

### **사용자 친화적 안내**
Git 명령어 실행 오류 시 자동으로 사용 가능한 도구 목록 제안:
```
🚫 Git commands cannot be executed due to shell/command issues.

📚 Available Git-specific tools:
• git_status - Check Git repository status
• git_add - Add files to staging area
• git_commit - Commit changes
...
```

## 🔄 **라인 수 변화 감지 시스템**

### **실시간 변화 추적**
```
✅ 기존: "Inserted line at 10"
🎯 개선: "Inserted line at 10
         📈 Added 1 line - Lines 11+ shifted DOWN by 1
         📊 Total lines: 150 → 151"
```

### **변화 유형별 알림**
- **📈 라인 증가**: "Added X lines - Lines Y+ shifted DOWN by X"
- **📉 라인 감소**: "Removed X lines - Lines Y+ shifted UP by X"  
- **✅ 변화 없음**: "Line numbers unchanged"
- **📊 전체 요약**: "Total lines: before → after"

## 💡 **Git 도구 사용 예제**

### **1. 기본 Git 워크플로우**
```python
# 저장소 상태 확인
git_status(repo_path="/path/to/repo")

# 파일 스테이징
git_add(repo_path="/path/to/repo", files=["file1.py", "file2.py"])

# 커밋
git_commit(repo_path="/path/to/repo", message="Add new features")

# 원격 저장소로 푸시
git_push(repo_path="/path/to/repo", remote="origin", branch="main")
```

### **2. 브랜치 관리**
```python
# 브랜치 목록 확인
git_branch(repo_path="/path/to/repo", action="list")

# 새 브랜치 생성
git_branch(repo_path="/path/to/repo", action="create", 
          branch_name="feature-branch", base_branch="main")

# 브랜치 전환
git_branch(repo_path="/path/to/repo", action="checkout", 
          branch_name="feature-branch")

# 브랜치 삭제
git_branch(repo_path="/path/to/repo", action="delete", 
          branch_name="old-branch")
```

### **3. 저장소 관리**
```python
# 새 저장소 초기화
git_init(repo_path="/path/to/new/repo")

# 원격 저장소 복제
git_clone(url="https://github.com/user/repo.git", 
         path="/local/path")

# 커밋 히스토리 조회
git_log(repo_path="/path/to/repo", max_count=5)

# 원격 변경사항 가져오기
git_pull(repo_path="/path/to/repo", remote="origin", branch="main")
```

## 💡 **AI 도구 추천 시스템 사용법**

### **1. 전체 가이드 확인**
```python
tool_guide(show_full_guide=True)
# → 모든 도구의 우선순위별 사용법 안내
```

### **2. 작업별 맞춤 추천**
```python
# 텍스트 교체 최적화
tool_guide(operation_type="text_replace")
# → regex_replace vs find_and_replace 상세 비교

# 라인 편집 최적화  
tool_guide(operation_type="line_edit")
# → patch_apply > replace_line_range > insert_line 추천

# 파일 읽기 최적화
tool_guide(operation_type="file_read")  
# → get_file_section vs read_file 토큰 효율성 비교
```

## 🏗️ **프로젝트 구조**

```
AllInOneMCP/
├── main.py                     # 메인 실행 파일
├── config.py                   # 설정 관리
├── mcp_server.py               # MCP 서버 + 도구 정의
├── tools_registry.py           # 도구 통합 레지스트리
├── requirements.txt            # 의존성 패키지 (GitPython 포함)
├── tools.json                  # 도구 정의 스키마
├── CHANGELOG/                  # 변경 이력 관리
│   └── CHANGELOG_20250612_0230.md
└── tools/                      # 도구 모듈들
    ├── utils.py                        # 공통 유틸리티
    ├── fastapi_routes.py               # FastAPI 라우트들
    ├── file_io.py                      # 기본 파일 I/O
    ├── directory_manager.py            # 디렉토리 관리
    ├── command_executor.py             # 🆕 시스템 명령어 (Git 차단)
    ├── git_tools.py                    # 🆕 GitPython 기반 Git 도구들
    ├── file_metadata.py               # 파일 메타데이터
    ├── text_processor.py               # 기본 텍스트 처리
    ├── advanced_text_processor.py      # 고급 편집 도구
    ├── tool_guide_handler.py           # 도구 추천 핸들러
    └── recommendations/                # AI 추천 시스템
        └── tool_advisor.py                 # 도구 선택 조언자
```

## 📦 **의존성 및 설치**

### **requirements.txt**
```
# MCP 프로토콜 지원
mcp

# FastAPI 웹 프레임워크와 관련 패키지
fastapi
uvicorn[standard]
pydantic
python-multipart

# Git 도구 지원
GitPython

# 성능 최적화 (Linux/macOS만)
uvloop; sys_platform != "win32"
```

### **설치 방법**
```bash
# 저장소 클론
git clone <repository-url>
cd AllInOneMCP

# 의존성 설치
pip install -r requirements.txt

# MCP 서버 실행
python main.py
```

## 🚀 **실행 방법**

### MCP 모드 (기본)
```bash
cd AllInOneMCP
python main.py
```

### FastAPI 모드
```bash
cd AllInOneMCP  
python main.py --fastapi
```

## 🆚 **기존 대비 개선점**

### **❌ 기존 문제점**
- Git 명령어 실행 오류
- 제한적인 Git 기능 (1개 도구)
- AI가 기본 도구만 반복 사용
- 라인 번호 변화로 후속 편집 실패
- 도구 간 우선순위 불명확

### **✅ 개선된 기능**
- 🔧 **기능 개선**: Git 명령어 실행 오류 해결, GitPython 기반 안정적인 작업
- 🎯 **완전한 Git 지원**: 9개 포괄적 도구로 모든 기본 Git 작업 가능
- 🤖 **AI 자동 최적화**: 상황별 최적 도구 자동 제안
- 📊 **라인 추적**: 모든 편집에서 라인 번호 변화 실시간 감지
- ⚡ **우선순위 체계**: EXPERT > ADVANCED > BASIC 명확한 구분
- 🔄 **연속 편집 안전성**: 라인 번호 충돌 방지

## 📊 **성능 최적화**

- **GitPython**: 순수 Python Git 라이브러리로 안정성과 성능 균형
- **uvloop**: Linux/macOS에서 2-4배 빠른 이벤트 루프
- **스트리밍 처리**: 대용량 파일도 메모리 효율적 처리
- **배치 작업**: 여러 편집을 원자적으로 처리
- **토큰 효율성**: get_file_section으로 90% 토큰 절약 가능

## 🔧 **개발 및 기여**

### **백업 시스템**
모든 중요한 파일 수정 시 자동 백업:
- 타임스탬프 기반 백업 파일 생성
- 안정적인 롤백 가능

### **변경 이력 관리**
- `CHANGELOG/` 폴더에 상세한 변경 이력 관리
- 버전별 주요 변경사항 추적

### **테스트 가이드**
```bash
# Git 기능 테스트
git_status
git_branch --action=list

# 명령어 오류 테스트  
execute_command "git status"  # 오류 확인

# 도구 추천 테스트
tool_guide --operation_type=git
```

---

**🎉 이제 AI가 항상 최적의 도구를 선택하여 안전하고 효율적인 파일 편집과 Git 작업이 가능합니다!**

**🔧 Git 명령어 실행 오류가 해결되었으며, 포괄적인 Git 기능으로 모든 개발 워크플로우를 안정적으로 지원합니다.**
