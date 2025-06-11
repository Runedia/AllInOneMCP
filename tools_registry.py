"""
모든 도구들을 통합하는 레지스트리 - Git 도구 개선 포함
"""

from tools.command_executor import *
from tools.git_tools import *
from tools.text_processor import *
from tools.file_metadata import *
from tools.advanced_text_processor import *
from tools.tool_guide_handler import *
from tools.directory_manager import *
from tools.file_io import *

# 도구 핸들러 매핑 - 기존 + 새로운 Git 도구들
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

    # 🆕 명령어 실행 (Git 명령어 차단)
    "execute_command": handle_execute_command,

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

    # 🎯 도구 추천 시스템
    "tool_guide": handle_tool_guide,
    "tool_comparison": handle_tool_comparison,
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
    "system": [
        "execute_command"
    ],
    "git": [
        "git_status", "git_add", "git_commit", "git_push", "git_pull",
        "git_clone", "git_branch", "git_log", "git_init"
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
    ],
    "guidance": [
        "tool_guide", "tool_comparison"
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
