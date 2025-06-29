"""
고급 텍스트 처리 도구들 - 더 효율적인 파일 편집
"""

import os
import tempfile
import shutil
import re
from typing import Dict, Any

from tools.utils import normalize_path


async def handle_replace_line_range(arguments: Dict[str, Any]) -> str:
    """라인 범위를 새 내용으로 교체 (메모리 효율적) - 라인 수 변화 감지 포함"""
    path_str = arguments.get("path", "")
    start_line = arguments.get("start_line", 1)
    end_line = arguments.get("end_line", start_line)
    new_content = arguments.get("content", "")

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 📊 라인 수 변화 감지를 위한 사전 계산
    original_content = path.read_text(encoding='utf-8')
    original_total_lines = len(original_content.splitlines())
    
    lines_to_remove = end_line - start_line + 1
    lines_to_add = new_content.count('\n') + 1 if new_content.strip() else 0
    line_change = lines_to_add - lines_to_remove
    
    # 스트리밍 방식으로 처리
    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)

    try:
        with path.open('r', encoding='utf-8') as infile:
            current_line = 1

            # start_line 이전 라인들 복사
            while current_line < start_line:
                line = infile.readline()
                if not line:
                    break
                temp_file.write(line)
                current_line += 1

            # 교체할 라인들 건너뛰기
            while current_line <= end_line:
                line = infile.readline()
                if not line:
                    break
                current_line += 1

            # 새 내용 삽입
            if new_content:
                if not new_content.endswith('\n'):
                    new_content += '\n'
                temp_file.write(new_content)

            # 나머지 라인들 복사
            for line in infile:
                temp_file.write(line)

        temp_file.close()
        shutil.move(temp_file.name, path)

        # 📊 라인 수 변화 결과 계산
        new_total_lines = original_total_lines + line_change
        
        # 📋 상세한 변화 정보 메시지 생성
        base_msg = f"Replaced lines {start_line}-{end_line} ({lines_to_remove} lines) with new content"
        
        if line_change == 0:
            change_msg = "✅ Line numbers unchanged"
        elif line_change > 0:
            change_msg = f"📈 Added {line_change} lines - Lines {end_line + 1}+ shifted DOWN by {line_change}"
        else:
            shift_up = abs(line_change)
            change_msg = f"📉 Removed {shift_up} lines - Lines {end_line + 1}+ shifted UP by {shift_up}"
        
        total_msg = f"📊 Total lines: {original_total_lines} → {new_total_lines}"
        
        return f"{base_msg}\n{change_msg}\n{total_msg}"

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


async def handle_delete_lines(arguments: Dict[str, Any]) -> str:
    """특정 라인들 삭제 (메모리 효율적) - 라인 수 변화 감지 포함"""
    path_str = arguments.get("path", "")
    start_line = arguments.get("start_line", 1)
    end_line = arguments.get("end_line", start_line)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 📊 라인 수 변화 감지를 위한 사전 계산
    original_content = path.read_text(encoding='utf-8')
    original_total_lines = len(original_content.splitlines())
    
    lines_to_delete = end_line - start_line + 1
    line_change = -lines_to_delete  # 항상 음수 (삭제)

    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)

    try:
        with path.open('r', encoding='utf-8') as infile:
            current_line = 1
            deleted_count = 0

            for line in infile:
                if start_line <= current_line <= end_line:
                    deleted_count += 1
                else:
                    temp_file.write(line)
                current_line += 1

        temp_file.close()
        shutil.move(temp_file.name, path)

        # 📊 라인 수 변화 결과 계산
        new_total_lines = original_total_lines + line_change
        
        # 📋 상세한 변화 정보 메시지 생성
        base_msg = f"Deleted lines {start_line}-{end_line} ({deleted_count} lines)"
        
        if deleted_count > 0:
            change_msg = f"📉 Removed {deleted_count} lines - Lines {end_line + 1}+ shifted UP by {deleted_count}"
        else:
            change_msg = "✅ No lines were deleted"
        
        total_msg = f"📊 Total lines: {original_total_lines} → {new_total_lines}"
        
        return f"{base_msg}\n{change_msg}\n{total_msg}"

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


