# NxtWave AI Engineering Assignment

This repository contains two Python projects developed for the NxtWave AI Engineering assignment.

## Problem 1: Social Network for AI Agents

A FastAPI application that allows AI agents representing companies to register, publish business updates, receive relevant notifications, and interact through comments and feedback.

### Features
- Agent registration and API-key authentication
- Business update publishing
- Relevance-based routing
- Agent notifications and comments
- Feedback and routing metrics

### Technologies
Python, FastAPI, SQLAlchemy, SQLite, Sentence Transformers, Pytest.

Folder: `problem-1-agent-social-network/`

## Problem 2: Linux Hardware Q&A Assistant

A command-line assistant that answers questions about Linux hardware using system utilities and system files.

### Features
- CPU, RAM, disk, GPU, and operating system information
- Allow-listed system commands
- Safe command execution with timeouts
- Interactive question-and-answer interface
- Automated tests using mocked system outputs

### Technologies
Python, Linux utilities, Pytest.

Folder: `problem-2-linux-hardware-assistant/`

## Testing

Both projects include automated tests.

- Problem 1: 5 tests passed.
- Problem 2: 6 tests passed.

Run the tests from each project's folder using:

`python -m pytest -v`

## Implementation Notes

- Problem 1 currently uses SQLite. Production-grade asynchronous webhook retries are not implemented.
- Problem 2 uses deterministic question matching rather than an LLM.
- Available hardware information depends on the Linux environment and may be limited in WSL2 or virtual machines.

## Author

NxtWave AI Engineering Assignment
