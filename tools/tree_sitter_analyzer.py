"""
Tree-sitter 기반 다중 언어 구문 분석기
tree-sitter 0.24.0+ 전용
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# Tree-sitter 관련 import 및 초기화
TREE_SITTER_AVAILABLE = False
AVAILABLE_PARSERS = {}

try:
    import tree_sitter
    from tree_sitter import Language, Parser
    print("tree-sitter 기본 패키지 로드 성공")

    # 언어별 파서 개별 import - 최신 API 방식
    parsers_to_load = [
        ('javascript', 'tree_sitter_javascript'),
        ('python', 'tree_sitter_python'), 
        ('typescript', 'tree_sitter_typescript'),
        ('java', 'tree_sitter_java'),
        ('cpp', 'tree_sitter_cpp'),
        ('c_sharp', 'tree_sitter_c_sharp'),
        ('c', 'tree_sitter_c'),
        ('rust', 'tree_sitter_rust'),
        ('css', 'tree_sitter_css'),
        ('html', 'tree_sitter_html'),
        ('json', 'tree_sitter_json'),
    ]

    for lang_name, module_name in parsers_to_load:
        try:
            module = __import__(module_name)
            # 최신 tree-sitter API: language 속성을 직접 사용
            language_func = getattr(module, 'language', None)
            if language_func:
                AVAILABLE_PARSERS[lang_name] = language_func
                print(f"{lang_name} 파서 로드 성공")
            else:
                print(f"{lang_name} 파서에서 language 함수를 찾을 수 없음")
        except ImportError as e:
            print(f"{lang_name} 파서 로드 실패: {e}")
        except Exception as e:
            print(f"{lang_name} 파서 로드 중 오류: {e}")

    if AVAILABLE_PARSERS:
        TREE_SITTER_AVAILABLE = True
        print(f"총 {len(AVAILABLE_PARSERS)}/{len(parsers_to_load)} 파서 로드됨")
    else:
        print("사용 가능한 tree-sitter 파서가 없습니다")

except ImportError as e:
    print(f"tree-sitter 기본 패키지 로드 실패: {e}")
except Exception as e:
    print(f"tree-sitter 초기화 중 예상치 못한 오류: {e}")
class TreeSitterAnalyzer:
    """다중 언어 tree-sitter 분석기 (0.24.0+ 전용)"""

    def __init__(self):
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self._init_languages()

    def _init_languages(self):
        """사용 가능한 언어의 파서만 초기화 - 최신 tree-sitter API"""
        if not TREE_SITTER_AVAILABLE:
            print("[ERROR] tree-sitter를 사용할 수 없습니다")
            return

        for lang_name, language_func in AVAILABLE_PARSERS.items():
            try:
                # 최신 tree-sitter API: language 함수를 직접 호출
                language = Language(language_func())
                
                # 최신 API: Parser 생성자에 직접 언어 전달
                parser = Parser(language)

                self.languages[lang_name] = language
                self.parsers[lang_name] = parser
                print(f"[OK] {lang_name} 파서 초기화 완료")

            except Exception as e:
                print(f"[ERROR] {lang_name} 파서 초기화 실패: {e}")
                # 디버깅을 위한 자세한 오류 정보
                import traceback
                print(f"[DEBUG] {lang_name} 상세 오류: {traceback.format_exc()}")

        print(f"[INFO] 총 {len(self.parsers)}개 파서 초기화 완료")

    def _get_language_from_extension(self, file_path: str) -> Optional[str]:
        """파일 확장자로부터 적절한 언어 파서 결정"""
        ext = Path(file_path).suffix.lower()

        extension_map = {
            '.js': 'javascript',
            '.mjs': 'javascript',
            '.cjs': 'javascript',
            '.jsx': 'typescript',  # JSX는 typescript 파서 사용
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.py': 'python',
            '.pyx': 'python',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'c_sharp',
            '.rs': 'rust',
            '.css': 'css',
            '.scss': 'css',
            '.sass': 'css',
            '.html': 'html',
            '.htm': 'html',
            '.json': 'json',
        }

        return extension_map.get(ext)

    def _get_function_query(self, language: str) -> str:
        """언어별 함수 검색 쿼리 생성"""
        queries = {
            'javascript': '''
                (function_declaration name: (identifier) @name) @function
                (method_definition name: (property_identifier) @name) @function
                (arrow_function) @function
                (function_expression name: (identifier) @name) @function
                (variable_declarator name: (identifier) @name value: (arrow_function)) @function
                (variable_declarator name: (identifier) @name value: (function_expression)) @function
            ''',
            'typescript': '''
                (function_declaration name: (identifier) @name) @function
                (method_definition name: (property_identifier) @name) @function
                (arrow_function) @function
                (function_expression name: (identifier) @name) @function
                (method_signature name: (property_identifier) @name) @function
                (variable_declarator name: (identifier) @name value: (arrow_function)) @function
                (variable_declarator name: (identifier) @name value: (function_expression)) @function
            ''',
            'python': '''
                (function_definition name: (identifier) @name) @function
            ''',
            'java': '''
                (method_declaration name: (identifier) @name) @function
                (constructor_declaration name: (identifier) @name) @function
            ''',
            'cpp': '''
                (function_definition declarator: (function_declarator declarator: (identifier) @name)) @function
                (function_declaration declarator: (function_declarator declarator: (identifier) @name)) @function
            ''',
            'c': '''
                (function_definition declarator: (function_declarator declarator: (identifier) @name)) @function
                (function_declaration declarator: (function_declarator declarator: (identifier) @name)) @function
            ''',
            'c_sharp': '''
                (method_declaration name: (identifier) @name) @function
                (constructor_declaration name: (identifier) @name) @function
            ''',
            'rust': '''
                (function_item name: (identifier) @name) @function
                (impl_item (function_item name: (identifier) @name)) @function
            ''',
        }

        return queries.get(language, '')

    def _get_node_text(self, node, content: str) -> str:
        """노드에서 텍스트를 안전하게 추출"""
        try:
            if hasattr(node, 'text') and node.text:
                return node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            else:
                return content[node.start_byte:node.end_byte]
        except:
            return content[node.start_byte:node.end_byte]

# =============================================================================
# MCP 도구 핸들러 함수들
# =============================================================================

# 전역 analyzer
analyzer = None

def get_analyzer():
    """analyzer 인스턴스를 안전하게 가져오기"""
    global analyzer
    if analyzer is None:
        if not TREE_SITTER_AVAILABLE:
            return None, "tree-sitter package is not available."

        if not AVAILABLE_PARSERS:
            return None, "No available tree-sitter language parsers."

        try:
            analyzer = TreeSitterAnalyzer()
            if not analyzer.parsers:
                return None, "Failed to initialize tree-sitter parsers."
        except Exception as e:
            return None, f"TreeSitter initialization failed: {str(e)}"
    return analyzer, None

async def handle_find_function(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """특정 함수를 검색하고 위치 정보 반환"""
    analyzer, error = get_analyzer()
    if analyzer is None:
        return {"error": error}

    try:
        path = arguments.get("path", "")
        function_name = arguments.get("function_name", "")

        if not path or not function_name:
            return {"error": "path and function_name are required"}

        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}

        # 파일 읽기
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 언어 결정
        language = analyzer._get_language_from_extension(path)
        if not language or language not in analyzer.parsers:
            return {"error": f"Unsupported file format: {path}"}

        # 파서로 구문 분석
        parser = analyzer.parsers[language]
        tree = parser.parse(bytes(content, "utf8"))

        # 함수 검색 쿼리
        query_text = analyzer._get_function_query(language)
        if not query_text:
            return {"error": f"Function search for {language} language is not yet supported"}

        query = analyzer.languages[language].query(query_text)
        captures = query.captures(tree.root_node)

        # tree-sitter 0.24.0의 딕셔너리 형식 처리
        function_nodes = captures.get('function', [])
        name_nodes = captures.get('name', [])

        # 함수와 이름을 매칭하여 찾기
        for func_node in function_nodes:
            for name_node in name_nodes:
                # 이름 노드가 함수 노드 내부에 있는지 확인
                if (func_node.start_point <= name_node.start_point <= func_node.end_point):
                    name_text = analyzer._get_node_text(name_node, content)
                    
                    if name_text == function_name:
                        start_line = func_node.start_point[0] + 1
                        end_line = func_node.end_point[0] + 1
                        
                        # 함수 시그니처 추출
                        function_text = analyzer._get_node_text(func_node, content)
                        first_line = function_text.split('\n')[0].strip()
                        
                        return {
                            "found": True,
                            "function_name": function_name,
                            "start_line": start_line,
                            "end_line": end_line,
                            "signature": first_line,
                            "language": language,
                            "file_path": path
                        }

        return {
            "found": False,
            "function_name": function_name,
            "message": f"Function '{function_name}' not found"
        }

    except Exception as e:
        return {"error": f"Error occurred during function search: {str(e)}"}

async def handle_list_functions(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """파일의 모든 함수 목록 조회"""
    analyzer, error = get_analyzer()
    if analyzer is None:
        return {"error": error}

    try:
        path = arguments.get("path", "")
        include_private = arguments.get("include_private", True)

        if not path:
            return {"error": "path is required"}

        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}

        # 파일 읽기
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 언어 결정
        language = analyzer._get_language_from_extension(path)
        if not language or language not in analyzer.parsers:
            return {"error": f"Unsupported file format: {path}"}

        # 파서로 구문 분석
        parser = analyzer.parsers[language]
        tree = parser.parse(bytes(content, "utf8"))

        # 함수 검색 쿼리
        query_text = analyzer._get_function_query(language)
        if not query_text:
            return {"error": f"Function listing for {language} language is not yet supported"}

        query = analyzer.languages[language].query(query_text)
        captures = query.captures(tree.root_node)

        functions = []
        processed_nodes = set()

        # tree-sitter 0.24.0의 딕셔너리 형식 처리
        function_nodes = captures.get('function', [])
        name_nodes = captures.get('name', [])

        for func_node in function_nodes:
            if id(func_node) not in processed_nodes:
                processed_nodes.add(id(func_node))
                
                # 함수 이름 찾기
                function_name = "anonymous"
                for name_node in name_nodes:
                    # 이름 노드가 함수 노드 내부에 있는지 확인
                    if (func_node.start_point <= name_node.start_point <= func_node.end_point):
                        function_name = analyzer._get_node_text(name_node, content)
                        break
                
                # private 함수 필터링 (언더스코어로 시작)
                if not include_private and function_name.startswith('_'):
                    continue
                
                start_line = func_node.start_point[0] + 1
                end_line = func_node.end_point[0] + 1
                
                # 함수 타입 결정
                node_type = func_node.type
                function_type = "function"
                if "arrow" in node_type:
                    function_type = "arrow_function"
                elif "method" in node_type:
                    function_type = "method"
                elif "async" in node_type:
                    function_type = "async_function"
                elif "variable_declarator" in node_type:
                    function_type = "const_function"
                
                functions.append({
                    "name": function_name,
                    "type": function_type,
                    "start_line": start_line,
                    "end_line": end_line,
                    "line_count": end_line - start_line + 1
                })

        # 라인 번호로 정렬
        functions.sort(key=lambda x: x['start_line'])

        return {
            "functions": functions,
            "total_count": len(functions),
            "language": language,
            "file_path": path,
            "include_private": include_private
        }

    except Exception as e:
        return {"error": f"Error occurred during function listing: {str(e)}"}

async def handle_extract_function(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """특정 함수의 전체 코드 추출"""
    try:
        path = arguments.get("path", "")
        function_name = arguments.get("function_name", "")
        include_comments = arguments.get("include_comments", True)

        if not path or not function_name:
            return {"error": "path and function_name are required"}

        # 먼저 함수 위치 찾기
        find_result = await handle_find_function({"path": path, "function_name": function_name})

        if not find_result.get("found"):
            return find_result

        # 파일 읽기
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_line = find_result["start_line"] - 1  # 0-based index
        end_line = find_result["end_line"] - 1

        # 주석 포함 옵션 처리
        if include_comments and start_line > 0:
            # 함수 바로 위의 주석들 찾기
            comment_start = start_line - 1
            while comment_start >= 0:
                line = lines[comment_start].strip()
                if (line.startswith('//') or line.startswith('#') or
                        line.startswith('/*') or line.startswith('*') or
                        line.startswith('"""') or line.startswith("'''")):
                    comment_start -= 1
                else:
                    comment_start += 1
                    break

            if comment_start < start_line:
                start_line = comment_start

        # 함수 코드 추출
        function_code = ''.join(lines[start_line:end_line + 1])

        return {
            "function_name": function_name,
            "code": function_code,
            "start_line": start_line + 1,
            "end_line": end_line + 1,
            "line_count": end_line - start_line + 1,
            "include_comments": include_comments,
            "language": find_result["language"],
            "file_path": path
        }

    except Exception as e:
        return {"error": f"Error occurred during function extraction: {str(e)}"}

