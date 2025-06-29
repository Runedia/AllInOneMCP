"""
서버 설정
"""

# 허용된 디렉토리 목록
import os
import pathlib

RAW_ALLOWED_DIRECTORIES = [
    r"C:\Project",
]


def normalize_path(path):
    return str(pathlib.Path(os.path.expanduser(path)).resolve())


ALLOWED_DIRECTORIES = [normalize_path(p) for p in RAW_ALLOWED_DIRECTORIES]

# 서버 설정
SERVER_VERSION = "20250629.3"
SERVER_VERSION = "20250630.1"
SERVER_NAME = "nexus-fs"
