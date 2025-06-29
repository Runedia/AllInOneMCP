"""
파일 읽기/쓰기 관련 도구들
"""

import shutil
from datetime import datetime
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
    path_str = arguments.get("path", "")
    path = normalize_path(path_str)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 타임스탬프로 백업 파일의 확장자 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}.backup_{timestamp}"  # 확장자를 backup_timestamp로 변경
    backup_path = path.parent / backup_name

    shutil.copy2(path, backup_path)

    size = backup_path.stat().st_size
    return f"Backup created: {backup_name} ({size} bytes)"



async def handle_backup_files(arguments: Dict[str, Any]) -> str:
    """다중 파일 백업 도구 - 여러 파일을 동일한 타임스탬프로 백업"""
    paths = arguments.get("paths", [])
    
    if not paths:
        raise ValueError("At least one file path is required in 'paths' array")
    
    if not isinstance(paths, list):
        raise ValueError("'paths' must be an array of file paths")
    
    # 모든 경로를 정규화하고 존재하는지 확인
    normalized_paths = []
    missing_files = []
    
    for path_str in paths:
        path = normalize_path(path_str)
        if path.exists():
            normalized_paths.append(path)
        else:
            missing_files.append(str(path))
    
    if missing_files:
        raise FileNotFoundError(f"Files not found: {', '.join(missing_files)}")
    
    # 동일한 타임스탬프 생성 (백업 세트의 일관성을 위해)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 백업 수행 및 결과 추적
    successful_backups = []
    failed_backups = []
    total_size = 0
    
    for path in normalized_paths:
        try:
            backup_name = f"{path.stem}.backup_{timestamp}"
            backup_path = path.parent / backup_name
            
            # 백업 생성
            shutil.copy2(path, backup_path)
            
            # 성공 기록
            size = backup_path.stat().st_size
            total_size += size
            successful_backups.append({
                'original': path.name,
                'backup': backup_name,
                'size': size
            })
            
        except Exception as e:
            failed_backups.append({
                'file': path.name,
                'error': str(e)
            })
    
    # 결과 메시지 생성
    success_count = len(successful_backups)
    failure_count = len(failed_backups)
    
    result = f"Backup completed: {success_count} files backed up"
    
    if total_size > 0:
        # 사이즈를 읽기 쉬운 형식으로 변환
        if total_size < 1024:
            size_str = f"{total_size} bytes"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        
        result += f" ({size_str} total)"
    
    if failure_count > 0:
        result += f", {failure_count} failed"
    
    # 상세 정보 추가 (토큰 효율성을 위해 간단하게)
    if successful_backups:
        result += f"\nBackup timestamp: {timestamp}"
    
    return result