async def handle_get_function_info(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """함수의 상세 메타데이터 조회"""
    try:
        path = arguments.get("path", "")
        function_name = arguments.get("function_name", "")

        if not path or not function_name:
            return {"error": "path and function_name are required"}

        # 함수 찾기
        find_result = await handle_find_function({"path": path, "function_name": function_name})

        if not find_result.get("found"):
            return find_result

        # 함수 코드 추출
        extract_result = await handle_extract_function({
            "path": path,
            "function_name": function_name,
            "include_comments": True
        })

        if "error" in extract_result:
            return extract_result

        function_code = extract_result["code"]

        # 복잡도 추정 (대략적)
        complexity_score = 0
        complexity_indicators = ['if', 'for', 'while', 'switch', 'case', 'try', 'catch', 'elif', 'else']
        for indicator in complexity_indicators:
            complexity_score += function_code.count(indicator)

        return {
            "function_name": function_name,
            "signature": find_result["signature"],
            "start_line": find_result["start_line"],
            "end_line": find_result["end_line"],
            "line_count": extract_result["line_count"],
            "complexity_score": complexity_score,
            "language": find_result["language"],
            "file_path": path,
            "preview": function_code[:200] + "..." if len(function_code) > 200 else function_code
        }

    except Exception as e:
        return {"error": f"Error occurred during function info retrieval: {str(e)}"}
