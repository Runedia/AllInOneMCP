"""
공통 유틸리티 함수들
경로 정규화, 파일 인코딩 감지 등
"""

import os
import pathlib
import sys

# Windows 호환성
try:
    import chardet

    print("[DEBUG] chardet imported successfully", file=sys.stderr)
except ImportError:
    chardet = None
    print("[DEBUG] chardet not available", file=sys.stderr)

# 설정 import
try:
    from config import ALLOWED_DIRECTORIES

    print(f"[DEBUG] Config loaded: {ALLOWED_DIRECTORIES}", file=sys.stderr)
except ImportError:
    ALLOWED_DIRECTORIES = [
        "C:\\",
    ]
    print(f"[DEBUG] Using default config", file=sys.stderr)


def normalize_path(requested_path: str) -> pathlib.Path:
    """경로 정규화 및 권한 확인"""
    try:
        requested = pathlib.Path(os.path.expanduser(requested_path)).resolve()

        if os.name == 'nt' and len(str(requested)) > 260:
            raise ValueError(f"Path too long for Windows: {len(str(requested))} characters")

        for allowed in ALLOWED_DIRECTORIES:
            if str(requested).lower().startswith(allowed.lower()):
                return requested

        raise PermissionError(f"Access denied: {requested} not in allowed directories")
    except Exception as e:
        print(f"[DEBUG] Path error: {e}", file=sys.stderr)
        raise


def detect_file_encoding(file_path: pathlib.Path) -> str:
    """파일 인코딩 감지"""
    if not chardet:
        return "utf-8"

    try:
        with file_path.open("rb") as f:
            raw_data = f.read(8192)
            if not raw_data:
                return "utf-8"

            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)

            if confidence < 0.7 or not encoding:
                common_encodings = ['utf-8', 'cp949', 'euc-kr', 'cp1252', 'latin1']
                for enc in common_encodings:
                    try:
                        with file_path.open("r", encoding=enc) as test_f:
                            test_f.read(1024)
                        return enc
                    except (UnicodeDecodeError, LookupError):
                        continue
                return "utf-8"

            return encoding
    except Exception:
        return "utf-8"


# ==================== 새로운 공통 유틸리티 함수들 ====================

import json
from typing import List, Dict, Any, Type, Optional
from pydantic import BaseModel, Field, create_model


def load_tools_json() -> List[Dict[str, Any]]:
    """
    tools.json 파일에서 도구 정의를 로드하여 딕셔너리 리스트로 반환
    mcp_server.py의 get_tool_definitions() 로직을 재사용하여 일관성 확보
    """
    try:
        # 현재 스크립트와 같은 디렉토리의 상위 디렉토리에 있는 tools.json 파일 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        tools_json_path = os.path.join(parent_dir, 'tools.json')

        # JSON 파일 읽기
        with open(tools_json_path, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)

        print(f"[DEBUG] Loaded {len(tools_data)} tools from tools.json", file=sys.stderr)
        return tools_data

    except FileNotFoundError:
        print(f"[ERROR] tools.json file not found at {tools_json_path}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in tools.json: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[ERROR] Error loading tools from JSON: {e}", file=sys.stderr)
        return []


def create_pydantic_model(tool_name: str, input_schema: Dict[str, Any]) -> Type[BaseModel]:
    """
    tools.json의 inputSchema를 기반으로 Pydantic 모델을 동적 생성
    
    Args:
        tool_name: 도구 이름 (모델 클래스명에 사용)
        input_schema: JSON Schema 딕셔너리
        
    Returns:
        동적 생성된 Pydantic BaseModel 클래스
    """
    try:
        # 스키마에서 properties와 required 필드 추출
        properties = input_schema.get('properties', {})
        required_fields = input_schema.get('required', [])

        # Pydantic 필드 딕셔너리 생성
        fields = {}

        for field_name, field_schema in properties.items():
            field_type = _get_python_type_from_schema(field_schema)
            field_description = field_schema.get('description', '')
            field_default = field_schema.get('default')

            # 필수 필드인지 확인
            if field_name in required_fields:
                # 필수 필드: Field(..., description=...)
                fields[field_name] = (field_type, Field(..., description=field_description))
            else:
                # 선택 필드: Field(default_value, description=...)
                if field_default is not None:
                    fields[field_name] = (field_type, Field(field_default, description=field_description))
                else:
                    # Optional 타입으로 변경
                    from typing import Union
                    optional_type = Union[field_type, None]
                    fields[field_name] = (optional_type, Field(None, description=field_description))

        # 동적 모델 생성
        model_name = f"{tool_name.replace('_', '').title()}Request"
        return create_model(model_name, **fields)

    except Exception as e:
        print(f"[ERROR] Error creating Pydantic model for {tool_name}: {e}", file=sys.stderr)
        # 기본 모델 반환
        return create_model(f"{tool_name}Request", **{})


def _get_python_type_from_schema(field_schema: Dict[str, Any]) -> Type:
    """
    JSON Schema 타입을 Python 타입으로 변환
    
    Args:
        field_schema: JSON Schema 필드 정의
        
    Returns:
        Python 타입
    """
    schema_type = field_schema.get('type', 'string')

    if schema_type == 'string':
        # enum이 있는 경우 처리
        if 'enum' in field_schema:
            # enum이 있는 경우 단순히 str 타입으로 처리 (검증은 FastAPI에서 수행)
            return str
        return str
        return int
    elif schema_type == 'number':
        return float
    elif schema_type == 'boolean':
        return bool
    elif schema_type == 'array':
        from typing import List
        # 배열 아이템 타입 확인
        items = field_schema.get('items', {})
        item_type = _get_python_type_from_schema(items)
        return List[item_type]
    elif schema_type == 'object':
        from typing import Dict, Any
        return Dict[str, Any]
    else:
        # 알 수 없는 타입은 Any로 처리
        from typing import Any
        return Any
