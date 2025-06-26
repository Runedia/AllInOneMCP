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
    """여러 편집 작업을 한 번에 적용 (배치 처리) - 개선된 버전"""
    path_str = arguments.get("path", "")
    operations = arguments.get("operations", [])  # [{"type": "replace", "start": 1, "end": 2, "content": "new"}]

    path = normalize_path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not operations:
        return "No operations provided"

    # 📊 라인 수 변화 감지를 위한 사전 계산
    original_content = path.read_text(encoding='utf-8')
    original_total_lines = len(original_content.splitlines())
    
    # 입력 검증
    for i, op in enumerate(operations):
        op_type = op.get("type", "")
        if op_type not in ["replace", "insert", "delete"]:
            raise ValueError(f"Operation {i}: Invalid type '{op_type}'. Must be 'replace', 'insert', or 'delete'")
        
        start = op.get("start")
        if start is None or not isinstance(start, int) or start < 1:
            raise ValueError(f"Operation {i}: Invalid start line number. Must be positive integer >= 1")
        
        if start > original_total_lines + 1:  # insert는 마지막 라인 + 1까지 허용
            raise ValueError(f"Operation {i}: Start line {start} exceeds file length ({original_total_lines})")
        
        if op_type in ["replace", "delete"]:
            end = op.get("end", start)  # 기본값은 start와 같음 (한 줄만)
            if not isinstance(end, int) or end < start:
                raise ValueError(f"Operation {i}: Invalid end line number. Must be >= start ({start})")
            if end > original_total_lines:
                raise ValueError(f"Operation {i}: End line {end} exceeds file length ({original_total_lines})")

    # 라인 번호 기준으로 역순 정렬 (뒤부터 수정해야 라인 번호가 안 바뀜)
    sorted_ops = sorted(operations, key=lambda x: x.get("start", 0), reverse=True)

    lines = original_content.splitlines()
    applied_ops = 0
    operation_details = []

    for op in sorted_ops:
        op_type = op.get("type", "")
        start = op.get("start", 1) - 1  # 0-based로 변환
        content = op.get("content", "")
        
        try:
            if op_type == "replace":
                end = op.get("end", start + 2) - 1  # 1-based end를 0-based로 변환
                
                # content를 라인별로 분할 (빈 content면 빈 리스트)
                if content:
                    content_lines = content.splitlines()
                else:
                    content_lines = []
                
                # 기존 라인들을 새 content로 교체
                replaced_count = end - start + 1
                lines[start:end + 1] = content_lines
                applied_ops += 1
                
                operation_details.append(f"Replace lines {start+1}-{end+1} ({replaced_count} → {len(content_lines)} lines)")
                
            elif op_type == "insert":
                # content를 라인별로 분할하여 삽입
                if content:
                    content_lines = content.splitlines()
                    # 역순으로 삽입 (여러 라인을 순서대로 삽입하기 위해)
                    for i, line in enumerate(content_lines):
                        lines.insert(start + i, line)
                    applied_ops += 1
                    operation_details.append(f"Insert {len(content_lines)} lines at position {start+1}")
                else:
                    # 빈 content인 경우 빈 라인 하나 삽입
                    lines.insert(start, "")
                    applied_ops += 1
                    operation_details.append(f"Insert empty line at position {start+1}")
                    
            elif op_type == "delete":
                end = op.get("end", start + 2) - 1  # 1-based end를 0-based로 변환
                deleted_count = end - start + 1
                del lines[start:end + 1]
                applied_ops += 1
                operation_details.append(f"Delete lines {start+1}-{end+1} ({deleted_count} lines)")
                
        except Exception as e:
            raise RuntimeError(f"Failed to apply {op_type} operation at line {start+1}: {str(e)}")

    # 파일에 쓰기
    try:
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    except Exception as e:
        raise RuntimeError(f"Failed to write file: {str(e)}")

    # 📊 라인 수 변화 결과 계산
    new_total_lines = len(lines)
    line_change = new_total_lines - original_total_lines

    # 📋 상세한 변화 정보 메시지 생성
    base_msg = f"✅ Applied {applied_ops} operations successfully"
    
    if operation_details:
        details_msg = "📝 Operations performed:\n" + "\n".join(f"  • {detail}" for detail in operation_details)
    else:
        details_msg = ""

    if line_change == 0:
        change_msg = "✅ Line numbers unchanged"
    elif line_change > 0:
        change_msg = f"📈 Added {line_change} lines total"
    else:
        change_msg = f"📉 Removed {abs(line_change)} lines total"

    total_msg = f"📊 Total lines: {original_total_lines} → {new_total_lines}"
    
    result_parts = [base_msg, details_msg, change_msg, total_msg]
    return "\n".join(part for part in result_parts if part)


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
