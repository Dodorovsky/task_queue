
import argparse
from task_queue.queue_manager import QueueManager
from task_queue.task import TaskPriority, TaskStatus


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
    subparsers.add_parser("next", help="Show next task by priority")

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

    for task in tasks:
        print(f"{task.id} | {task.status.value} | {task.priority.name} | {task.description}")



def handle_command(args):
    if hasattr(args, "func"):
        args.func(args)
    else:
        print("No command provided. Use --help for usage.")
        
if __name__ == "__main__":
    main()



