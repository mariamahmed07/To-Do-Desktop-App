
import json
from pathlib import Path
from uuid import uuid4


class TaskManager:
    """Manage tasks and store them in a JSON file."""

    def __init__(self, storage_path="tasks.json"):
        self.storage_path = Path(storage_path)
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from disk, or start with an empty list."""
        if not self.storage_path.exists():
            self.tasks = []
            return

        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("The tasks file must contain a JSON list.")

            required_fields = {"id", "title", "completed", "created_at"}

            for task in data:
                if not isinstance(task, dict):
                    raise ValueError("Invalid task entry.")
                if not required_fields.issubset(task):
                    raise ValueError("A task is missing required fields.")
                if not isinstance(task["id"], str):
                    raise ValueError("Invalid task ID.")
                if not isinstance(task["title"], str) or not task["title"].strip():
                    raise ValueError("Invalid task title.")
                if not isinstance(task["completed"], bool):
                    raise ValueError("Invalid task status.")
                if not isinstance(task["created_at"], str):
                    raise ValueError("Invalid creation date.")

            self.tasks = data

        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(
                f"Could not read tasks from {self.storage_path}: {error}"
            ) from error

    def save_tasks(self):
        """Save all tasks to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = self.storage_path.with_name(
            self.storage_path.name + ".tmp"
        )

        try:
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(self.tasks, file, ensure_ascii=False, indent=4)
            temporary_path.replace(self.storage_path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    def add_task(self, title):
        """Add a task and return it."""
        title = title.strip()

        if not title:
            raise ValueError("Task title cannot be empty.")

        from datetime import datetime

        task = {
            "id": str(uuid4()),
            "title": title,
            "completed": False,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }

        self.tasks.append(task)
        self.save_tasks()
        return task.copy()

    def edit_task(self, task_id, new_title):
        """Change the title of an existing task."""
        new_title = new_title.strip()

        if not new_title:
            raise ValueError("Task title cannot be empty.")

        task = self._find_task(task_id)
        task["title"] = new_title
        self.save_tasks()
        return task.copy()

    def delete_task(self, task_id):
        """Delete a task by its ID."""
        task = self._find_task(task_id)
        self.tasks.remove(task)
        self.save_tasks()
        return task.copy()

    def toggle_task(self, task_id):
        """Switch a task between completed and incomplete."""
        task = self._find_task(task_id)
        task["completed"] = not task["completed"]
        self.save_tasks()
        return task.copy()

    def get_tasks(self, status="all"):
        """Return tasks filtered by status."""
        if status == "all":
            result = self.tasks
        elif status == "completed":
            result = [task for task in self.tasks if task["completed"]]
        elif status == "pending":
            result = [task for task in self.tasks if not task["completed"]]
        else:
            raise ValueError("Status must be all, completed, or pending.")

        return [task.copy() for task in result]

    def get_stats(self):
        """Return total, completed, and pending task counts."""
        total = len(self.tasks)
        completed = sum(task["completed"] for task in self.tasks)

        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
        }

    def _find_task(self, task_id):
        """Find a task or raise an error if it doesn't exist."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task

        raise KeyError(f"Task not found: {task_id}")
