# task_queue — A Minimalist, Test‑Driven CLI Task Workflow Manager

task_queue is a small but intentionally designed command‑line task manager built around three principles:

- Clarity — simple, explicit workflows

- Determinism — predictable state transitions

- Professional polish — clean architecture, tests, and documentation

This project is part of an ongoing exploration of CLI tooling, workflow automation, and maintainable Python architecture.

---

## 🚧 Project Status

This project is actively evolving.
The core architecture is stable and fully tested, but some CLI commands and UX details are still being refined.

### Current UI Preview 

Here is a preview of the current interface (work in progress): 

![Screenshot](screenshot.png)

If you explore the code, you may find:

- Commands that are being improved or reorganized

- Features that are intentionally minimal for now

- Areas marked for future expansion

- A CLI interface that will continue to evolve

Everything works end‑to‑end, but the project is not “finished” — it’s growing in public, intentionally.

---

## Features

### ✔ Task management

- Create tasks with priorities (HIGH, MEDIUM, LOW)

- Automatic timestamps and unique IDs

- State transitions: PENDING → PROCESSING → COMPLETED / CANCELLED

### ✔ Queue behavior

- Priority‑based selection

- FIFO ordering within the same priority

- Deterministic get_next_task() logic

### ✔ Persistence

- JSON‑based storage

- Full round‑trip serialization (save / load)

- Stable enum handling

### ✔ CLI interface

- Add tasks

- List tasks

- Complete or cancel tasks

- Fetch the next task

- Purge finished tasks

---

## Tests

The project includes a full test suite covering:

- Task lifecycle

- Priority ordering

- Queue behavior

- Persistence

- CLI‑related logic

- All tests currently pass.

---

## License

This project is licensed under the **MIT License**.

See the `LICENSE` file for full details.

---

## Usage

python -m task_queue.cli <command> [options]

### Examples

python -m task_queue.cli add "Comprar pan" --priority low
python -m task_queue.cli list
python -m task_queue.cli next
python -m task_queue.cli complete <task_id>
python -m task_queue.cli cancel <task_id>
python -m task_queue.cli purge

---

## Project Structure

task_queue/
│
├── cli.py               # CLI entrypoint
├── manager.py           # QueueManager logic
├── task.py              # Task model + enums
├── storage.py           # JSON persistence
│
└── tests/               # Full test suite

---

## Roadmap

- Planned improvements:

- Better CLI help and UX

- Richer filtering and sorting in list

- Optional colored output toggle

- Packaging for pip install task_queue

- More robust error handling

- Optional YAML backend

---

## Final Note

This repository is intentionally public even while evolving.
The goal is to document the process, not just the result — including architecture decisions, refactors, and the test‑driven workflow behind the scenes.