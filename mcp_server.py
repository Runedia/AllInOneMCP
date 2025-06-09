"""
MCP 서버 설정과 도구 정의
"""

import sys
import traceback
from typing import List, Dict, Any, Sequence

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types

    MCP_AVAILABLE = True
    print("[DEBUG] MCP imports successful", file=sys.stderr)
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"[DEBUG] MCP import failed: {e}", file=sys.stderr)

from tools_registry import TOOL_HANDLERS


def create_mcp_server():
    """MCP 서버 생성"""
    if not MCP_AVAILABLE:
        return None

    print("[DEBUG] Creating MCP server", file=sys.stderr)
    server = Server("hybrid-filesystem")

    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """MCP 도구 목록 반환"""
        print("[DEBUG] MCP list_tools called", file=sys.stderr)
        return get_tool_definitions()

    @server.call_tool()
    async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
    ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """MCP 도구 호출 처리"""
        print(f"[DEBUG] MCP tool called: {name} with args: {arguments}", file=sys.stderr)

        try:
            if name in TOOL_HANDLERS:
                result = await TOOL_HANDLERS[name](arguments)
                return [types.TextContent(type="text", text=result)]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = f"Error executing {name}: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            return [types.TextContent(type="text", text=error_msg)]

    return server


def get_tool_definitions() -> List[types.Tool]:
    """모든 도구 정의 반환"""
    return [
        # 기존 도구들
        types.Tool(
            name="read_file",
            description="Read the contents of a file with automatic encoding detection",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_directory",
            description="List directory contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="create_directory",
            description="Create a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to create"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_allowed_directories",
            description="List all allowed directories",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        ),
        # 토큰 효율적인 도구들
        types.Tool(
            name="file_exists",
            description="Check if a file or directory exists (very token efficient - returns Yes/No)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to check"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="count_files",
            description="Count files in directory by extension (token efficient summary)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"},
                    "extension": {"type": "string", "description": "File extension (optional)"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_directory_size",
            description="Get total size of directory (compact size summary)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_recent_files",
            description="Get most recently modified files (small list)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"},
                    "limit": {"type": "integer", "description": "Max files to return (default: 5)", "default": 5}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="analyze_project",
            description="Analyze project structure and file types (compact overview)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Project directory path"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="git_status_summary",
            description="Get brief git status summary (very compact)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repository path"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        # OS 명령어 기반 도구들
        types.Tool(
            name="copy_file",
            description="Copy a file (very token efficient - uses OS commands)",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source file path"},
                    "destination": {"type": "string", "description": "Destination file path"}
                },
                "required": ["source", "destination"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="move_file",
            description="Move or rename a file (token efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source file path"},
                    "destination": {"type": "string", "description": "Destination file path"}
                },
                "required": ["source", "destination"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="delete_file",
            description="Delete a file (token efficient - simple confirmation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to delete"},
                    "force": {"type": "boolean", "description": "Skip confirmation", "default": False}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="backup_file",
            description="Create a backup copy with timestamp (very token efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to backup"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="file_info",
            description="Get file info without reading contents (very token efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to check"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="execute_command",
            description="Execute system command (token efficient for file operations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                },
                "required": ["command"],
                "additionalProperties": False
            }
        ),
        # 파일 수정 도구들
        types.Tool(
            name="find_and_replace",
            description="Find and replace text in file (very token efficient - no full file reading)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "find": {"type": "string", "description": "Text to find"},
                    "replace": {"type": "string", "description": "Text to replace with"},
                    "count": {"type": "integer", "description": "Max replacements (0 = all)", "default": 0}
                },
                "required": ["path", "find", "replace"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="insert_line",
            description="Insert line at specific position (token efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "line_number": {"type": "integer", "description": "Line number to insert at (1-based)"},
                    "content": {"type": "string", "description": "Content to insert"}
                },
                "required": ["path", "line_number", "content"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="append_to_file",
            description="Append content to end of file (very token efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "content": {"type": "string", "description": "Content to append"}
                },
                "required": ["path", "content"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_file_section",
            description="Get specific lines from file (token efficient reading)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                    "start_line": {"type": "integer", "description": "Start line number (1-based)"},
                    "end_line": {"type": "integer", "description": "End line number (1-based, optional)"},
                    "context": {"type": "integer", "description": "Extra context lines around", "default": 0}
                },
                "required": ["path", "start_line"],
                "additionalProperties": False
            }
        ),
        # 🆕 고급 편집 도구들
        types.Tool(
            name="count_occurrences",
            description="Count occurrences of text in file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to search"},
                    "search_text": {"type": "string", "description": "Text to search for"},
                    "case_sensitive": {"type": "boolean", "description": "Case sensitive search", "default": True}
                },
                "required": ["path", "search_text"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="replace_line_range",
            description="Replace a range of lines with new content (memory efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "start_line": {"type": "integer", "description": "Start line number (1-based)"},
                    "end_line": {"type": "integer", "description": "End line number (1-based)"},
                    "content": {"type": "string", "description": "New content to replace with"}
                },
                "required": ["path", "start_line", "end_line", "content"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="delete_lines",
            description="Delete specific lines from file (memory efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "start_line": {"type": "integer", "description": "Start line number (1-based)"},
                    "end_line": {"type": "integer", "description": "End line number (1-based, optional)"}
                },
                "required": ["path", "start_line"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="regex_replace",
            description="Advanced find/replace using regular expressions",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "pattern": {"type": "string", "description": "Regular expression pattern"},
                    "replacement": {"type": "string", "description": "Replacement text (can use $1, $2 for groups)"},
                    "flags": {"type": "string", "description": "Regex flags (i=ignorecase, m=multiline, s=dotall)",
                              "default": ""},
                    "count": {"type": "integer", "description": "Max replacements (0 = all)", "default": 0}
                },
                "required": ["path", "pattern", "replacement"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="smart_indent",
            description="Smart indentation adjustment for code",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "start_line": {"type": "integer", "description": "Start line number (1-based)"},
                    "end_line": {"type": "integer", "description": "End line number (1-based)"},
                    "indent_change": {"type": "integer",
                                      "description": "Indent levels to add (positive) or remove (negative)"},
                    "use_tabs": {"type": "boolean", "description": "Use tabs instead of spaces", "default": False}
                },
                "required": ["path", "start_line", "end_line", "indent_change"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="patch_apply",
            description="Apply multiple edit operations in batch (very efficient)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to modify"},
                    "operations": {
                        "type": "array",
                        "description": "List of operations to apply",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["replace", "insert", "delete"]},
                                "start": {"type": "integer", "description": "Start line (1-based)"},
                                "end": {"type": "integer", "description": "End line (1-based, for replace/delete)"},
                                "content": {"type": "string", "description": "Content for replace/insert operations"}
                            },
                            "required": ["type", "start"]
                        }
                    }
                },
                "required": ["path", "operations"],
                "additionalProperties": False
            }
        )
    ]


