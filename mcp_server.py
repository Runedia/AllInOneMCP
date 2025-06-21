"""
MCP 서버 설정과 도구 정의
"""

import sys
import traceback
import json
import os
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
                # result가 dict인 경우 적절한 텍스트로 변환
                if isinstance(result, dict):
                    if 'formatted_results' in result:
                        # 검색 결과의 경우 formatted_results 사용
                        text_result = result['formatted_results']
                    else:
                        # 기타 경우 JSON으로 변환
                        text_result = json.dumps(result, ensure_ascii=False, indent=2)
                else:
                    text_result = str(result)
                
                return [types.TextContent(type="text", text=text_result)]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            error_msg = f"Error executing {name}: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            return [types.TextContent(type="text", text=error_msg)]

    return server


def get_tool_definitions() -> List[types.Tool]:
    """JSON 파일에서 도구 정의를 로드하여 types.Tool 객체로 변환"""
    try:
        # 현재 스크립트와 같은 디렉토리의 tools.json 파일 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tools_json_path = os.path.join(current_dir, 'tools.json')

        # JSON 파일 읽기
        with open(tools_json_path, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)

        # JSON 데이터를 types.Tool 객체로 변환
        tools = []
        for tool_data in tools_data:
            tool = types.Tool(
                name=tool_data['name'],
                description=tool_data['description'],
                inputSchema=tool_data['inputSchema']
            )
            tools.append(tool)

        print(f"[DEBUG] Loaded {len(tools)} tools from tools.json", file=sys.stderr)
        return tools

    except FileNotFoundError:
        print(f"[ERROR] tools.json file not found at {tools_json_path}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in tools.json: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[ERROR] Error loading tools from JSON: {e}", file=sys.stderr)
        return []


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
