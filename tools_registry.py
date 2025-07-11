"""
모든 도구들을 통합하는 레지스트리 - Git 도구 개선 포함
"""

from tools.git_tools import *
from tools.text_processor import *
from tools.file_metadata import *
from tools.advanced_text_processor import *
from tools.directory_manager import *
from tools.file_io import *
from tools.file_search import *
from tools.tree_sitter_analyzer import *

# 도구 핸들러 매핑 - 기존 + 새로운 Git 도구들
TOOL_HANDLERS = {
    # 기본 파일 I/O
    "read_file": handle_read_file,
    "write_file": handle_write_file,
    "copy_file": handle_copy_file,
    "move_file": handle_move_file,
    "delete_file": handle_delete_file,
    "backup_file": handle_backup_file,
    "backup_files": handle_backup_files,

    # 디렉토리 관리
    "list_directory": handle_list_directory,
    "create_directory": handle_create_directory,
    "create_directories": handle_create_directories,
    "list_allowed_directories": handle_list_allowed_directories,
    "count_files": handle_count_files,
    "get_directory_size": handle_get_directory_size,
    "get_recent_files": handle_get_recent_files,
    "analyze_project": handle_analyze_project,

    # 🆕 Git 도구들 (GitPython 기반)
    "git_status": handle_git_status,
    "git_add": handle_git_add,
    "git_commit": handle_git_commit,
    "git_push": handle_git_push,
    "git_pull": handle_git_pull,
    "git_clone": handle_git_clone,
    "git_branch": handle_git_branch,
    "git_log": handle_git_log,
    "git_init": handle_git_init,

    # 기본 텍스트 처리
    "append_to_file": handle_append_to_file,
    "get_file_section": handle_get_file_section,
    "count_occurrences": handle_count_occurrences,

    # 파일 메타데이터
    "file_exists": handle_file_exists,
    "files_exist": handle_files_exist,
    "file_info": handle_file_info,

    # 🆕 고급 편집 도구들
    "replace_line_range": handle_replace_line_range,
    "delete_lines": handle_delete_lines,
    "regex_replace": handle_regex_replace,
    "insert_at_position": handle_insert_at_position,
    "patch_apply": handle_patch_apply,
    "smart_indent": handle_smart_indent,

    # 🔍 파일 검색 도구들
    "search_in_file": handle_search_in_file,
    "search_in_directory": handle_search_in_directory,
    "regex_search": handle_regex_search,


    # 🆕 Tree-sitter 기반 함수 분석 도구들
    "find_function": handle_find_function,
    "list_functions": handle_list_functions,
    "extract_function": handle_extract_function,
    "get_function_info": handle_get_function_info,
}

# 도구 카테고리별 분류
TOOL_CATEGORIES = {
    "file_io": [
        "read_file", "write_file", "copy_file", "move_file", "delete_file", "backup_file", "backup_files"
    ],
    "directory": [
        "list_directory", "create_directory", "create_directories", "list_allowed_directories",
        "count_files", "get_directory_size", "get_recent_files", "analyze_project"
    ],
    "git": [
        "git_status", "git_add", "git_commit", "git_push", "git_pull",
        "git_clone", "git_branch", "git_log", "git_init"
    ],
    "text_basic": [
        "insert_line", "append_to_file",
        "get_file_section", "count_occurrences"
    ],
    "text_advanced": [
        "replace_line_range", "delete_lines", "regex_replace",
        "insert_at_position", "patch_apply", "smart_indent"
    ],
    "metadata": [
        "file_exists", "files_exist", "file_info"
        "file_exists", "file_info"
    ],
    "search": [
        "search_in_file", "search_in_directory", "regex_search"
    ],
    "function_analysis": [
        "find_function", "list_functions", "extract_function", "get_function_info"
    ]
}


def get_tools_by_category(category: str):
    """카테고리별 도구 목록 반환"""
    return TOOL_CATEGORIES.get(category, [])


def get_all_tool_names():
    """모든 도구 이름 목록 반환"""
    return list(TOOL_HANDLERS.keys())


def get_git_tools():
    """Git 도구 목록 반환"""
    return get_tools_by_category("git")


def is_git_tool_available():
    """Git 도구 사용 가능 여부 확인"""
    try:
        from tools.git_tools import is_git_available
        return is_git_available()
    except ImportError:
        return False