async def run_mcp_server():
    """MCP 서버 실행"""
    if not MCP_AVAILABLE:
        print("[ERROR] MCP not available, cannot run MCP server", file=sys.stderr)
        return

    server = create_mcp_server()
    if not server:
        print("[ERROR] Failed to create MCP server", file=sys.stderr)
        return

    print("[DEBUG] Starting MCP server", file=sys.stderr)

    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            print("[DEBUG] MCP server running", file=sys.stderr)

            # MCP 라이브러리 버전 호환성을 위한 capabilities 처리
            try:
                # 간단한 객체 생성 - tools_changed 속성이 있는 객체
                class SimpleNotificationOptions:
                    def __init__(self):
                        self.tools_changed = None
                        self.resources_changed = None
                        self.prompts_changed = None

                notification_options = SimpleNotificationOptions()
                capabilities = server.get_capabilities(notification_options, {})
                print("[DEBUG] Capabilities created with custom notification options", file=sys.stderr)
            except Exception as e:
                print(f"[DEBUG] Failed to create capabilities: {e}", file=sys.stderr)
                # 가장 기본적인 capabilities 수동 생성
                capabilities = {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                }

            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="hybrid-filesystem",
                    server_version="0.6.0",
                    capabilities=capabilities,
                ),
            )
    except Exception as e:
        print(f"[ERROR] MCP server error: {e}", file=sys.stderr)
        print(f"[ERROR] Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise
