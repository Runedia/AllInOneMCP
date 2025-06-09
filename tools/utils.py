"""
공통 유틸리티 함수들
경로 정규화, 파일 인코딩 감지 등
"""

import os
import pathlib
import sys

# Windows 호환성
try:
    import chardet

    print("[DEBUG] chardet imported successfully", file=sys.stderr)
except ImportError:
    chardet = None
    print("[DEBUG] chardet not available", file=sys.stderr)

if os.name == 'nt':
    try:
        import win32_stat

        print("[DEBUG] win32_stat imported successfully", file=sys.stderr)
    except ImportError:
        win32_stat = None
        print("[DEBUG] win32_stat not available", file=sys.stderr)

# 설정 import
try:
    from config import ALLOWED_DIRECTORIES

    print(f"[DEBUG] Config loaded: {ALLOWED_DIRECTORIES}", file=sys.stderr)
except ImportError:
    ALLOWED_DIRECTORIES = [
        "C:\\",
    ]
    print(f"[DEBUG] Using default config", file=sys.stderr)


def normalize_path(requested_path: str) -> pathlib.Path:
    """경로 정규화 및 권한 확인"""
    try:
        requested = pathlib.Path(os.path.expanduser(requested_path)).resolve()

        if os.name == 'nt' and len(str(requested)) > 260:
            raise ValueError(f"Path too long for Windows: {len(str(requested))} characters")

        for allowed in ALLOWED_DIRECTORIES:
            if str(requested).lower().startswith(allowed.lower()):
                return requested

        raise PermissionError(f"Access denied: {requested} not in allowed directories")
    except Exception as e:
        print(f"[DEBUG] Path error: {e}", file=sys.stderr)
        raise


def detect_file_encoding(file_path: pathlib.Path) -> str:
    """파일 인코딩 감지"""
    if not chardet:
        return "utf-8"

    try:
        with file_path.open("rb") as f:
            raw_data = f.read(8192)
            if not raw_data:
                return "utf-8"

            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)

            if confidence < 0.7 or not encoding:
                common_encodings = ['utf-8', 'cp949', 'euc-kr', 'cp1252', 'latin1']
                for enc in common_encodings:
                    try:
                        with file_path.open("r", encoding=enc) as test_f:
                            test_f.read(1024)
                        return enc
                    except (UnicodeDecodeError, LookupError):
                        continue
                return "utf-8"

            return encoding
    except Exception:
        return "utf-8"
