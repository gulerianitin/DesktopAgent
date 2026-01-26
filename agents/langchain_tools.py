"""
LangChain Tools for Desktop Agent
Defines tools that the agent can use to interact with the system
"""
from typing import Optional
from langchain_core.tools import tool
from utils.security import SecureCommandExecutor, SecurityError

# Import debugging tools
from agents.debugging_tools import DEBUGGING_TOOLS


# Initialize secure executor
secure_executor = SecureCommandExecutor(
    work_directory="/tmp",
    allowed_sudo=True
)


@tool
def execute_shell_command(command: str) -> str:
    """
    Execute a shell command on the Ubuntu system.

    Use this for installing packages, running system commands, or executing programs.
    The command will be validated for security before execution.

    Args:
        command: The shell command to execute (e.g., "sudo apt-get install gimp")

    Returns:
        str: The command output or error message

    Examples:
        - execute_shell_command("sudo apt-get update")
        - execute_shell_command("which python3")
        - execute_shell_command("sudo apt-get install -y vim")
    """
    try:
        result = secure_executor.execute_command(command, timeout=300)

        if result['success']:
            output = result['stdout'].strip()
            return f"✅ Command successful (exit code {result['returncode']})\n\nOutput:\n{output[:1000]}"
        else:
            error = result['stderr'].strip()
            return f"❌ Command failed (exit code {result['returncode']})\n\nError:\n{error[:500]}"

    except SecurityError as e:
        return f"🛑 Security Error: {str(e)}\n\nThis command was blocked for safety. Try a different approach."
    except Exception as e:
        return f"❌ Execution Error: {str(e)}"


@tool
def verify_installation(package_name: str) -> str:
    """
    Verify if a package or program is installed and working.

    Use this to check if an installation was successful.

    Args:
        package_name: Name of the package/program to verify

    Returns:
        str: Verification result with version info if available

    Examples:
        - verify_installation("gimp")
        - verify_installation("python3")
        - verify_installation("git")
    """
    try:
        # Check if binary exists
        which_result = secure_executor.execute_command(f"which {package_name}", timeout=10)

        if which_result['success']:
            binary_path = which_result['stdout'].strip()

            # Try to get version
            version_result = secure_executor.execute_command(
                f"{package_name} --version 2>&1 | head -n 1",
                timeout=10
            )

            version_info = version_result['stdout'].strip() if version_result['success'] else "version unknown"

            return f"✅ {package_name} is installed\nLocation: {binary_path}\nVersion: {version_info}"
        else:
            return f"❌ {package_name} is not installed or not in PATH"

    except Exception as e:
        return f"❌ Verification error: {str(e)}"


@tool
def search_package(package_name: str) -> str:
    """
    Search for a package in apt repositories.

    Use this when you're not sure of the exact package name or want to find available packages.

    Args:
        package_name: Package name or search term

    Returns:
        str: Search results showing available packages

    Examples:
        - search_package("image editor")
        - search_package("python")
        - search_package("video player")
    """
    try:
        result = secure_executor.execute_command(
            f"apt-cache search {package_name} | head -n 10",
            timeout=30
        )

        if result['success'] and result['stdout'].strip():
            return f"📦 Available packages matching '{package_name}':\n\n{result['stdout'][:800]}"
        else:
            return f"❌ No packages found matching '{package_name}'"

    except Exception as e:
        return f"❌ Search error: {str(e)}"


@tool
def get_system_info() -> str:
    """
    Get information about the system (OS, disk space, memory, etc.).

    Use this to check system resources before installing large packages.

    Returns:
        str: System information including OS version, disk space, memory

    Examples:
        - get_system_info()
    """
    try:
        info = {}

        # OS version
        os_result = secure_executor.execute_command("lsb_release -d", timeout=10)
        if os_result['success']:
            info['os'] = os_result['stdout'].replace('Description:', '').strip()

        # Disk space
        disk_result = secure_executor.execute_command("df -h / | tail -n 1", timeout=10)
        if disk_result['success']:
            info['disk'] = disk_result['stdout'].strip()

        # Memory
        mem_result = secure_executor.execute_command("free -h | grep Mem", timeout=10)
        if mem_result['success']:
            info['memory'] = mem_result['stdout'].strip()

        output = "💻 System Information:\n\n"
        output += f"OS: {info.get('os', 'Unknown')}\n"
        output += f"Disk: {info.get('disk', 'Unknown')}\n"
        output += f"Memory: {info.get('memory', 'Unknown')}\n"

        return output

    except Exception as e:
        return f"❌ Error getting system info: {str(e)}"


@tool
def list_installed_packages(filter_term: Optional[str] = None) -> str:
    """
    List installed packages on the system.

    Use this to see what's already installed before installing new packages.

    Args:
        filter_term: Optional search term to filter results

    Returns:
        str: List of installed packages

    Examples:
        - list_installed_packages()
        - list_installed_packages("python")
        - list_installed_packages("editor")
    """
    try:
        if filter_term:
            cmd = f"dpkg -l | grep -i {filter_term} | head -n 20"
        else:
            cmd = "dpkg -l | head -n 30"

        result = secure_executor.execute_command(cmd, timeout=30)

        if result['success']:
            return f"📦 Installed packages:\n\n{result['stdout'][:1000]}"
        else:
            return "❌ Could not list packages"

    except Exception as e:
        return f"❌ Error listing packages: {str(e)}"


@tool
def update_package_lists() -> str:
    """
    Update apt package lists (run 'apt-get update').

    IMPORTANT: Always run this before installing packages to get the latest package information.

    Returns:
        str: Result of the update operation

    Examples:
        - update_package_lists()
    """
    try:
        result = secure_executor.execute_command("sudo apt-get update", timeout=120)

        if result['success']:
            return "✅ Package lists updated successfully\n\nYou can now install packages."
        else:
            return f"❌ Failed to update package lists:\n{result['stderr'][:300]}"

    except Exception as e:
        return f"❌ Update error: {str(e)}"


@tool
def check_disk_space() -> str:
    """
    Check available disk space on the system.

    Use this before installing large packages to ensure there's enough space.

    Returns:
        str: Disk space information

    Examples:
        - check_disk_space()
    """
    try:
        result = secure_executor.execute_command("df -h /", timeout=10)

        if result['success']:
            lines = result['stdout'].strip().split('\n')
            if len(lines) >= 2:
                header = lines[0]
                data = lines[1]
                return f"💾 Disk Space:\n\n{header}\n{data}"
            return result['stdout']
        else:
            return "❌ Could not check disk space"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# Export all tools (base + debugging)
ALL_TOOLS = [
    # Basic system tools
    execute_shell_command,
    verify_installation,
    search_package,
    get_system_info,
    list_installed_packages,
    update_package_lists,
    check_disk_space,
] + DEBUGGING_TOOLS  # Add debugging tools for self-healing capabilities
