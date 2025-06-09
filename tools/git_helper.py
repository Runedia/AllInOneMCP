"""
Git 관련 기능들
"""

import subprocess
from typing import Dict, Any

from tools.utils import normalize_path


async def handle_git_status_summary(arguments: Dict[str, Any]) -> str:
    """Git 상태 요약 도구"""
    path_str = arguments.get("path", "")
    dir_path = normalize_path(path_str)

    git_dir = dir_path / ".git"
    if not git_dir.exists():
        return "Not a git repository"

    try:
        # git status --porcelain으로 간단한 상태만
        result_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=dir_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result_proc.returncode == 0:
            lines = result_proc.stdout.strip().split('\n') if result_proc.stdout.strip() else []
            if not lines:
                return "Clean (no changes)"
            else:
                modified = len([l for l in lines if l.startswith(' M')])
                added = len([l for l in lines if l.startswith('A')])
                untracked = len([l for l in lines if l.startswith('??')])
                return f"Modified: {modified}, Added: {added}, Untracked: {untracked}"
        else:
            return "Git error"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "Git not available"
    except Exception:
        return "Git command failed"


async def handle_execute_command(arguments: Dict[str, Any]) -> str:
    """시스템 명령어 실행 도구"""
    import os

    command = arguments.get("command", "")
    timeout = arguments.get("timeout", 30)

    if not command:
        raise ValueError("Command is required")

    try:
        result_proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()  # 현재 작업 디렉토리에서 실행
        )

        if result_proc.returncode == 0:
            output = result_proc.stdout.strip()
            if len(output) > 500:  # 긴 출력은 잘라내기
                output = output[:500] + "... (truncated)"
            return f"✅ Command succeeded:\n{output}"
        else:
            error = result_proc.stderr.strip()[:200]  # 에러도 제한
            return f"❌ Command failed (code {result_proc.returncode}):\n{error}"

    except subprocess.TimeoutExpired:
        return f"❌ Command timed out after {timeout}s"
    except Exception as e:
        return f"❌ Command error: {str(e)}"
