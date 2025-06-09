"""
텍스트 처리 관련 도구들 - 개선된 버전
"""

import tempfile
import shutil
import os
from typing import Dict, Any

from tools.utils import normalize_path


async def handle_find_and_replace(arguments: Dict[str, Any]) -> str:
    """찾기 및 바꾸기 도구 - 개선된 버전"""
    path_str = arguments.get("path", "")
    find_text = arguments.get("find", "")
    replace_text = arguments.get("replace", "")
    max_count = arguments.get("count", 0)
    case_sensitive = arguments.get("case_sensitive", True)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 대소문자 구분 옵션
    if not case_sensitive:
        # 대소문자를 무시하는 경우 정규식 사용
        import re
        pattern = re.escape(find_text)
        regex = re.compile(pattern, re.IGNORECASE)

    replacements = 0
    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)

    try:
        with path.open('r', encoding='utf-8') as infile:
            for line in infile:
                if max_count == 0 or replacements < max_count:
                    if case_sensitive:
                        if find_text in line:
                            original_count = line.count(find_text)
                            new_line = line.replace(find_text, replace_text)
                            replacements += original_count
                        else:
                            new_line = line
                    else:
                        new_line, count = regex.subn(replace_text, line)
                        replacements += count
                    temp_file.write(new_line)
                else:
                    temp_file.write(line)

        temp_file.close()
        shutil.move(temp_file.name, path)

        case_info = "" if case_sensitive else " (case-insensitive)"
        return f"Replaced '{find_text}' → '{replace_text}' ({replacements} times){case_info}"

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


async def handle_insert_line(arguments: Dict[str, Any]) -> str:
    """라인 삽입 도구 - 메모리 효율적 버전"""
    path_str = arguments.get("path", "")
    line_number = arguments.get("line_number", 1)
    content = arguments.get("content", "")

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 큰 파일을 위한 스트리밍 방식
    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)

    try:
        with path.open('r', encoding='utf-8') as infile:
            current_line = 1

            # line_number까지 복사
            while current_line < line_number:
                line = infile.readline()
                if not line:  # 파일 끝에 도달
                    break
                temp_file.write(line)
                current_line += 1

            # 새 라인 삽입
            if not content.endswith('\n'):
                content += '\n'
            temp_file.write(content)

            # 나머지 라인들 복사
            for line in infile:
                temp_file.write(line)

        temp_file.close()
        shutil.move(temp_file.name, path)

        return f"Inserted line at {line_number}: '{content[:50]}...'"

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


async def handle_append_to_file(arguments: Dict[str, Any]) -> str:
    """파일에 추가 도구 - 이미 효율적"""
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
    """파일 섹션 읽기 도구 - 큰 파일용 최적화"""
    path_str = arguments.get("path", "")
    start_line = arguments.get("start_line", 1)
    end_line = arguments.get("end_line", start_line)
    context = arguments.get("context", 0)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 컨텍스트 적용
    actual_start = max(1, start_line - context)
    actual_end = end_line + context

    result_lines = []

    # 스트리밍 방식으로 큰 파일도 효율적으로 처리
    with path.open('r', encoding='utf-8') as f:
        current_line = 1

        # actual_start까지 스킵
        while current_line < actual_start:
            f.readline()
            current_line += 1

        # 필요한 라인들만 읽기
        while current_line <= actual_end:
            line = f.readline()
            if not line:  # 파일 끝
                break

            marker = ">>> " if start_line <= current_line <= end_line else "    "
            result_lines.append(f"{marker}{current_line:3d}: {line.rstrip()}")
            current_line += 1

    return "\n".join(result_lines)


async def handle_count_occurrences(arguments: Dict[str, Any]) -> str:
    """텍스트 출현 횟수 카운트 (새로운 도구)"""
    path_str = arguments.get("path", "")
    search_text = arguments.get("search_text", "")
    case_sensitive = arguments.get("case_sensitive", True)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    total_count = 0
    line_count = 0
    matching_lines = 0

    with path.open('r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line_count += 1

            if case_sensitive:
                count_in_line = line.count(search_text)
            else:
                count_in_line = line.lower().count(search_text.lower())

            if count_in_line > 0:
                total_count += count_in_line
                matching_lines += 1

    case_info = "" if case_sensitive else " (case-insensitive)"
    return f"Found '{search_text}' {total_count} times in {matching_lines} lines (total {line_count} lines){case_info}"
