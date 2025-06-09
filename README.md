# 🚀 AllInOneMCP - 고급 파일 시스템 서버

완전한 하이브리드 서버: FastAPI (HTTP REST) + MCP (JSON-RPC over stdio)  
모듈화된 구조 + uvloop 성능 최적화 + 고급 파일 편집 도구

## ✨ 주요 기능

### 📁 **기본 파일 I/O**
- `read_file` - 자동 인코딩 감지로 파일 읽기
- `write_file` - UTF-8로 파일 쓰기
- `copy_file` - 메타데이터 포함 파일 복사
- `move_file` - 파일 이동/이름 변경
- `delete_file` - 안전한 파일 삭제 (확인 옵션)
- `backup_file` - 타임스탬프 백업 생성

### 📂 **디렉토리 관리**
- `list_directory` - 디렉토리 내용 조회
- `create_directory` - 재귀적 디렉토리 생성
- `count_files` - 확장자별 파일 개수
- `get_directory_size` - 디렉토리 총 크기
- `get_recent_files` - 최근 수정 파일 목록
- `analyze_project` - 프로젝트 구조 분석

### ✏️ **기본 텍스트 편집**
- `find_and_replace` - 텍스트 찾기/바꾸기 (대소문자 옵션)
- `insert_line` - 특정 위치에 라인 삽입
- `append_to_file` - 파일 끝에 내용 추가
- `get_file_section` - 특정 라인 범위 읽기
- `count_occurrences` - 텍스트 출현 횟수 카운트

### 🔧 **고급 편집 도구**
- `replace_line_range` - 라인 범위 교체 (메모리 효율적)
- `delete_lines` - 특정 라인들 삭제
- `regex_replace` - 정규식 기반 고급 찾기/바꾸기
- `smart_indent` - 스마트 들여쓰기 조정
- `patch_apply` - 여러 편집 작업 배치 실행

### 🔍 **메타데이터 & 유틸리티**
- `file_exists` - 파일/디렉토리 존재 확인
- `file_info` - 파일 정보 조회 (크기, 수정일 등)
- `git_status_summary` - Git 상태 요약
- `execute_command` - 시스템 명령어 실행

## 🆚 **기존 대비 편집 기능 개선점**

### **기존 방식의 문제점:**
❌ 전체 파일을 메모리로 로드  
❌ 임시 파일 생성/이동 오버헤드  
❌ 큰 파일에서 비효율적  
❌ 단순한 텍스트 replace만 지원  

### **개선된 방식:**
✅ **스트리밍 처리** - 메모리 효율적  
✅ **배치 작업** - 여러 편집을 한 번에  
✅ **정규식 지원** - 고급 패턴 매칭  
✅ **정밀한 위치 편집** - 라인/문자 단위  
✅ **대용량 파일 최적화** - 큰 파일도 빠르게  

## 📊 **성능 최적화**

### **uvloop 적용**
- Linux/macOS: **2-4배 빠른** 이벤트 루프
- Windows: 안전한 fallback으로 호환성 보장

### **메모리 효율성**
- 스트리밍 파일 처리로 메모리 사용량 최소화
- 큰 파일도 안정적으로 처리

## 🏗️ **모듈화된 구조**

```
AllInOneMCP/
├── main.py                 # 메인 실행 파일
├── config.py               # 설정
├── mcp_server.py           # MCP 서버 설정
├── tools_registry.py       # 도구 통합 레지스트리
├── requirements.txt        # 의존성 패키지
└── tools/                  # 도구 모듈들
    ├── utils.py                    # 공통 유틸리티
    ├── fastapi_routes.py           # FastAPI 라우트들
    ├── file_io.py                  # 파일 I/O 도구들
    ├── file_tools.py               # 통합 파일 도구들
    ├── directory_manager.py        # 디렉토리 관리
    ├── git_helper.py               # Git & 시스템 명령어
    ├── text_processor.py           # 기본 텍스트 처리
    ├── advanced_text_processor.py  # 고급 편집 도구
    └── file_metadata.py            # 파일 메타데이터
```

## 🚀 **실행 방법**

### MCP 모드 (기본)
```bash
cd E:\Project\mcp\AllInOneMCP
python main.py
```

### FastAPI 모드
```bash
cd E:\Project\mcp\AllInOneMCP
python main.py --fastapi
```

## 💡 **고급 편집 도구 사용 예제**

### 1. 라인 범위 교체
```python
# 10-15번 라인을 새 내용으로 교체
replace_line_range(path="file.py", start_line=10, end_line=15, content="새로운 코드")
```

### 2. 정규식 교체
```python
# 모든 TODO 주석을 DONE으로 변경
regex_replace(path="file.py", pattern=r"# TODO:(.*)", replacement="# DONE:\\1", flags="i")
```

### 3. 배치 편집
```python
# 여러 편집 작업을 한 번에
patch_apply(path="file.py", operations=[
    {"type": "replace", "start": 1, "end": 2, "content": "새 헤더"},
    {"type": "insert", "start": 10, "content": "새 라인"},
    {"type": "delete", "start": 20, "end": 25}
])
```

### 4. 스마트 들여쓰기
```python
# 10-20번 라인의 들여쓰기를 2레벨 증가
smart_indent(path="file.py", start_line=10, end_line=20, indent_change=2)
```

## 🔧 **설정**

`config.py`에서 허용된 디렉토리와 기본 설정을 관리할 수 있습니다.

---

**이제 더 강력하고 효율적인 파일 편집이 가능합니다!** 🎉
