from unittest.mock import patch, Mock

from app.hardware import run_safe_command, read_memory_info
from app.assistant import answer_question


def test_rejects_unapproved_command():
    result = run_safe_command("rm")
    assert result["available"] is False
    assert "not allowed" in result["error"]


def test_missing_command():
    with patch("app.hardware.shutil.which", return_value=None):
        result = run_safe_command("lscpu")
    assert result["available"] is False
    assert "not installed" in result["error"]


def test_safe_command_uses_no_shell():
    with patch("app.hardware.shutil.which", return_value="/usr/bin/lscpu"):
        with patch("app.hardware.subprocess.run") as mocked:
            mocked.return_value = Mock(
                returncode=0,
                stdout="CPU(s): 4",
                stderr="",
            )
            result = run_safe_command("lscpu")

    assert result["available"] is True
    assert "CPU(s): 4" in result["output"]
    assert mocked.call_args.kwargs["shell"] is False
    assert mocked.call_args.kwargs["timeout"] == 5


def test_cpu_question():
    data = {"cpu": {"available": True, "output": "CPU(s): 4"}}
    assert "CPU(s): 4" in answer_question("How many CPU cores?", data)


def test_memory_question():
    data = {
        "memory_proc": {
            "available": True,
            "data": {
                "MemTotal": "8000000 kB",
                "MemAvailable": "4000000 kB",
            },
        }
    }
    answer = answer_question("How much RAM do I have?", data)
    assert "8000000 kB" in answer


def test_unknown_question():
    answer = answer_question("Tell me a joke", {})
    assert "CPU" in answer
