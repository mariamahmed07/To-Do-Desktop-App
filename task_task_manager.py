
import json
import tempfile
import unittest
from pathlib import Path

from task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name) / "test_tasks.json"
        self.manager = TaskManager(self.storage_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_starts_empty(self):
        self.assertEqual(self.manager.get_tasks(), [])
        self.assertEqual(
            self.manager.get_stats(),
            {"total": 0, "completed": 0, "pending": 0},
        )

    def test_add_task(self):
        task = self.manager.add_task("Study Python")

        self.assertEqual(task["title"], "Study Python")
        self.assertFalse(task["completed"])
        self.assertTrue(task["id"])
        self.assertTrue(self.storage_path.exists())

    def test_rejects_empty_task(self):
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

        self.assertEqual(self.manager.get_tasks(), [])

    def test_edit_task(self):
        task = self.manager.add_task("Old title")
        updated = self.manager.edit_task(task["id"], "New title")

        self.assertEqual(updated["title"], "New title")
        self.assertEqual(self.manager.get_tasks()[0]["title"], "New title")

    def test_rejects_empty_edit(self):
        task = self.manager.add_task("Keep this title")

        with self.assertRaises(ValueError):
            self.manager.edit_task(task["id"], "  ")

        self.assertEqual(
            self.manager.get_tasks()[0]["title"], "Keep this title"
        )

    def test_delete_task(self):
        task = self.manager.add_task("Delete me")
        deleted = self.manager.delete_task(task["id"])

        self.assertEqual(deleted["title"], "Delete me")
        self.assertEqual(self.manager.get_tasks(), [])

    def test_toggle_task(self):
        task = self.manager.add_task("Finish project")

        completed = self.manager.toggle_task(task["id"])
        self.assertTrue(completed["completed"])

        pending = self.manager.toggle_task(task["id"])
        self.assertFalse(pending["completed"])

    def test_filters(self):
        first = self.manager.add_task("Task one")
        self.manager.add_task("Task two")
        self.manager.toggle_task(first["id"])

        self.assertEqual(len(self.manager.get_tasks("all")), 2)
        self.assertEqual(len(self.manager.get_tasks("completed")), 1)
        self.assertEqual(len(self.manager.get_tasks("pending")), 1)

    def test_invalid_filter(self):
        with self.assertRaises(ValueError):
            self.manager.get_tasks("unknown")

    def test_stats(self):
        first = self.manager.add_task("Task one")
        self.manager.add_task("Task two")
        self.manager.toggle_task(first["id"])

        self.assertEqual(
            self.manager.get_stats(),
            {"total": 2, "completed": 1, "pending": 1},
        )

    def test_data_survives_reload(self):
        self.manager.add_task("Saved task")

        reloaded_manager = TaskManager(self.storage_path)

        self.assertEqual(
            reloaded_manager.get_tasks()[0]["title"], "Saved task"
        )

    def test_unknown_task_raises_error(self):
        for operation in (
            lambda: self.manager.edit_task("missing", "New title"),
            lambda: self.manager.delete_task("missing"),
            lambda: self.manager.toggle_task("missing"),
        ):
            with self.subTest(operation=operation):
                with self.assertRaises(KeyError):
                    operation()

    def test_corrupted_json_raises_error(self):
        self.storage_path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            TaskManager(self.storage_path)

    def test_invalid_task_structure_raises_error(self):
        self.storage_path.write_text(
            json.dumps([{"id": "123", "title": "Missing fields"}]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            TaskManager(self.storage_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
