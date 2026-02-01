
import argparse
from task_queue.queue_manager import QueueManager
from task_queue.task import TaskPriority, TaskStatus

# Simple ANSI colors
RESET = "\033[0m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"

STATUS_ICONS = {
    "pending": "🟡",
    "processing": "🔵",
    "done": "🟢",
    "completed": "🟢",
    "cancelled": "🔴",
}

manager = QueueManager()
manager.load("tasks.json")



def main():
    parser = argparse.ArgumentParser(
        prog="task",
        description="Task Queue CLI"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- add ---
    add_parser = subparsers.add_parser("add", help="Create a new task")
    add_parser.add_argument("description")
    add_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    add_parser.set_defaults(func=cmd_add)

    # --- list ---
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--pending", action="store_true")
    list_parser.add_argument("--processing", action="store_true")
    list_parser.add_argument("--done", action="store_true")
    list_parser.add_argument("--cancelled", action="store_true")
    list_parser.add_argument("--completed", action="store_true")
    list_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        help="Filter by priority"
    )
    list_parser.add_argument(
        "--sort",
        choices=["created", "updated", "priority"],
        help="Sort tasks"
    )
    list_parser.set_defaults(func=cmd_list)

    # --- next ---
    _next_parser = subparsers.add_parser("next")
    _next_parser.set_defaults(func=cmd_next)

    # --- start ---
    start_parser = subparsers.add_parser("start", help="Start a task")
    start_parser.add_argument("id")
    
    # --- complete ---
    complete_parser = subparsers.add_parser("complete", help="Complete a task")
    complete_parser.add_argument("id")

    # --- cancel ---
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a task")
    cancel_parser.add_argument("id")

    # --- save ---
    save_parser = subparsers.add_parser("save", help="Save tasks to file")
    save_parser.add_argument("file")

    # --- load ---
    load_parser = subparsers.add_parser("load", help="Load tasks from file")
    load_parser.add_argument("file")
    

    

    args = parser.parse_args()
    print(args)

    handle_command(args)
    


def cmd_add(args):
    priority_map = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
    }

    priority = priority_map[args.priority]
    task = manager.add_task(args.description, priority=priority)
    manager.save("tasks.json")
    print(f"Task created: {task.id} [{task.priority.name}]")
    
def cmd_list(args):
    tasks = manager._tasks

    if not tasks:
        print("No tasks found.")
        return

    # --- status filters ---
    status_filters = {
        "pending": TaskStatus.PENDING,
        "processing": TaskStatus.PROCESSING,
        "done": TaskStatus.DONE,
        "cancelled": TaskStatus.CANCELLED,
        "completed": TaskStatus.COMPLETED,
    }

    active_status_filters = [
        status_filters[name]
        for name in status_filters
        if getattr(args, name)
    ]

    if active_status_filters:
        tasks = [t for t in tasks if t.status in active_status_filters]

    # --- priority filter ---
    if args.priority:
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
        }
        selected_priority = priority_map[args.priority]
        tasks = [t for t in tasks if t.priority == selected_priority]

    # --- sorting ---
    if args.sort:
        if args.sort == "created":
            tasks = sorted(tasks, key=lambda t: t.created_at)
        elif args.sort == "updated":
            tasks = sorted(tasks, key=lambda t: t.updated_at)
        elif args.sort == "priority":
            tasks = sorted(tasks, key=lambda t: t.priority.value)

    # --- output ---
    if not tasks:
        print("No tasks match the filters.")
        return

    # Header
    print(f"{'STATUS':<20} {'PRIORITY':<10} DESCRIPTION")
    print("─" * 60)


    for task in tasks:
        status = format_status(task)
        priority = format_priority(task)

        print(f"{status:<20} {priority:<10} {task.description}")

def handle_command(args):
    if hasattr(args, "func"):
        args.func(args)
    else:
        print("No command provided. Use --help for usage.")
        
def format_status(task):
    status = task.status.value

    color = {
        "pending": YELLOW,
        "processing": BLUE,
        "done": GREEN,
        "completed": GREEN,
        "cancelled": RED,
    }.get(status, RESET)

    icon = STATUS_ICONS.get(status, "•")

    return f"{icon} {color}{status}{RESET}"

def format_priority(task):
    color = {
        "LOW": GREEN,
        "MEDIUM": YELLOW,
        "HIGH": RED,
    }.get(task.priority.name, RESET)

    return f"{color}{task.priority.name}{RESET}"

def cmd_next(args):
    tasks = manager._tasks

    # Filter only pending tasks
    pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]

    if not pending_tasks:
        print("No pending tasks available.")
        return

    # Sort by priority (HIGH > MEDIUM > LOW) and then by creation time
    sorted_tasks = sorted(
        pending_tasks,
        key=lambda t: (-t.priority.value, t.created_at)
    )

    next_task = sorted_tasks[1]

    # Visual formatting
    status = format_status(next_task)
    priority = format_priority(next_task)

    print("Next task:")
    print("─" * 60)
    print(f"{status:<20} {priority:<10} {next_task.description}")
    print(f"ID: {next_task.id}")


        
        
if __name__ == "__main__":
    main()



