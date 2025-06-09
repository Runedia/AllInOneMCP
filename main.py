#!/usr/bin/env python3
"""
완전한 하이브리드 서버: FastAPI (HTTP REST) + MCP (JSON-RPC over stdio)
모듈화된 구조로 리팩토링된 버전
"""

import asyncio
import os
import sys

# uvloop 적용 (Linux/macOS에서만)
try:
    import uvloop

    if sys.platform != "win32":
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        print("[DEBUG] uvloop enabled for better performance", file=sys.stderr)
    else:
        print("[DEBUG] uvloop not available on Windows, using default asyncio", file=sys.stderr)
except ImportError:
    print("[DEBUG] uvloop not installed, using default asyncio", file=sys.stderr)

print(f"[DEBUG] Starting server with Python {sys.version}", file=sys.stderr)
print(f"[DEBUG] Working directory: {os.getcwd()}", file=sys.stderr)

# MCP 가용성 확인
try:
    from mcp.server import Server

    MCP_AVAILABLE = True
    print("[DEBUG] MCP imports successful", file=sys.stderr)
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"[DEBUG] MCP import failed: {e}", file=sys.stderr)

# 모듈 import
from tools.fastapi_routes import create_fastapi_app
from mcp_server import run_mcp_server


def run_fastapi_server():
    """FastAPI 서버 실행"""
    import uvicorn

    app = create_fastapi_app()
    print("[INFO] Starting FastAPI server on http://localhost:8000", file=sys.stderr)

    # uvloop이 사용 가능한 경우 uvicorn에서도 활용
    loop_config = {}
    try:
        import uvloop
        if sys.platform != "win32":
            loop_config["loop"] = "uvloop"
            print("[INFO] Using uvloop for uvicorn", file=sys.stderr)
    except ImportError:
        pass

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", **loop_config)


async def main():
    """메인 함수 - MCP 모드"""
    if MCP_AVAILABLE:
        await run_mcp_server()
    else:
        print("[ERROR] MCP not available, cannot run MCP server", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # 실행 모드 결정
    if len(sys.argv) > 1 and sys.argv[1] == "--fastapi":
        # FastAPI 모드
        run_fastapi_server()
    else:
        # MCP 모드 (기본)
        print("[DEBUG] Starting MCP mode", file=sys.stderr)
        asyncio.run(main())
