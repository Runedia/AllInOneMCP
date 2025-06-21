"""
파일 내 텍스트 검색 도구 모듈
Windows findstr 같은 기능을 제공하는 검색 도구들
"""

import os
import re
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path


class SearchResult:
    """검색 결과를 저장하는 클래스"""
    def __init__(self, file_path: str, line_number: int, line_content: str, 
                 match_start: int = -1, match_end: int = -1, match_text: str = ""):
        self.file_path = file_path
        self.line_number = line_number
        self.line_content = line_content.rstrip('\n\r')
        self.match_start = match_start
        self.match_end = match_end
        self.match_text = match_text
    
    def __str__(self):
        return f"{self.file_path}:{self.line_number}: {self.line_content}"


def search_in_file(file_path: str, search_text: str, case_sensitive: bool = True, 
                  context_lines: int = 0, use_regex: bool = False) -> List[SearchResult]:
    """
    단일 파일에서 텍스트 검색
    
    Args:
        file_path: 검색할 파일 경로
        search_text: 검색할 텍스트 또는 정규식 패턴
        case_sensitive: 대소문자 구분 여부
        context_lines: 매칭된 라인 앞뒤로 포함할 컨텍스트 라인 수
        use_regex: 정규식 사용 여부
        
    Returns:
        SearchResult 객체들의 리스트
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    if not os.path.isfile(file_path):
        raise ValueError(f"디렉토리입니다, 파일이 아닙니다: {file_path}")
    
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            
        # 검색 패턴 준비
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(search_text, flags)
        else:
            search_target = search_text if case_sensitive else search_text.lower()
        
        # 매칭된 라인 번호들 수집
        matched_lines = []
        
        for i, line in enumerate(lines, 1):
            line_content = line.rstrip('\n\r')
            
            if use_regex:
                match = pattern.search(line_content)
                if match:
                    result = SearchResult(
                        file_path=file_path,
                        line_number=i,
                        line_content=line_content,
                        match_start=match.start(),
                        match_end=match.end(),
                        match_text=match.group()
                    )
                    results.append(result)
                    matched_lines.append(i)
            else:
                line_target = line_content if case_sensitive else line_content.lower()
                if search_target in line_target:
                    # 매칭 위치 찾기
                    match_start = line_target.find(search_target)
                    match_end = match_start + len(search_target)
                    
                    result = SearchResult(
                        file_path=file_path,
                        line_number=i,
                        line_content=line_content,
                        match_start=match_start,
                        match_end=match_end,
                        match_text=line_content[match_start:match_end]
                    )
                    results.append(result)
                    matched_lines.append(i)
        
        # 컨텍스트 라인 추가
        if context_lines > 0 and results:
            context_results = []
            all_lines_to_include = set()
            
            # 컨텍스트 라인 번호들 수집
            for line_num in matched_lines:
                for offset in range(-context_lines, context_lines + 1):
                    context_line = line_num + offset
                    if 1 <= context_line <= len(lines):
                        all_lines_to_include.add(context_line)
            
            # 모든 라인 추가 (매칭된 라인과 컨텍스트 라인)
            for line_num in sorted(all_lines_to_include):
                line_content = lines[line_num - 1].rstrip('\n\r')
                
                # 이미 매칭된 라인인지 확인
                is_match = line_num in matched_lines
                if is_match:
                    # 기존 결과 사용
                    existing_result = next(r for r in results if r.line_number == line_num)
                    context_results.append(existing_result)
                else:
                    # 컨텍스트 라인 추가
                    context_result = SearchResult(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line_content
                    )
                    context_results.append(context_result)
            
            results = context_results
    
    except UnicodeDecodeError:
        # UTF-8로 읽기 실패 시 다른 인코딩 시도
        try:
            with open(file_path, 'r', encoding='cp949', errors='ignore') as file:
                # 동일한 검색 로직 재실행 (간소화)
                return search_in_file(file_path, search_text, case_sensitive, context_lines, use_regex)
        except:
            raise UnicodeDecodeError(f"파일 인코딩을 읽을 수 없습니다: {file_path}")
    
    except Exception as e:
        raise Exception(f"파일 검색 중 오류 발생: {str(e)}")
    
    return results


def search_in_directory(directory: str, search_text: str, file_extensions: List[str] = None,
                       case_sensitive: bool = True, context_lines: int = 0, 
                       use_regex: bool = False, max_files: int = 100) -> Dict[str, List[SearchResult]]:
    """
    디렉토리 내 여러 파일에서 텍스트 검색
    
    Args:
        directory: 검색할 디렉토리 경로
        search_text: 검색할 텍스트
        file_extensions: 검색할 파일 확장자 리스트 (예: ['.py', '.js'])
        case_sensitive: 대소문자 구분 여부
        context_lines: 컨텍스트 라인 수
        use_regex: 정규식 사용 여부
        max_files: 최대 검색 파일 수 (성능 제한)
        
    Returns:
        파일 경로를 키로 하는 SearchResult 리스트 딕셔너리
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {directory}")
    
    if not os.path.isdir(directory):
        raise ValueError(f"파일입니다, 디렉토리가 아닙니다: {directory}")
    
    results = {}
    file_count = 0
    
    # 파일 확장자 정규화
    if file_extensions:
        file_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                          for ext in file_extensions]
    
    try:
        for root, dirs, files in os.walk(directory):
            # 숨김 폴더 제외
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # 숨김 파일 제외
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                
                # 확장자 필터링
                if file_extensions:
                    file_ext = Path(file).suffix.lower()
                    if file_ext not in file_extensions:
                        continue
                
                # 최대 파일 수 제한
                if file_count >= max_files:
                    break
                
                try:
                    file_results = search_in_file(file_path, search_text, case_sensitive, 
                                                context_lines, use_regex)
                    if file_results:
                        results[file_path] = file_results
                    file_count += 1
                    
                except Exception as e:
                    # 개별 파일 오류는 무시하고 계속 진행
                    print(f"파일 검색 오류 (계속 진행): {file_path} - {str(e)}")
                    continue
            
            if file_count >= max_files:
                break
                
    except Exception as e:
        raise Exception(f"디렉토리 검색 중 오류 발생: {str(e)}")
    
    return results


