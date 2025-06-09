"""
모든 도구들을 통합하는 레지스트리 - 고급 편집 도구 포함
"""

# 기존 도구 핸들러들 import
from tools.file_io import (
    handle_read_file, handle_write_file, handle_copy_file,
    handle_move_file, handle_delete_file, handle_backup_file
)
from tools.directory_manager import (
    handle_list_directory, handle_create_directory, handle_list_allowed_directories,
    handle_count_files, handle_get_directory_size, handle_get_recent_files,
    handle_analyze_project
)
from tools.git_helper import handle_git_status_summary, handle_execute_command
from tools.text_processor import (
    handle_find_and_replace, handle_insert_line,
    handle_append_to_file, handle_get_file_section, handle_count_occurrences
)
from tools.file_metadata import handle_file_exists, handle_file_info

# 고급 텍스트 처리 도구들 import
from tools.advanced_text_processor import (
    handle_replace_line_range, handle_delete_lines, handle_regex_replace,
    handle_insert_at_position, handle_patch_apply, handle_smart_indent
)

# 도구 핸들러 매핑 - 기존 + 새로운 고급 도구들
TOOL_HANDLERS = {
    # 기본 파일 I/O
    "read_file": handle_read_file,
    "write_file": handle_write_file,
    "copy_file": handle_copy_file,
    "move_file": handle_move_file,
    "delete_file": handle_delete_file,
    "backup_file": handle_backup_file,

    # 디렉토리 관리
    "list_directory": handle_list_directory,
    "create_directory": handle_create_directory,
    "list_allowed_directories": handle_list_allowed_directories,
    "count_files": handle_count_files,
    "get_directory_size": handle_get_directory_size,
    "get_recent_files": handle_get_recent_files,
    "analyze_project": handle_analyze_project,

    # Git & 명령어
    "git_status_summary": handle_git_status_summary,
    "execute_command": handle_execute_command,

    # 기본 텍스트 처리
    "find_and_replace": handle_find_and_replace,
    "insert_line": handle_insert_line,
    "append_to_file": handle_append_to_file,
    "get_file_section": handle_get_file_section,
    "count_occurrences": handle_count_occurrences,

    # 파일 메타데이터
    "file_exists": handle_file_exists,
    "file_info": handle_file_info,

    # 🆕 고급 편집 도구들
    "replace_line_range": handle_replace_line_range,
    "delete_lines": handle_delete_lines,
    "regex_replace": handle_regex_replace,
    "insert_at_position": handle_insert_at_position,
    "patch_apply": handle_patch_apply,
    "smart_indent": handle_smart_indent,
}

# 도구 카테고리별 분류
TOOL_CATEGORIES = {
    "file_io": [
        "read_file", "write_file", "copy_file", "move_file", "delete_file", "backup_file"
    ],
    "directory": [
        "list_directory", "create_directory", "list_allowed_directories",
        "count_files", "get_directory_size", "get_recent_files", "analyze_project"
    ],
    "git_system": [
        "git_status_summary", "execute_command"
    ],
    "text_basic": [
        "find_and_replace", "insert_line", "append_to_file",
        "get_file_section", "count_occurrences"
    ],
    "text_advanced": [
        "replace_line_range", "delete_lines", "regex_replace",
        "insert_at_position", "patch_apply", "smart_indent"
    ],
    "metadata": [
        "file_exists", "file_info"
    ]
}


def get_tools_by_category(category: str):
    """카테고리별 도구 목록 반환"""
    return TOOL_CATEGORIES.get(category, [])


def get_all_tool_names():
    """모든 도구 이름 목록 반환"""
    return list(TOOL_HANDLERS.keys())
