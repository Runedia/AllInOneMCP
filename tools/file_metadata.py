"""
파일 메타데이터 관련 도구들
"""

from datetime import datetime
from typing import Dict, Any

from tools.utils import normalize_path


async def handle_file_exists(arguments: Dict[str, Any]) -> str:
    """파일 존재 확인 도구"""
    path_str = arguments.get("path", "")
    path = normalize_path(path_str)
    return "Yes" if path.exists() else "No"


async def handle_file_info(arguments: Dict[str, Any]) -> str:
    """파일 정보 도구"""
    path_str = arguments.get("path", "")
    path = normalize_path(path_str)

    if not path.exists():
        return f"Not found: {path.name}"

    stat = path.stat()
    size_kb = stat.st_size / 1024
    file_type = "directory" if path.is_dir() else "file"

    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%m-%d %H:%M")

    return f"{path.name}: {file_type}, {size_kb:.1f}KB, modified {modified}"


async def handle_files_exist(arguments: Dict[str, Any]) -> str:
    """다중 파일 존재 확인 도구"""
    paths = arguments.get("paths", [])
    if not paths:
        raise ValueError("paths argument is required")

    if not isinstance(paths, list):
        raise ValueError("paths must be a list of file paths")

    results = []
    for path_str in paths:
        try:
            path = normalize_path(path_str)
            if path.exists():
                results.append("Yes")
            else:
                results.append("No")
        except Exception:
            results.append("Error")

    return str(results)