def regex_search_advanced(file_path: str, pattern: str, flags: str = "", 
                         capture_groups: bool = False) -> List[Dict]:
    """
    고급 정규식 검색 (그룹 캡처 포함)
    
    Args:
        file_path: 검색할 파일 경로
        pattern: 정규식 패턴
        flags: 정규식 플래그 (i=대소문자무시, m=다중라인, s=점이모든문자)
        capture_groups: 캡처 그룹 반환 여부
        
    Returns:
        상세한 매칭 정보 딕셔너리 리스트
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    # 플래그 변환
    regex_flags = 0
    if 'i' in flags.lower():
        regex_flags |= re.IGNORECASE
    if 'm' in flags.lower():
        regex_flags |= re.MULTILINE
    if 's' in flags.lower():
        regex_flags |= re.DOTALL
    
    try:
        compiled_pattern = re.compile(pattern, regex_flags)
    except re.error as e:
        raise ValueError(f"잘못된 정규식 패턴: {str(e)}")
    
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines, 1):
            line_content = line.rstrip('\n\r')
            
            for match in compiled_pattern.finditer(line_content):
                result = {
                    'file_path': file_path,
                    'line_number': i,
                    'line_content': line_content,
                    'match_start': match.start(),
                    'match_end': match.end(),
                    'match_text': match.group(),
                    'full_match': match.group(0)
                }
                
                if capture_groups and match.groups():
                    result['groups'] = match.groups()
                    result['groupdict'] = match.groupdict()
                
                results.append(result)
    
    except Exception as e:
        raise Exception(f"정규식 검색 중 오류 발생: {str(e)}")
    
    return results


def format_search_results(results: List[SearchResult], show_line_numbers: bool = True,
                         highlight_matches: bool = False) -> str:
    """
    검색 결과를 포맷팅하여 문자열로 반환
    
    Args:
        results: SearchResult 리스트
        show_line_numbers: 라인 번호 표시 여부
        highlight_matches: 매칭 텍스트 강조 여부
        
    Returns:
        포맷팅된 결과 문자열
    """
    if not results:
        return "검색 결과가 없습니다."
    
    formatted_lines = []
    current_file = None
    
    for result in results:
        # 파일이 바뀔 때 구분선 추가
        if current_file != result.file_path:
            if current_file is not None:
                formatted_lines.append("")  # 빈 줄 추가
            formatted_lines.append(f"=== {result.file_path} ===")
            current_file = result.file_path
        
        # 라인 번호와 내용 포맷팅
        line_prefix = f"{result.line_number:4d}: " if show_line_numbers else ""
        
        line_content = result.line_content
        
        # 매칭 텍스트 강조 (간단한 마커 추가)
        if highlight_matches and result.match_start >= 0:
            before = line_content[:result.match_start]
            match = line_content[result.match_start:result.match_end]
            after = line_content[result.match_end:]
            line_content = f"{before}>>>{match}<<<{after}"
        
        formatted_lines.append(f"{line_prefix}{line_content}")
    
    return "\n".join(formatted_lines)


def get_search_statistics(results: Dict[str, List[SearchResult]]) -> Dict:
    """
    검색 결과 통계 정보 반환
    
    Args:
        results: 파일별 검색 결과 딕셔너리
        
    Returns:
        통계 정보 딕셔너리
    """
    total_files = len(results)
    total_matches = sum(len(file_results) for file_results in results.values())
    
    file_stats = []
    for file_path, file_results in results.items():
        file_stats.append({
            'file': file_path,
            'matches': len(file_results),
            'lines': [r.line_number for r in file_results]
        })
    
    return {
        'total_files_searched': total_files,
        'total_matches': total_matches,
        'files_with_matches': total_files,
        'file_statistics': file_stats
    }



# ========================================
# MCP 서버 핸들러 함수들
# ========================================

async def handle_search_in_file(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """단일 파일 검색 핸들러"""
    try:
        file_path = arguments.get("path", "")
        search_text = arguments.get("search_text", "")
        case_sensitive = arguments.get("case_sensitive", True)
        context_lines = arguments.get("context_lines", 0)
        use_regex = arguments.get("use_regex", False)
        show_matches = arguments.get("show_matches", True)
        
        if not file_path:
            return {"error": "파일 경로가 필요합니다"}
        
        if not search_text:
            return {"error": "검색할 텍스트가 필요합니다"}
        
        # 검색 실행
        results = search_in_file(
            file_path=file_path,
            search_text=search_text,
            case_sensitive=case_sensitive,
            context_lines=context_lines,
            use_regex=use_regex
        )
        
        if not results:
            return {
                "message": f"'{search_text}'에 대한 검색 결과가 없습니다.",
                "file_path": file_path,
                "search_text": search_text,
                "total_matches": 0
            }
        
        # 결과 포맷팅
        formatted_output = format_search_results(results, show_line_numbers=True, 
                                               highlight_matches=show_matches)
        
        # 통계 정보
        match_lines = [r.line_number for r in results if r.match_start >= 0]
        
        return {
            "message": f"📁 {file_path}",
            "search_text": search_text,
            "case_sensitive": case_sensitive,
            "use_regex": use_regex,
            "total_matches": len(match_lines),
            "match_lines": match_lines,
            "context_lines": context_lines,
            "formatted_results": formatted_output,
            "raw_results": [
                {
                    "line_number": r.line_number,
                    "line_content": r.line_content,
                    "match_start": r.match_start,
                    "match_end": r.match_end,
                    "match_text": r.match_text
                }
                for r in results
            ]
        }
        
    except Exception as e:
        return {"error": f"파일 검색 중 오류 발생: {str(e)}"}


async def handle_search_in_directory(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """디렉토리 검색 핸들러"""
    try:
        directory = arguments.get("directory", "")
        search_text = arguments.get("search_text", "")
        file_extensions = arguments.get("file_extensions", None)
        case_sensitive = arguments.get("case_sensitive", True)
        context_lines = arguments.get("context_lines", 0)
        use_regex = arguments.get("use_regex", False)
        max_files = arguments.get("max_files", 100)
        
        if not directory:
            return {"error": "디렉토리 경로가 필요합니다"}
        
        if not search_text:
            return {"error": "검색할 텍스트가 필요합니다"}
        
        # 검색 실행
        results = search_in_directory(
            directory=directory,
            search_text=search_text,
            file_extensions=file_extensions,
            case_sensitive=case_sensitive,
            context_lines=context_lines,
            use_regex=use_regex,
            max_files=max_files
        )
        
        if not results:
            return {
                "message": f"'{search_text}'에 대한 검색 결과가 없습니다.",
                "directory": directory,
                "search_text": search_text,
                "files_searched": 0,
                "total_matches": 0
            }
        
        # 통계 정보 생성
        stats = get_search_statistics(results)
        
        # 결과 포맷팅
        all_results = []
        for file_path, file_results in results.items():
            all_results.extend(file_results)
        
        formatted_output = format_search_results(all_results, show_line_numbers=True, 
                                               highlight_matches=True)
        
        return {
            "message": f"📂 디렉토리 검색 완료: {directory}",
            "search_text": search_text,
            "directory": directory,
            "file_extensions": file_extensions,
            "case_sensitive": case_sensitive,
            "use_regex": use_regex,
            "files_with_matches": stats["files_with_matches"],
            "total_matches": stats["total_matches"],
            "max_files_limit": max_files,
            "statistics": stats,
            "formatted_results": formatted_output,
            "file_results": {
                file_path: [
                    {
                        "line_number": r.line_number,
                        "line_content": r.line_content,
                        "match_start": r.match_start,
                        "match_end": r.match_end,
                        "match_text": r.match_text
                    }
                    for r in file_results
                ]
                for file_path, file_results in results.items()
            }
        }
        
    except Exception as e:
        return {"error": f"디렉토리 검색 중 오류 발생: {str(e)}"}


async def handle_regex_search(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """고급 정규식 검색 핸들러"""
    try:
        file_path = arguments.get("path", "")
        pattern = arguments.get("pattern", "")
        flags = arguments.get("flags", "")
        capture_groups = arguments.get("capture_groups", False)
        
        if not file_path:
            return {"error": "파일 경로가 필요합니다"}
        
        if not pattern:
            return {"error": "정규식 패턴이 필요합니다"}
        
        # 정규식 검색 실행
        results = regex_search_advanced(
            file_path=file_path,
            pattern=pattern,
            flags=flags,
            capture_groups=capture_groups
        )
        
        if not results:
            return {
                "message": f"정규식 패턴 '{pattern}'에 대한 검색 결과가 없습니다.",
                "file_path": file_path,
                "pattern": pattern,
                "flags": flags,
                "total_matches": 0
            }
        
        # 결과 포맷팅
        formatted_lines = [f"=== {file_path} ==="]
        for result in results:
            line_num = result["line_number"]
            line_content = result["line_content"]
            match_text = result["match_text"]
            
            # 매칭 텍스트 강조
            before = line_content[:result["match_start"]]
            after = line_content[result["match_end"]:]
            highlighted = f"{before}>>>{match_text}<<<{after}"
            
            formatted_lines.append(f"{line_num:4d}: {highlighted}")
            
            # 캡처 그룹 정보 추가
            if capture_groups and result.get("groups"):
                for i, group in enumerate(result["groups"], 1):
                    if group is not None:
                        formatted_lines.append(f"      그룹 {i}: {group}")
        
        formatted_output = "\n".join(formatted_lines)
        
        return {
            "message": f"🔍 정규식 검색 완료: {file_path}",
            "pattern": pattern,
            "flags": flags,
            "capture_groups": capture_groups,
            "total_matches": len(results),
            "match_lines": [r["line_number"] for r in results],
            "formatted_results": formatted_output,
            "detailed_results": results
        }
        
    except Exception as e:
        return {"error": f"정규식 검색 중 오류 발생: {str(e)}"}
