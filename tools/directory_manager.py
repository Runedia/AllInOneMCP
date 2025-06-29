"""
디렉토리 관리 관련 도구들
"""

from datetime import datetime
from collections import Counter
from typing import Dict, Any

from tools.utils import normalize_path


async def handle_list_directory(arguments: Dict[str, Any]) -> str:
    """디렉토리 목록 도구"""
    path_str = arguments.get("path", "")
    if not path_str:
        raise ValueError("Path argument is required")

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    items = []
    for item in sorted(path.iterdir()):
        item_type = "directory" if item.is_dir() else "file"
        size = ""
        if item.is_file():
            try:
                size = f" ({item.stat().st_size} bytes)"
            except:
                pass
        items.append(f"[{item_type.upper()}] {item.name}{size}")

    if not items:
        return "Directory is empty"
    else:
        return f"Directory contents ({len(items)} items):\n" + "\n".join(items)


async def handle_create_directory(arguments: Dict[str, Any]) -> str:
    """디렉토리 생성 도구 (부모 디렉토리도 자동 생성)"""
    path_str = arguments.get("path", "")
    if not path_str:
        raise ValueError("Path argument is required")

    path = normalize_path(path_str)
    path.mkdir(parents=True, exist_ok=True)
    return f"Successfully created directory: {path}"

async def handle_create_directory_multiple(arguments: Dict[str, Any]) -> str:
    """다중 디렉토리 생성 도구 (부모 디렉토리도 자동 생성)"""
    paths = arguments.get("paths", [])
    if not paths:
        raise ValueError("Paths argument is required")
    
    if not isinstance(paths, list):
        raise ValueError("Paths must be a list of strings")
    
    created_dirs = []
    errors = []
    
    for path_str in paths:
        try:
            if not path_str or not isinstance(path_str, str):
                errors.append(f"Invalid path: {path_str}")
                continue
                
            path = normalize_path(path_str)
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(path))
        except Exception as e:
            errors.append(f"Failed to create {path_str}: {str(e)}")
    
    result = f"Successfully created {len(created_dirs)} directories"
    if created_dirs:
        result += ":\n" + "\n".join(f"• {dir}" for dir in created_dirs)
    
    if errors:
        result += "\n\nErrors encountered:\n" + "\n".join(f"• {error}" for error in errors)
    
    return result


async def handle_list_allowed_directories(arguments: Dict[str, Any]) -> str:
    """허용된 디렉토리 목록 도구"""
    from .utils import ALLOWED_DIRECTORIES
    dirs_text = "\n".join(f"• {dir}" for dir in ALLOWED_DIRECTORIES)
    return f"Allowed directories ({len(ALLOWED_DIRECTORIES)}):\n{dirs_text}"


async def handle_count_files(arguments: Dict[str, Any]) -> str:
    """파일 개수 세기 도구"""
    path_str = arguments.get("path", "")
    extension = arguments.get("extension", "")

    dir_path = normalize_path(path_str)
    if not dir_path.is_dir():
        raise ValueError("Path is not a directory")

    if extension:
        count = len(list(dir_path.glob(f"*.{extension.lstrip('.')}")))
        return f"{extension}: {count} files"
    else:
        extensions = Counter()
        for file in dir_path.rglob("*"):
            if file.is_file():
                ext = file.suffix.lower() or "no extension"
                extensions[ext] += 1

        top_5 = extensions.most_common(5)
        result = f"Total: {sum(extensions.values())} files\n"
        result += "\n".join([f"{ext}: {count}" for ext, count in top_5])
        return result


async def handle_get_directory_size(arguments: Dict[str, Any]) -> str:
    """디렉토리 크기 도구"""
    path_str = arguments.get("path", "")
    dir_path = normalize_path(path_str)

    total_size = 0
    file_count = 0
    for file in dir_path.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size
            file_count += 1

    size_mb = total_size / (1024 * 1024)
    return f"Total: {size_mb:.1f} MB ({file_count} files)"


async def handle_get_recent_files(arguments: Dict[str, Any]) -> str:
    """최근 파일 목록 도구"""
    path_str = arguments.get("path", "")
    limit = arguments.get("limit", 5)

    dir_path = normalize_path(path_str)
    files = []
    for file in dir_path.rglob("*"):
        if file.is_file():
            files.append((file, file.stat().st_mtime))

    # 최근 수정된 파일들 정렬
    recent_files = sorted(files, key=lambda x: x[1], reverse=True)[:limit]

    result = f"Recent files (last {limit}):\n"
    for file, mtime in recent_files:
        date_str = datetime.fromtimestamp(mtime).strftime("%m-%d %H:%M")
        result += f"• {file.name} ({date_str})\n"

    return result.strip()


async def handle_analyze_project(arguments: Dict[str, Any]) -> str:
    """프로젝트 분석 도구"""
    path_str = arguments.get("path", "")
    dir_path = normalize_path(path_str)

    extensions = Counter()
    total_size = 0

    for file in dir_path.rglob("*"):
        if file.is_file():
            ext = file.suffix.lower() or "no ext"
            extensions[ext] += 1
            total_size += file.stat().st_size

    top_types = extensions.most_common(3)
    size_mb = total_size / (1024 * 1024)

    result = f"Project: {dir_path.name}\n"
    result += f"Size: {size_mb:.1f} MB\n"
    result += f"Files: {sum(extensions.values())}\n"
    result += "Types: " + ", ".join([f"{ext}({count})" for ext, count in top_types])

    return result