async def handle_regex_replace(arguments: Dict[str, Any]) -> str:
    """정규식을 사용한 고급 찾기/바꾸기"""
    path_str = arguments.get("path", "")
    pattern = arguments.get("pattern", "")
    replacement = arguments.get("replacement", "")
    flags_str = arguments.get("flags", "")  # "i" for ignorecase, "m" for multiline
    max_count = arguments.get("count", 0)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 플래그 처리
    flags = 0
    if 'i' in flags_str.lower():
        flags |= re.IGNORECASE
    if 'm' in flags_str.lower():
        flags |= re.MULTILINE
    if 's' in flags_str.lower():
        flags |= re.DOTALL

    try:
        pattern_obj = re.compile(pattern, flags)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

    temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
    replacements = 0

    try:
        with path.open('r', encoding='utf-8') as infile:
            for line in infile:
                if max_count == 0 or replacements < max_count:
                    new_line, count = pattern_obj.subn(replacement, line)
                    replacements += count
                    temp_file.write(new_line)
                else:
                    temp_file.write(line)

        temp_file.close()
        shutil.move(temp_file.name, path)

        return f"Regex replaced '{pattern}' → '{replacement}' ({replacements} times)"

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


async def handle_insert_at_position(arguments: Dict[str, Any]) -> str:
    """특정 문자 위치에 텍스트 삽입 (큰 파일에 적합)"""
    path_str = arguments.get("path", "")
    position = arguments.get("position", 0)  # 바이트 위치
    content = arguments.get("content", "")

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    file_size = path.stat().st_size
    if position > file_size:
        position = file_size

    temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False)

    try:
        with path.open('rb') as infile:
            # position까지 복사
            if position > 0:
                temp_file.write(infile.read(position))

            # 새 내용 삽입
            temp_file.write(content.encode('utf-8'))

            # 나머지 복사
            temp_file.write(infile.read())

        temp_file.close()
        shutil.move(temp_file.name, path)

        return f"Inserted {len(content)} characters at position {position}"

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e



