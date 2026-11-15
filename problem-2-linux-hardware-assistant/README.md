# Linux Hardware Q&A Assistant

## Overview
A command-line assistant that answers questions about Linux hardware using system utilities and system files.

## Features
- CPU information using lscpu
- RAM information using free and /proc/meminfo
- Disk information using lsblk
- GPU information using lspci when available
- Operating system information
- Interactive question-and-answer interface

## Safety
- Uses predefined, allow-listed commands.
- Does not execute arbitrary shell commands.
- Uses subprocess with shell=False.
- Applies command timeouts.
- Does not require root privileges for normal operation.
- Reads system information without modifying hardware settings.

## Requirements
- Python 3.10 or newer
- Linux environment
- Pytest

## Installation
1. Create a virtual environment:
   python3 -m venv .venv

2. Activate it:
   source .venv/bin/activate

3. Install dependencies:
   python -m pip install -r requirements.txt

## Run the Assistant
   python -m app.assistant

Example questions:
- What is my CPU?
- How much RAM do I have?
- What is my disk storage?
- What operating system am I using?

Type exit to close the assistant.

## Run Tests
   python -m pytest -v

Tests use mocked system outputs to verify hardware information handling and safe command execution.

## Limitations
- Uses deterministic question matching, not an LLM.
- Hardware visibility depends on the Linux environment.
- Some hardware details may not be available in WSL2 or virtual machines.

## Author
NxtWave AI Engineering Assignment
