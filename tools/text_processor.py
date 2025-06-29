"""
텍스트 처리 관련 도구들 - 개선된 버전
"""

import tempfile
import shutil
import os
from typing import Dict, Any

from tools.utils import normalize_path

async def handle_insert_line(arguments: Dict[str, Any]) -> str:
    """라인 삽입 도구 - 메모리 효율적 버전, 라인 수 변화 감지 포함"""
    path_str = arguments.get("path", "")
    line_number = arguments.get("line_number", 1)
    content = arguments.get("content", "")

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 📊 라인 수 변화 감지를 위한 사전 계산
    original_content = path.read_text(encoding='utf-8')
    original_total_lines = len(original_content.splitlines())
    
    # 실제 추가될 줄 수 계산 (multi-line 지원)
    if content:
        # content의 실제 줄 수 계산
        content_lines = content.split('\n')
        # 마지막이 빈 문자열이면 (즉, \n으로 끝나면) 실제 줄 수에서 1 제외
        if content_lines and content_lines[-1] == '':
            lines_to_add = len(content_lines) - 1
        else:
            lines_to_add = len(content_lines)
    else:
        lines_to_add = 1  # 빈 content라도 1줄은 추가됨
    
    line_change = lines_to_add

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

        # 📊 라인 수 변화 결과 계산
        new_total_lines = original_total_lines + line_change
        
        # 📋 상세한 변화 정보 메시지 생성
        if lines_to_add == 1:
            base_msg = f"Inserted line at {line_number}"
            change_msg = f"📈 Added 1 line - Lines {line_number + 1}+ shifted DOWN by 1"
        else:
            base_msg = f"Inserted {lines_to_add} lines at {line_number}"
            change_msg = f"📈 Added {lines_to_add} lines - Lines {line_number + lines_to_add}+ shifted DOWN by {lines_to_add}"
        total_msg = f"📊 Total lines: {original_total_lines} → {new_total_lines}"
        
        return f"{base_msg}\n{change_msg}\n{total_msg}"

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


async def handle_append_to_file(arguments: Dict[str, Any]) -> str:
    """파일에 추가 도구 - 라인 수 변화 감지 포함"""
    path_str = arguments.get("path", "")
    content = arguments.get("content", "")

    path = normalize_path(path_str)

    # 📊 라인 수 변화 감지를 위한 사전 계산
    original_content = path.read_text(encoding='utf-8')
    original_total_lines = len(original_content.splitlines())
    
    # 추가될 라인 수 계산
    lines_to_add = content.count('\n')
    if content and not content.endswith('\n'):
        lines_to_add += 1  # 마지막에 개행문자가 없으면 1줄 추가

    # 파일 끝에 추가 (메모리 효율적)
    with path.open('a', encoding='utf-8') as f:
        if not content.endswith('\n'):
            content += '\n'
        f.write(content)

    # 📊 라인 수 변화 결과 계산
    new_total_lines = original_total_lines + lines_to_add
    
    # 📋 상세한 변화 정보 메시지 생성
    base_msg = f"Appended {len(content)} characters to file"
    
    if lines_to_add == 0:
        change_msg = "✅ No new lines added"
    elif lines_to_add == 1:
        change_msg = "📈 Added 1 line at end of file"
    else:
        change_msg = f"📈 Added {lines_to_add} lines at end of file"
    
    total_msg = f"📊 Total lines: {original_total_lines} → {new_total_lines}"
    
    return f"{base_msg}\n{change_msg}\n{total_msg}"


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
