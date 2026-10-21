
import tkinter as tk
from tkinter import ttk, messagebox

from task_manager import TaskManager


# ---------- Colors and styling ----------

BG = "#F4F6FB"
CARD = "#FFFFFF"
PRIMARY = "#4F46E5"
PRIMARY_HOVER = "#4338CA"
TEXT = "#20243A"
MUTED = "#747B91"
GREEN = "#16845B"
RED = "#D64545"
BORDER = "#E5E8F0"


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow | To-Do App")
        self.root.geometry("900x700")
        self.root.minsize(720, 600)
        self.root.configure(bg=BG)

        self.manager = TaskManager()
        self.current_filter = tk.StringVar(value="all")
        self.selected_task_id = None
        self.title_input = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready to plan your day.")

        self._configure_styles()
        self._build_ui()
        self.refresh_tasks()

        self.root.bind("<Return>", self._handle_enter)
        self.root.bind("<Escape>", lambda event: self._clear_form())

    def _configure_styles(self):
        style = ttk.Style()

        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Task.Treeview",
            background=CARD,
            fieldbackground=CARD,
            foreground=TEXT,
            rowheight=38,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Task.Treeview.Heading",
            background="#EEF0F8",
            foreground=TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Task.Treeview",
            background=[("selected", "#E4E4FF")],
            foreground=[("selected", TEXT)],
        )

    def _build_ui(self):
        # Main page
        page = tk.Frame(self.root, bg=BG, padx=28, pady=22)
        page.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(page, bg=BG)
        header.pack(fill="x", pady=(0, 22))

        tk.Label(
            header,
            text="TaskFlow",
            font=("Segoe UI", 25, "bold"),
            fg=PRIMARY,
            bg=BG,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="A little progress every day adds up.",
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG,
        ).pack(anchor="w", pady=(3, 0))

        # Statistics
        stats_frame = tk.Frame(page, bg=BG)
        stats_frame.pack(fill="x", pady=(0, 20))

        self.total_value = self._create_stat_card(
            stats_frame, "TOTAL TASKS", "0", PRIMARY
        )
        self.pending_value = self._create_stat_card(
            stats_frame, "TO DO", "0", RED
        )
        self.completed_value = self._create_stat_card(
            stats_frame, "COMPLETED", "0", GREEN
        )

        # Task entry card
        form = tk.Frame(
            page, bg=CARD, padx=18, pady=17,
            highlightbackground=BORDER, highlightthickness=1
        )
        form.pack(fill="x", pady=(0, 18))

        tk.Label(
            form,
            text="YOUR NEXT TASK",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=CARD,
        ).pack(anchor="w", pady=(0, 9))

        entry_row = tk.Frame(form, bg=CARD)
        entry_row.pack(fill="x")

        self.task_entry = tk.Entry(
            entry_row,
            textvariable=self.title_input,
            font=("Segoe UI", 11),
            bg="#F8F9FD",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=PRIMARY,
        )
        self.task_entry.pack(side="left", fill="x", expand=True, ipady=10)
        self.task_entry.insert(0, "")

        self.add_button = tk.Button(
            entry_row,
            text="＋ Add Task",
            command=self.add_task,
            bg=PRIMARY,
            fg="white",
            activebackground=PRIMARY_HOVER,
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8,
        )
        self.add_button.pack(side="left", padx=(10, 0))

        self.form_hint = tk.Label(
            form,
            text="Tip: select a task below to edit, complete, or delete it.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=CARD,
        )
        self.form_hint.pack(anchor="w", pady=(10, 0))

        # Task list card
        list_card = tk.Frame(
            page, bg=CARD, padx=16, pady=15,
            highlightbackground=BORDER, highlightthickness=1
        )
        list_card.pack(fill="both", expand=True)

        list_header = tk.Frame(list_card, bg=CARD)
        list_header.pack(fill="x", pady=(0, 12))

        tk.Label(
            list_header,
            text="My Tasks",
            font=("Segoe UI", 15, "bold"),
            fg=TEXT,
            bg=CARD,
        ).pack(side="left")

        filter_frame = tk.Frame(list_header, bg=CARD)
        filter_frame.pack(side="right")

        filters = [
            ("All", "all"),
            ("To Do", "pending"),
            ("Completed", "completed"),
        ]

        for label, value in filters:
            tk.Radiobutton(
                filter_frame,
                text=label,
                value=value,
                variable=self.current_filter,
                command=self.refresh_tasks,
                bg=CARD,
                fg=MUTED,
                selectcolor="#E9E8FF",
                activebackground=CARD,
                font=("Segoe UI", 9),
                cursor="hand2",
            ).pack(side="left", padx=(4, 0))

        table_frame = tk.Frame(list_card, bg=CARD)
        table_frame.pack(fill="both", expand=True)

        columns = ("status", "title", "created")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Task.Treeview",
            selectmode="browse",
        )

        self.tree.heading("status", text="STATUS")
        self.tree.heading("title", text="TASK")
        self.tree.heading("created", text="CREATED")

        self.tree.column("status", width=100, anchor="center", stretch=False)
        self.tree.column("title", width=380, anchor="w")
        self.tree.column("created", width=155, anchor="center", stretch=False)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("completed", foreground=GREEN)
        self.tree.tag_configure("pending", foreground=TEXT)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda event: self.toggle_selected())

        # Action buttons
        actions = tk.Frame(list_card, bg=CARD)
        actions.pack(fill="x", pady=(14, 0))

        self._button(actions, "✓ Complete / Undo", self.toggle_selected,
                     "#E8F6EF", GREEN).pack(side="left", padx=(0, 7))
        self._button(actions, "✎ Edit", self.edit_selected,
                     "#EEEEFF", PRIMARY).pack(side="left", padx=(0, 7))
        self._button(actions, "Delete", self.delete_selected,
                     "#FCECEC", RED).pack(side="left")

        self._button(actions, "Clear Input", self._clear_form,
                     "#F0F2F7", MUTED).pack(side="right")

        # Footer
        tk.Label(
            page,
            textvariable=self.status_text,
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=BG,
        ).pack(anchor="w", pady=(12, 0))

    def _create_stat_card(self, parent, label, initial_value, color):
        card = tk.Frame(
            parent, bg=CARD, padx=16, pady=13,
            highlightbackground=BORDER, highlightthickness=1
        )
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Label(
            card, text=label, font=("Segoe UI", 8, "bold"),
            fg=MUTED, bg=CARD
        ).pack(anchor="w")

        value = tk.Label(
            card, text=initial_value, font=("Segoe UI", 21, "bold"),
            fg=color, bg=CARD
        )
        value.pack(anchor="w", pady=(4, 0))
        return value

    def _button(self, parent, text, command, bg, fg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=11,
            pady=8,
        )

    def _handle_enter(self, event):
        if self.root.focus_get() == self.task_entry:
            self.add_task()

    def add_task(self):
        title = self.title_input.get().strip()

        if not title:
            messagebox.showwarning(
                "Empty task", "Please type a task before adding it.",
                parent=self.root
            )
            self.task_entry.focus_set()
            return

        try:
            task = self.manager.add_task(title)
            self.current_filter.set("all")
            self._clear_form()
            self.refresh_tasks()
            self._select_task(task["id"])
            self.status_text.set("Task added successfully.")
        except (ValueError, OSError) as error:
            messagebox.showerror("Could not save task", str(error),
                                 parent=self.root)

    def edit_selected(self):
        task_id = self._get_selected_id()

        if not task_id:
            messagebox.showinfo(
                "Select a task", "Select a task from the list first.",
                parent=self.root
            )
            return

        new_title = self.title_input.get().strip()

        if not new_title:
            messagebox.showwarning(
                "Empty title", "Type the new task title in the input box.",
                parent=self.root
            )
            self.task_entry.focus_set()
            return

        try:
            self.manager.edit_task(task_id, new_title)
            self._clear_form()
            self.refresh_tasks()
            self._select_task(task_id)
            self.status_text.set("Task updated successfully.")
        except (KeyError, ValueError, OSError) as error:
            messagebox.showerror("Could not edit task", str(error),
                                 parent=self.root)

    def delete_selected(self):
        task_id = self._get_selected_id()

        if not task_id:
            messagebox.showinfo(
                "Select a task", "Select a task to delete first.",
                parent=self.root
            )
            return

        task = next(
            (item for item in self.manager.get_tasks()
             if item["id"] == task_id),
            None,
        )

        if task is None:
            self.refresh_tasks()
            return

        confirm = messagebox.askyesno(
            "Delete task",
            f"Are you sure you want to delete:\n\n{task['title']}?",
            parent=self.root,
        )

        if not confirm:
            return

        try:
            self.manager.delete_task(task_id)
            self._clear_form()
            self.refresh_tasks()
            self.status_text.set("Task deleted.")
        except (KeyError, OSError) as error:
            messagebox.showerror("Could not delete task", str(error),
                                 parent=self.root)

    def toggle_selected(self):
        task_id = self._get_selected_id()

        if not task_id:
            messagebox.showinfo(
                "Select a task", "Select a task to update its status.",
                parent=self.root
            )
            return

        try:
            task = self.manager.toggle_task(task_id)
            self.refresh_tasks()

            if self.current_filter.get() == "all" or (
                self.current_filter.get() == "completed" and task["completed"]
            ) or (
                self.current_filter.get() == "pending" and not task["completed"]
            ):
                self._select_task(task_id)

            self.status_text.set(
                "Task marked completed." if task["completed"]
                else "Task marked as to do."
            )
        except (KeyError, OSError) as error:
            messagebox.showerror("Could not update task", str(error),
                                 parent=self.root)

    def refresh_tasks(self):
        selected_id = self._get_selected_id()

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            tasks = self.manager.get_tasks(self.current_filter.get())
        except ValueError as error:
            messagebox.showerror("Invalid filter", str(error),
                                 parent=self.root)
            return

        for task in tasks:
            completed = task["completed"]
            status = "✓ Done" if completed else "○ To Do"
            created = task["created_at"].replace("T", " ")

            self.tree.insert(
                "",
                "end",
                iid=task["id"],
                values=(status, task["title"], created),
                tags=("completed" if completed else "pending",),
            )

        stats = self.manager.get_stats()
        self.total_value.config(text=str(stats["total"]))
        self.pending_value.config(text=str(stats["pending"]))
        self.completed_value.config(text=str(stats["completed"]))

        if selected_id and self.tree.exists(selected_id):
            self._select_task(selected_id)

    def _on_select(self, event=None):
        task_id = self._get_selected_id()
        if not task_id:
            return

        self.selected_task_id = task_id
        task = next(
            (item for item in self.manager.get_tasks()
             if item["id"] == task_id),
            None,
        )
        if task:
            self.title_input.set(task["title"])
            self.form_hint.config(
                text="Selected task loaded. Change its title, then click Edit."
            )

    def _get_selected_id(self):
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _select_task(self, task_id):
        if self.tree.exists(task_id):
            self.tree.selection_set(task_id)
            self.tree.focus(task_id)
            self.tree.see(task_id)
            self.selected_task_id = task_id

    def _clear_form(self):
        self.title_input.set("")
        self.selected_task_id = None
        if hasattr(self, "tree"):
            for item in self.tree.selection():
                self.tree.selection_remove(item)
        if hasattr(self, "form_hint"):
            self.form_hint.config(
                text="Tip: select a task below to edit, complete, or delete it."
            )
        if hasattr(self, "task_entry"):
            self.task_entry.focus_set()


def main():
    root = tk.Tk()
    try:
        TodoApp(root)
    except (OSError, ValueError) as error:
        messagebox.showerror(
            "TaskFlow could not start",
            f"The tasks file could not be loaded.\n\n{error}",
            parent=root,
        )
        root.destroy()
        return

    root.mainloop()


if __name__ == "__main__":
    main()
