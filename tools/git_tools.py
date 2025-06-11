"""
GitPython 라이브러리 기반 Git 도구들
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
import json

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

from tools.utils import normalize_path


def is_git_available() -> bool:
    """GitPython 라이브러리 사용 가능 여부 확인"""
    return GIT_AVAILABLE


async def handle_git_status(arguments: Dict[str, Any]) -> str:
    """
    Git 저장소의 상세한 작업 트리 상태 표시
    
    Git 저장소의 현재 상태를 자세히 분석하여 제공합니다.
    modified, staged, untracked 파일들의 상세 정보를 포함합니다.
    
    Args:
        repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        
    Returns:
        str: Git 상태 상세 정보
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = normalize_path(arguments.get("repo_path", "."))
        
        if not repo_path.is_dir():
            return "Error: Directory does not exist"
        
        repo = git.Repo(str(repo_path))
        
        # 기본 상태 정보
        result = [f"Repository path: {repo_path}"]
        result.append(f"Current branch: {repo.active_branch.name}")
        
        # 변경된 파일들 확인
        modified_files = [item.a_path for item in repo.index.diff(None)]
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        untracked_files = repo.untracked_files
        
        result.append(f"\nStatus summary:")
        result.append(f"  • Modified files: {len(modified_files)}")
        result.append(f"  • Staged files: {len(staged_files)}") 
        result.append(f"  • Untracked files: {len(untracked_files)}")
        
        if modified_files:
            result.append(f"\nModified files:")
            for file in modified_files:
                result.append(f"  • {file}")
        
        if staged_files:
            result.append(f"\nStaged files:")
            for file in staged_files:
                result.append(f"  • {file}")
        
        if untracked_files:
            result.append(f"\nUntracked files:")
            for file in untracked_files:
                result.append(f"  • {file}")
        
        if not modified_files and not staged_files and not untracked_files:
            result.append(f"\nWorking tree is clean")
        
        return "\n".join(result)
        
    except git.InvalidGitRepositoryError:
        return "Error: Not a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_add(arguments: Dict[str, Any]) -> str:
    """
    파일들을 스테이징 영역에 추가
    
    지정된 파일들을 다음 커밋을 위해 스테이징 영역에 추가합니다.
    여러 파일을 한 번에 추가할 수 있습니다.
    
    Args:
        repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        files: 추가할 파일 경로 목록
        
    Returns:
        str: 스테이징 성공 메시지
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = normalize_path(arguments.get("repo_path", "."))
        files = arguments.get("files", [])
        
        if not files:
            return "Error: files parameter is required"
        
        if not isinstance(files, list):
            files = [files]
        
        if not repo_path.is_dir():
            return "Error: Directory does not exist"
        
        repo = git.Repo(str(repo_path))
        repo.index.add(files)
        
        return f"Files staged successfully: {', '.join(files)}"
        
    except git.InvalidGitRepositoryError:
        return "Error: Not a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_commit(arguments: Dict[str, Any]) -> str:
    """
    스테이지된 변경사항을 저장소에 커밋
    
    현재 스테이징 영역에 있는 모든 변경사항을 지정된 메시지와 함께 커밋합니다.
    커밋 후 새로운 커밋의 해시값을 반환합니다.
    
    Args:
        repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        message: 커밋 메시지
        
    Returns:
        str: 커밋 성공 메시지 및 해시값
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = normalize_path(arguments.get("repo_path", "."))
        message = arguments.get("message")
        
        if not message:
            return "Error: Commit message is required"
        
        if not repo_path.is_dir():
            return "Error: Directory does not exist"
        
        repo = git.Repo(str(repo_path))
        
        # 스테이지된 변경사항이 있는지 확인
        if not repo.index.diff("HEAD"):
            return "Error: No staged changes to commit"
        
        commit = repo.index.commit(message)
        return f"Changes committed successfully with hash {commit.hexsha[:8]}"
        
    except git.InvalidGitRepositoryError:
        return "Error: Not a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_push(arguments: Dict[str, Any]) -> str:
    """
    로컬 브랜치를 원격 저장소로 푸시
    
    현재 브랜치의 커밋들을 원격 저장소로 업로드합니다.
    
    Args:
        repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        remote: 원격 저장소 이름 (기본값: origin)
        branch: 푸시할 브랜치 (기본값: 현재 브랜치)
        
    Returns:
        str: 푸시 성공 메시지
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = normalize_path(arguments.get("repo_path", "."))
        remote_name = arguments.get("remote", "origin")
        branch = arguments.get("branch")
        
        if not repo_path.is_dir():
            return "Error: Directory does not exist"
        
        repo = git.Repo(str(repo_path))
        
        if not branch:
            branch = repo.active_branch.name
        
        remote = repo.remote(remote_name)
        remote.push(branch)
        
        return f"Push completed: {branch} → {remote_name}/{branch}"
        
    except git.InvalidGitRepositoryError:
        return "Error: Not a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_pull(arguments: Dict[str, Any]) -> str:
    """
    원격 저장소에서 변경사항을 가져와 병합
    
    원격 저장소의 최신 변경사항을 로컬 브랜치로 가져와 병합합니다.
    
    Args:
        repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        remote: 원격 저장소 이름 (기본값: origin)
        branch: 가져올 브랜치 (기본값: 현재 브랜치)
        
    Returns:
        str: 풀 성공 메시지
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = normalize_path(arguments.get("repo_path", "."))
        remote_name = arguments.get("remote", "origin")
        branch = arguments.get("branch")
        
        if not repo_path.is_dir():
            return "Error: Directory does not exist"
        
        repo = git.Repo(str(repo_path))
        
        if not branch:
            branch = repo.active_branch.name
        
        remote = repo.remote(remote_name)
        remote.pull(branch)
        
        return f"Pull completed: {remote_name}/{branch} → {branch}"
        
    except git.InvalidGitRepositoryError:
        return "Error: Not a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_clone(arguments: Dict[str, Any]) -> str:
    """
    원격 저장소를 로컬에 복제
    
    지정된 URL의 Git 저장소를 로컬 디렉토리에 복제합니다.
    
    Args:
        url: 복제할 Git 저장소 URL
        path: 복제할 로컬 경로 (선택사항)
        
    Returns:
        str: 복제 성공 메시지
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        url = arguments.get("url")
        path = arguments.get("path")
        
        if not url:
            return "Error: Repository URL is required"
        
        if path:
            path = normalize_path(path)
            repo = git.Repo.clone_from(url, str(path))
            return f"Repository cloned successfully: {url} → {path}"
        else:
            repo = git.Repo.clone_from(url, ".")
            return f"Repository cloned successfully: {url}"
        
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_branch(arguments: Dict[str, Any]) -> str:
    """
    브랜치 관리 (생성, 전환, 목록, 삭제)
    
    Git 브랜치를 관리합니다. 작업 종류에 따라 다양한 브랜치 작업을 수행할 수 있습니다.
    
    Args:
        repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        action: 수행할 작업 (list/create/checkout/delete)
        branch_name: 브랜치 이름 (action이 create/checkout/delete일 때 필요)
        base_branch: 기준 브랜치 (create 시 선택사항)
        
    Returns:
        str: 브랜치 작업 결과
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = normalize_path(arguments.get("repo_path", "."))
        action = arguments.get("action", "list")
        branch_name = arguments.get("branch_name")
        base_branch = arguments.get("base_branch")
        
        if not repo_path.is_dir():
            return "Error: Directory does not exist"
        
        repo = git.Repo(str(repo_path))
        
        if action == "list":
            # 브랜치 목록 표시
            branches = []
            for branch in repo.branches:
                prefix = "* " if branch == repo.active_branch else "  "
                branches.append(f"{prefix}{branch.name}")
            
            result = ["Local branches:"]
            result.extend(branches)
            return "\n".join(result)
        
        elif action == "create":
            # 새 브랜치 생성
            if not branch_name:
                return "Error: Branch name is required"
            
            # 브랜치가 이미 존재하는지 확인
            if branch_name in [ref.name for ref in repo.refs]:
                return f"Error: Branch '{branch_name}' already exists"
            
            if base_branch:
                try:
                    base = repo.refs[base_branch]
                except IndexError:
                    return f"Error: Base branch '{base_branch}' does not exist"
            else:
                base = repo.active_branch
            
            repo.create_head(branch_name, base)
            return f"Branch created successfully: '{branch_name}' (based on {base.name})"
        
        elif action == "checkout":
            # 브랜치 전환
            if not branch_name:
                return "Error: Branch name is required"
            
            # 브랜치가 존재하는지 확인
            if branch_name not in [ref.name for ref in repo.refs]:
                return f"Error: Branch '{branch_name}' does not exist"
            
            # 변경되지 않은 파일이 있는지 확인
            if repo.is_dirty():
                return "Error: You have unstaged changes. Please commit or stash them first"
            
            repo.git.checkout(branch_name)
            return f"Switched to branch '{branch_name}'"
        
        elif action == "delete":
            # 브랜치 삭제
            if not branch_name:
                return "Error: Branch name is required"
            
            # 현재 브랜치인지 확인
            if branch_name == repo.active_branch.name:
                return f"Error: Cannot delete current branch '{branch_name}'"
            
            # 브랜치가 존재하는지 확인
            if branch_name not in [ref.name for ref in repo.refs]:
                return f"Error: Branch '{branch_name}' does not exist"
            
            repo.delete_head(branch_name)
            return f"Branch deleted successfully: {branch_name}"
        
        else:
            return f"Error: Unknown action '{action}'. Available actions: list, create, checkout, delete"
        
    except git.InvalidGitRepositoryError:
        return "Error: Not a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_log(arguments: Dict[str, Any]) -> str:
    """
    커밋 히스토리 조회
    
    저장소의 커밋 히스토리를 지정된 개수만큼 조회합니다.
    각 커밋의 해시, 작성자, 날짜, 메시지를 포함합니다.
    
    Args:
        repo_path: Git 저장소 경로 (기본값: 현재 디렉토리)
        max_count: 조회할 최대 커밋 개수 (기본값: 10)
        
    Returns:
        str: 커밋 히스토리 정보
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = normalize_path(arguments.get("repo_path", "."))
        max_count = arguments.get("max_count", 10)
        
        if not repo_path.is_dir():
            return "Error: Directory does not exist"
        
        repo = git.Repo(str(repo_path))
        commits = list(repo.iter_commits(max_count=max_count))
        
        if not commits:
            return "No commits found"
        
        result = [f"Commit history (last {len(commits)} commits):"]
        result.append("")
        
        for i, commit in enumerate(commits, 1):
            result.append(f"{i}. {commit.hexsha[:8]} - {commit.summary}")
            result.append(f"   Author: {commit.author} <{commit.author.email}>")
            result.append(f"   Date: {commit.authored_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            result.append("")
        
        return "\n".join(result)
        
    except git.InvalidGitRepositoryError:
        return "Error: Not a git repository"
    except git.GitCommandError as e:
        return f"Git error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def handle_git_init(arguments: Dict[str, Any]) -> str:
    """
    새 Git 저장소 초기화
    
    지정된 경로에 새로운 Git 저장소를 초기화합니다.
    디렉토리가 존재하지 않으면 자동으로 생성됩니다.
    
    Args:
        repo_path: 초기화할 디렉토리 경로
        
    Returns:
        str: 초기화 성공 메시지
    """
    if not is_git_available():
        return "Error: GitPython is not installed. Install with: pip install GitPython"
    
    try:
        repo_path = arguments.get("repo_path")
        
        if not repo_path:
            return "Error: repo_path parameter is required"
        
        repo_path = normalize_path(repo_path)
        
        # 이미 Git 저장소인지 확인
        if repo_path.exists():
            try:
                existing_repo = git.Repo(str(repo_path))
                return f"Error: '{repo_path}' is already a git repository"
            except git.InvalidGitRepositoryError:
                # Git 저장소가 아니므로 계속 진행
                pass
        
        # 저장소 초기화
        repo = git.Repo.init(path=str(repo_path), mkdir=True)
        return f"Initialized empty Git repository in {repo.git_dir}"
        
    except PermissionError:
        return f"Error: Permission denied to create repository at '{repo_path}'"
    except Exception as e:
        return f"Error initializing repository: {str(e)}"
