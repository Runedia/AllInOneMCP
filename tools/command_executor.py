"""
시스템 명령어 실행 도구 (Git 명령어 차단)
"""

import subprocess
import os
import re
from typing import Dict, Any


async def handle_execute_command(arguments: Dict[str, Any]) -> str:
    """시스템 명령어 실행 도구 (git 명령어 차단)"""
    command = arguments.get("command", "")
    timeout = arguments.get("timeout", 30)

    if not command:
        raise ValueError("Command is required")

    # Git 명령어 차단 검사
    if is_git_command(command):
        return get_git_command_blocked_message()

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
            return f"✅ Command executed successfully:\n{output}"
        else:
            error = result_proc.stderr.strip()[:200]  # 에러도 제한
            return f"❌ Command failed with exit code {result_proc.returncode}:\n{error}"

    except subprocess.TimeoutExpired:
        return f"⏰ Command timed out after {timeout} seconds"
    except Exception as e:
        return f"💥 Execution error: {str(e)}"


def is_git_command(command: str) -> bool:
    """Git 명령어인지 확인하는 함수"""
    # 명령어를 소문자로 변환하고 앞뒤 공백 제거
    cmd_lower = command.strip().lower()

    # 다양한 git 명령어 패턴들
    git_patterns = [
        r'^git\s',  # git으로 시작
        r'^\s*git\s',  # 앞에 공백이 있어도 git으로 시작
        r'&&\s*git\s',  # && git (명령어 체이닝)
        r';\s*git\s',  # ; git (명령어 체이닝)
        r'\|\s*git\s',  # | git (파이프)
        r'`git\s',  # `git (백틱 내부)
        r'\$\(git\s',  # $(git (명령어 치환)
    ]

    # 패턴 중 하나라도 매치되면 git 명령어로 판단
    for pattern in git_patterns:
        if re.search(pattern, cmd_lower):
            return True

    return False


def get_git_command_blocked_message() -> str:
    """Message to display when Git commands are blocked"""
    return """🚫 Git commands are blocked for security reasons.

📚 Available Git-specific tools:
• git_status - Check Git repository status
• git_add - Add files to staging area
• git_commit - Commit changes
• git_push - Push to remote repository
• git_pull - Pull from remote repository
• git_clone - Clone repository
• git_branch - Branch management (create, switch, list)
• git_log - View commit history
• git_init - Initialize new Git repository

💡 Example: Use git_status to check repository status."""
