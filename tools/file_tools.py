"""
MCP 도구들의 실제 구현
파일 작업, 토큰 효율적인 도구들, 파일 수정 도구들
"""

import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from collections import Counter
from typing import Dict, Any
import pathlib

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
    """디렉토리 생성 도구"""
    path_str = arguments.get("path", "")
    if not path_str:
        raise ValueError("Path argument is required")

    path = normalize_path(path_str)
    path.mkdir(parents=True, exist_ok=True)
    return f"Successfully created directory: {path}"


async def handle_list_allowed_directories(arguments: Dict[str, Any]) -> str:
    """허용된 디렉토리 목록 도구"""
    from utils import ALLOWED_DIRECTORIES
    dirs_text = "\n".join(f"• {dir}" for dir in ALLOWED_DIRECTORIES)
    return f"Allowed directories ({len(ALLOWED_DIRECTORIES)}):\n{dirs_text}"


async def handle_file_exists(arguments: Dict[str, Any]) -> str:
    """파일 존재 확인 도구"""
    path_str = arguments.get("path", "")
    path = normalize_path(path_str)
    return "Yes" if path.exists() else "No"


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


async def handle_git_status_summary(arguments: Dict[str, Any]) -> str:
    """Git 상태 요약 도구"""
    path_str = arguments.get("path", "")
    dir_path = normalize_path(path_str)

    git_dir = dir_path / ".git"
    if not git_dir.exists():
        return "Not a git repository"

    try:
        # git status --porcelain으로 간단한 상태만
        result_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=dir_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result_proc.returncode == 0:
            lines = result_proc.stdout.strip().split('\n') if result_proc.stdout.strip() else []
            if not lines:
                return "Clean (no changes)"
            else:
                modified = len([l for l in lines if l.startswith(' M')])
                added = len([l for l in lines if l.startswith('A')])
                untracked = len([l for l in lines if l.startswith('??')])
                return f"Modified: {modified}, Added: {added}, Untracked: {untracked}"
        else:
            return "Git error"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "Git not available"
    except Exception:
        return "Git command failed"


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

    # 타임스탬프로 백업 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}.backup_{timestamp}{path.suffix}"
    backup_path = path.parent / backup_name

    shutil.copy2(path, backup_path)

    size = backup_path.stat().st_size
    return f"Backup created: {backup_name} ({size} bytes)"


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


async def handle_execute_command(arguments: Dict[str, Any]) -> str:
    """시스템 명령어 실행 도구"""
    command = arguments.get("command", "")
    timeout = arguments.get("timeout", 30)

    if not command:
        raise ValueError("Command is required")

    try:
        result_proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()  # 현재 작업 디렉토리에서 실행
        )

        if result_proc.returncode == 0:
            output = result_proc.stdout.strip()
            if len(output) > 500:  # 긴 출력은 잘라내기
                output = output[:500] + "... (truncated)"
            return f"✅ Command succeeded:\n{output}"
        else:
            error = result_proc.stderr.strip()[:200]  # 에러도 제한
            return f"❌ Command failed (code {result_proc.returncode}):\n{error}"

    except subprocess.TimeoutExpired:
        return f"❌ Command timed out after {timeout}s"
    except Exception as e:
        return f"❌ Command error: {str(e)}"


async def handle_find_and_replace(arguments: Dict[str, Any]) -> str:
    """찾기 및 바꾸기 도구"""
    path_str = arguments.get("path", "")
    find_text = arguments.get("find", "")
    replace_text = arguments.get("replace", "")
    max_count = arguments.get("count", 0)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 파일을 스트리밍으로 처리 (메모리 효율적)
    replacements = 0
    with path.open('r', encoding='utf-8') as infile, \
            tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as outfile:

        for line in infile:
            if max_count == 0 or replacements < max_count:
                new_line = line.replace(find_text, replace_text)
                if new_line != line:
                    replacements += new_line.count(replace_text) - line.count(replace_text)
                outfile.write(new_line)
            else:
                outfile.write(line)

        temp_path = outfile.name

    # 원본 파일 교체
    shutil.move(temp_path, path)

    return f"Replaced '{find_text}' → '{replace_text}' ({replacements} times)"


async def handle_insert_line(arguments: Dict[str, Any]) -> str:
    """라인 삽입 도구"""
    path_str = arguments.get("path", "")
    line_number = arguments.get("line_number", 1)
    content = arguments.get("content", "")

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    lines = path.read_text(encoding='utf-8').splitlines()

    # 1-based에서 0-based로 변환
    insert_index = line_number - 1
    if insert_index < 0:
        insert_index = 0
    elif insert_index > len(lines):
        insert_index = len(lines)

    lines.insert(insert_index, content)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    return f"Inserted line at {line_number}: '{content[:50]}...'"


async def handle_append_to_file(arguments: Dict[str, Any]) -> str:
    """파일에 추가 도구"""
    path_str = arguments.get("path", "")
    content = arguments.get("content", "")

    path = normalize_path(path_str)

    # 파일 끝에 추가 (메모리 효율적)
    with path.open('a', encoding='utf-8') as f:
        if not content.endswith('\n'):
            content += '\n'
        f.write(content)

    return f"Appended {len(content)} characters to file"


async def handle_get_file_section(arguments: Dict[str, Any]) -> str:
    """파일 섹션 읽기 도구"""
    path_str = arguments.get("path", "")
    start_line = arguments.get("start_line", 1)
    end_line = arguments.get("end_line", start_line)
    context = arguments.get("context", 0)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    lines = path.read_text(encoding='utf-8').splitlines()

    # 컨텍스트 적용
    start_idx = max(0, start_line - 1 - context)
    end_idx = min(len(lines), end_line + context)

    selected_lines = lines[start_idx:end_idx]

    # 라인 번호와 함께 출력
    result_lines = []
    for i, line in enumerate(selected_lines, start=start_idx + 1):
        marker = ">>> " if start_line <= i <= end_line else "    "
        result_lines.append(f"{marker}{i:3d}: {line}")

    return "\n".join(result_lines)


# 도구 핸들러 매핑
TOOL_HANDLERS = {
    "read_file": handle_read_file,
    "write_file": handle_write_file,
    "list_directory": handle_list_directory,
    "create_directory": handle_create_directory,
    "list_allowed_directories": handle_list_allowed_directories,
    "file_exists": handle_file_exists,
    "count_files": handle_count_files,
    "get_directory_size": handle_get_directory_size,
    "get_recent_files": handle_get_recent_files,
    "analyze_project": handle_analyze_project,
    "git_status_summary": handle_git_status_summary,
    "copy_file": handle_copy_file,
    "move_file": handle_move_file,
    "delete_file": handle_delete_file,
    "backup_file": handle_backup_file,
    "file_info": handle_file_info,
    "execute_command": handle_execute_command,
    "find_and_replace": handle_find_and_replace,
    "insert_line": handle_insert_line,
    "append_to_file": handle_append_to_file,
    "get_file_section": handle_get_file_section,
}
