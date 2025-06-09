"""
파일 읽기/쓰기 관련 도구들
"""

import shutil
from typing import Dict, Any

from tools.utils import normalize_path, detect_file_encoding


async def handle_read_file(arguments: Dict[str, Any]) -> str:
    """파일 읽기 도구"""
    path_str = arguments.get("path", "")
    if not path_str:
        raise ValueError("Path argument is required")

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    encoding = detect_file_encoding(path)
    content = path.read_text(encoding=encoding)
    return content


async def handle_write_file(arguments: Dict[str, Any]) -> str:
    """파일 쓰기 도구"""
    path_str = arguments.get("path", "")
    content = arguments.get("content", "")

    if not path_str:
        raise ValueError("Path argument is required")

    path = normalize_path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} characters to {path}"


async def handle_copy_file(arguments: Dict[str, Any]) -> str:
    """파일 복사 도구"""
    source_str = arguments.get("source", "")
    dest_str = arguments.get("destination", "")

    source = normalize_path(source_str)
    dest = normalize_path(dest_str)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    shutil.copy2(source, dest)  # copy2는 메타데이터도 복사

    # 토큰 효율적인 출력
    size = dest.stat().st_size
    return f"Copied: {source.name} → {dest.name} ({size} bytes)"


async def handle_move_file(arguments: Dict[str, Any]) -> str:
    """파일 이동 도구"""
    source_str = arguments.get("source", "")
    dest_str = arguments.get("destination", "")

    source = normalize_path(source_str)
    dest = normalize_path(dest_str)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    shutil.move(str(source), str(dest))
    return f"Moved: {source.name} → {dest.name}"


async def handle_delete_file(arguments: Dict[str, Any]) -> str:
    """파일 삭제 도구"""
    path_str = arguments.get("path", "")
    force = arguments.get("force", False)

    path = normalize_path(path_str)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not force:
        # 간단한 확인
        return f"Delete {path.name}? Use force=true to confirm"

    if path.is_file():
        path.unlink()
        return f"Deleted: {path.name}"
    elif path.is_dir():
        shutil.rmtree(path)
        return f"Deleted directory: {path.name}"


async def handle_backup_file(arguments: Dict[str, Any]) -> str:
    """파일 백업 도구"""
    from datetime import datetime

    path_str = arguments.get("path", "")
    path = normalize_path(path_str)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 타임스탬프로 백업 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}.backup_{timestamp}{path.suffix}"
    backup_path = path.parent / backup_name

    shutil.copy2(path, backup_path)

    size = backup_path.stat().st_size
    return f"Backup created: {backup_name} ({size} bytes)"
