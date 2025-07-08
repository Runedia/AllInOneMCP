"""
FastAPI 라우트들과 Pydantic 모델들
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Callable
import json
import asyncio
import sys
import config
from tools.utils import normalize_path, detect_file_encoding, ALLOWED_DIRECTORIES
from tools.utils import load_tools_json, create_pydantic_model
from tools_registry import TOOL_HANDLERS


# ==================== 동적 라우트 생성 로직 ====================

def create_dynamic_route(app: FastAPI, tool_data: Dict[str, Any]) -> None:
    """
    단일 도구에 대한 FastAPI 라우트를 동적으로 생성하고 등록
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
        tool_data: tools.json의 개별 도구 정의 딕셔너리
    """
    tool_name = tool_data['name']
    tool_description = tool_data['description']
    input_schema = tool_data['inputSchema']

    try:
        # 1. Pydantic 요청 모델 동적 생성
        request_model = create_pydantic_model(tool_name, input_schema)

        # 2. 동적 핸들러 함수 생성
        async def dynamic_handler(data: request_model = Body(...)) -> Dict[str, Any]:
            """동적으로 생성된 도구 핸들러"""
            try:
                # Pydantic 모델을 딕셔너리로 변환
                arguments = data.dict()

                # tools_registry에서 해당 도구 핸들러 가져오기
                if tool_name not in TOOL_HANDLERS:
                    raise HTTPException(
                        status_code=501,
                        detail=f"Tool '{tool_name}' handler not implemented"
                    )

                handler_func = TOOL_HANDLERS[tool_name]

                # 핸들러 함수 호출 (비동기 처리)
                if asyncio.iscoroutinefunction(handler_func):
                    result = await handler_func(arguments)
                else:
                    result = handler_func(arguments)

                # 결과 처리 - MCP와 동일한 형식 유지
                if isinstance(result, dict):
                    return result
                else:
                    return {"result": str(result)}

            except HTTPException:
                # HTTPException은 그대로 re-raise
                raise
            except Exception as e:
                # 기타 예외는 HTTPException으로 변환
                raise HTTPException(
                    status_code=500,
                    detail=f"Error executing {tool_name}: {str(e)}"
                )

        # 3. 라우트 등록
        route_path = f"/{tool_name}"
        app.add_api_route(
            path=route_path,
            endpoint=dynamic_handler,
            methods=["POST"],
            summary=f"Execute {tool_name}",
            description=tool_description,
            response_model=None,  # 유연한 응답을 위해 None 사용
            tags=[_get_tool_category(tool_name)]
        )

        print(f"[DEBUG] Dynamic route created: POST {route_path}", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] Failed to create route for {tool_name}: {e}", file=sys.stderr)


def _get_tool_category(tool_name: str) -> str:
    """
    도구 이름으로부터 카테고리를 추정
    tools_registry.TOOL_CATEGORIES를 참조하여 적절한 태그 반환
    """
    try:
        from tools_registry import TOOL_CATEGORIES
        for category, tools in TOOL_CATEGORIES.items():
            if tool_name in tools:
                return category
        return "tools"  # 기본 카테고리
    except ImportError:
        return "tools"


def register_dynamic_routes(app: FastAPI) -> None:
    """
    tools.json의 모든 도구에 대해 동적 라우트를 생성하고 등록
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    try:
        # tools.json 로드
        tools_data = load_tools_json()

        if not tools_data:
            print("[WARNING] No tools loaded from tools.json", file=sys.stderr)
            return

        # 각 도구에 대해 동적 라우트 생성
        success_count = 0
        for tool_data in tools_data:
            try:
                create_dynamic_route(app, tool_data)
                success_count += 1
            except Exception as e:
                tool_name = tool_data.get('name', 'unknown')
                print(f"[ERROR] Failed to create route for {tool_name}: {e}", file=sys.stderr)

        print(f"[INFO] Successfully created {success_count}/{len(tools_data)} dynamic routes", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] Failed to register dynamic routes: {e}", file=sys.stderr)


def create_fastapi_app() -> FastAPI:
    """FastAPI 앱 생성 및 설정"""
    app = FastAPI(
        title=config.SERVER_NAME,
        version=config.SERVER_VERSION,
        description="A hybrid server supporting both HTTP REST API and MCP protocol with token-efficient tools, OS commands, and optimized file editing",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우트 등록
    register_routes(app)

    return app


def register_routes(app: FastAPI):
    """모든 라우트를 앱에 등록"""

    @app.get("/")
    async def root():
        """루트 엔드포인트"""
        # 동적으로 도구 목록 생성
        tools_data = load_tools_json()
        tool_names = [tool['name'] for tool in tools_data] if tools_data else []

        return {
            "message": config.SERVER_NAME,
            "version": config.SERVER_VERSION,
            "total_tools": len(tool_names),
            "features": tool_names,
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "allowed_directories": "/list_allowed_directories"
            }
        }

    @app.get("/health")
    async def health_check():
        """헬스 체크"""
        try:
            from mcp.server import Server
            MCP_AVAILABLE = True
        except ImportError:
            MCP_AVAILABLE = False

        # 동적으로 도구 수 계산
        tools_data = load_tools_json()
        total_tools = len(tools_data) if tools_data else 0

        return {
            "status": "healthy",
            "mcp_available": MCP_AVAILABLE,
            "allowed_directories_count": len(ALLOWED_DIRECTORIES),
            "total_tools": total_tools
        }

    # ==================== 동적 라우트 생성 ====================
    # tools.json의 모든 도구에 대해 동적 라우트 생성
    try:
        register_dynamic_routes(app)
        print("[INFO] Dynamic routes registration completed", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Failed to register dynamic routes: {e}", file=sys.stderr)
        # 동적 라우트 생성 실패 시에도 서버는 계속 시작

    @app.get("/list_allowed_directories", summary="List access-permitted directories")
    async def list_allowed_directories():
        """Show all directories this server can access."""
        return {
            "allowed_directories": ALLOWED_DIRECTORIES,
            "count": len(ALLOWED_DIRECTORIES)
        }
