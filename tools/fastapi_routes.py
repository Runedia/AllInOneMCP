"""
FastAPI 라우트들과 Pydantic 모델들
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tools.utils import normalize_path, detect_file_encoding, ALLOWED_DIRECTORIES


# Pydantic 모델들
class ReadFileRequest(BaseModel):
    path: str = Field(..., description="Path to the file to read")


class WriteFileRequest(BaseModel):
    path: str = Field(..., description="Path to write to. Existing file will be overwritten.")
    content: str = Field(..., description="UTF-8 encoded text content to write.")


class CreateDirectoryRequest(BaseModel):
    path: str = Field(..., description="Directory path to create. Intermediate dirs are created automatically.")


class ListDirectoryRequest(BaseModel):
    path: str = Field(..., description="Directory path to list contents for.")


class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message indicating the operation was completed.")


class ReadFileResponse(BaseModel):
    content: str = Field(..., description="UTF-8 encoded text content of the file.")


def create_fastapi_app() -> FastAPI:
    """FastAPI 앱 생성 및 설정"""
    app = FastAPI(
        title="Hybrid Filesystem API",
        version="0.6.0",
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
        return {
            "message": "Hybrid Filesystem Server",
            "version": "0.6.0",
            "features": [
                "file_exists", "count_files", "get_directory_size",
                "get_recent_files", "analyze_project", "git_status_summary",
                "copy_file", "move_file", "delete_file", "backup_file",
                "file_info",
                "find_and_replace", "insert_line", "append_to_file", "get_file_section"
            ],
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

        return {
            "status": "healthy",
            "mcp_available": MCP_AVAILABLE,
            "allowed_directories_count": len(ALLOWED_DIRECTORIES),
            "total_tools": 21
        }

    @app.post("/read_file", response_model=ReadFileResponse, summary="Read a file")
    async def read_file(data: ReadFileRequest = Body(...)):
        """Read the entire contents of a file and return as JSON."""
        try:
            path = normalize_path(data.path)
            if not path.exists():
                raise HTTPException(status_code=404, detail=f"File not found: {data.path}")
            if not path.is_file():
                raise HTTPException(status_code=400, detail=f"Path is not a file: {data.path}")

            encoding = detect_file_encoding(path)
            file_content = path.read_text(encoding=encoding)
            return ReadFileResponse(content=file_content)
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file {data.path}: {str(e)}")

    @app.post("/write_file", response_model=SuccessResponse, summary="Write to a file")
    async def write_file(data: WriteFileRequest = Body(...)):
        """Write content to a file, overwriting if it exists."""
        try:
            path = normalize_path(data.path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data.content, encoding="utf-8")
            return SuccessResponse(message=f"Successfully wrote {len(data.content)} characters to {data.path}")
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write to {data.path}: {str(e)}")

    @app.post("/create_directory", response_model=SuccessResponse, summary="Create a directory")
    async def create_directory(data: CreateDirectoryRequest = Body(...)):
        """Create a new directory recursively."""
        try:
            dir_path = normalize_path(data.path)
            dir_path.mkdir(parents=True, exist_ok=True)
            return SuccessResponse(message=f"Successfully created directory {data.path}")
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create directory {data.path}: {str(e)}")

    @app.post("/list_directory", summary="List a directory")
    async def list_directory(data: ListDirectoryRequest = Body(...)):
        """List contents of a directory."""
        try:
            dir_path = normalize_path(data.path)
            if not dir_path.exists():
                raise HTTPException(status_code=404, detail=f"Directory not found: {data.path}")
            if not dir_path.is_dir():
                raise HTTPException(status_code=400, detail=f"Path is not a directory: {data.path}")

            listing = []
            for entry in sorted(dir_path.iterdir()):
                entry_type = "directory" if entry.is_dir() else "file"
                size = None
                if entry.is_file():
                    try:
                        size = entry.stat().st_size
                    except:
                        pass
                listing.append({
                    "name": entry.name,
                    "type": entry_type,
                    "size": size
                })

            return {"items": listing, "count": len(listing)}
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/list_allowed_directories", summary="List access-permitted directories")
    async def list_allowed_directories():
        """Show all directories this server can access."""
        return {
            "allowed_directories": ALLOWED_DIRECTORIES,
            "count": len(ALLOWED_DIRECTORIES)
        }