async def handle_patch_apply(arguments: Dict[str, Any]) -> str:
    """단일 편집 작업만 처리 (안전한 개별 처리 방식)"""
    path_str = arguments.get("path", "")
    
    # ⚠️ operations 배열 사용 시 에러 발생
    if "operations" in arguments:
        operations = arguments.get("operations", [])
        if isinstance(operations, list) and len(operations) > 1:
            error_msg = (
                "🚨 Multiple operations are no longer supported for safety reasons.\n\n"
                "💡 Please use individual patch_apply calls instead:\n"
                "   ❌ patch_apply({\"operations\": [{\"type\": \"replace\", ...}, {\"type\": \"delete\", ...}]})\n"
                "   ✅ patch_apply({\"type\": \"replace\", \"start\": 10, \"content\": \"...\"})\n"
                "   ✅ patch_apply({\"type\": \"delete\", \"start\": 15})\n\n"
                "📈 Benefits: Predictable results, safer editing, easier debugging\n"
                f"📊 Your request has {len(operations)} operations - please split into {len(operations)} separate calls"
            )
            raise ValueError(error_msg)
        elif isinstance(operations, list) and len(operations) == 1:
            # 단일 operation이 배열로 감싸진 경우 - 자동으로 추출
            operation = operations[0]
        else:
            raise ValueError("Invalid operations format")
    else:
        # 개별 파라미터로 operation 구성
        operation = {
            "type": arguments.get("type"),
            "start": arguments.get("start"),
            "end": arguments.get("end"),
            "content": arguments.get("content", "")
        }

    # 파라미터 검증
    op_type = operation.get("type", "")
    if not op_type:
        raise ValueError("Missing required parameter: 'type' (must be 'replace', 'insert', or 'delete')")
    
    if op_type not in ["replace", "insert", "delete"]:
        raise ValueError(f"Invalid operation type '{op_type}'. Must be 'replace', 'insert', or 'delete'")
    
    start = operation.get("start")
    if start is None or not isinstance(start, int) or start < 1:
        raise ValueError("Missing or invalid 'start' parameter. Must be positive integer >= 1")

    # 파일 처리
    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 📊 파일 상태 확인
    original_content = path.read_text(encoding='utf-8')
    original_total_lines = len(original_content.splitlines())
    
    if start > original_total_lines + 1:  # insert는 마지막 라인 + 1까지 허용
        raise ValueError(f"Start line {start} exceeds file length ({original_total_lines})")

    lines = original_content.splitlines()
    start_idx = start - 1  # 0-based로 변환
    content = operation.get("content", "")

    # Operation별 처리
    if op_type == "replace":
        end = operation.get("end", start)
        if not isinstance(end, int) or end < start or end > original_total_lines:
            raise ValueError(f"Invalid end line number. Must be >= start ({start}) and <= {original_total_lines}")
        
        end_idx = end - 1
        content_lines = content.splitlines() if content else []
        replaced_count = end - start + 1
        lines[start_idx:end_idx + 1] = content_lines
        
        detail = f"Replace lines {start}-{end} ({replaced_count} → {len(content_lines)} lines)"
        line_change = len(content_lines) - replaced_count
        
    elif op_type == "insert":
        content_lines = content.splitlines() if content else [""]
        for i, line in enumerate(content_lines):
            lines.insert(start_idx + i, line)
        
        detail = f"Insert {len(content_lines)} lines at position {start}"
        line_change = len(content_lines)
        
    elif op_type == "delete":
        end = operation.get("end", start)
        if not isinstance(end, int) or end < start or end > original_total_lines:
            raise ValueError(f"Invalid end line number. Must be >= start ({start}) and <= {original_total_lines}")
        
        end_idx = end - 1
        deleted_count = end - start + 1
        del lines[start_idx:end_idx + 1]
        
        detail = f"Delete lines {start}-{end} ({deleted_count} lines)"
        line_change = -deleted_count

    # 📁 파일 저장
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    
    # 📊 결과 리포트
    new_total_lines = original_total_lines + line_change
    
    if line_change == 0:
        change_msg = "✅ Line numbers unchanged"
    elif line_change > 0:
        change_msg = f"📈 Added {line_change} lines"
    else:
        change_msg = f"📉 Removed {abs(line_change)} lines"
    
    return f"✅ {detail}\n{change_msg}\n📊 Total lines: {original_total_lines} → {new_total_lines}"


async def handle_smart_indent(arguments: Dict[str, Any]) -> str:
    """스마트 들여쓰기 조정"""
    path_str = arguments.get("path", "")
    start_line = arguments.get("start_line", 1)
    end_line = arguments.get("end_line", start_line)
    indent_change = arguments.get("indent_change", 0)  # 양수면 들여쓰기 증가, 음수면 감소
    use_tabs = arguments.get("use_tabs", False)

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    indent_str = '\t' if use_tabs else '    '

    lines = path.read_text(encoding='utf-8').splitlines()
    modified_lines = 0

    for i in range(start_line - 1, min(end_line, len(lines))):
        line = lines[i]
        if line.strip():  # 빈 라인이 아닌 경우만
            if indent_change > 0:
                lines[i] = indent_str * indent_change + line
                modified_lines += 1
            elif indent_change < 0:
                # 들여쓰기 제거
                for _ in range(abs(indent_change)):
                    if line.startswith(indent_str):
                        line = line[len(indent_str):]
                    elif line.startswith(' '):
                        line = line[1:]
                    elif line.startswith('\t'):
                        line = line[1:]
                lines[i] = line
                modified_lines += 1

    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    action = "increased" if indent_change > 0 else "decreased"
    return f"Indentation {action} for {modified_lines} lines"
