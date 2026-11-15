import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

ALLOWED_COMMANDS = {
    "lscpu": ["lscpu", "-J"],
    "lsblk": ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"],
    "free": ["free", "-b"],
    "lspci": ["lspci"],
}

TIMEOUT_SECONDS = 5


def run_safe_command(name):
    """Run only a predefined, read-only hardware command."""
    if name not in ALLOWED_COMMANDS:
        return {"available": False, "error": "Command not allowed"}

    executable = shutil.which(name)
    if not executable:
        return {"available": False, "error": f"{name} is not installed"}

    args = ALLOWED_COMMANDS[name].copy()
    args[0] = executable

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            shell=False,
            check=False,
        )
        if result.returncode != 0:
            return {
                "available": False,
                "error": result.stderr.strip() or "Command failed",
            }

        return {"available": True, "output": result.stdout.strip()}

    except subprocess.TimeoutExpired:
        return {"available": False, "error": "Command timed out"}
    except OSError as exc:
        return {"available": False, "error": str(exc)}


def read_memory_info():
    """Read memory information from /proc/meminfo."""
    info = {}
    path = Path("/proc/meminfo")

    try:
        for line in path.read_text().splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            info[key] = value.strip()
        return {"available": True, "data": info}
    except OSError as exc:
        return {"available": False, "error": str(exc)}


def read_os_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or "Not reported",
        "python_version": platform.python_version(),
    }


def collect_hardware_info():
    """Collect a structured, read-only hardware snapshot."""
    commands = {
        name: run_safe_command(name)
        for name in ALLOWED_COMMANDS
    }

    return {
        "os": read_os_info(),
        "cpu": commands["lscpu"],
        "storage": commands["lsblk"],
        "memory_command": commands["free"],
        "memory_proc": read_memory_info(),
        "pci_devices": commands["lspci"],
    }


if __name__ == "__main__":
    print(json.dumps(collect_hardware_info(), indent=2))
