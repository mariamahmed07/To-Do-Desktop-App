
# TaskFlow — To-Do Desktop App

A desktop task management application built with Python and Tkinter to help users organize their daily tasks efficiently.

## Features

- Add new tasks
- Edit existing tasks
- Delete tasks
- Mark tasks as completed or pending
- Filter tasks by status
- View task statistics
- Automatically save tasks locally
- Restore saved tasks when reopening the application
- Simple and user-friendly graphical interface

## Technologies Used

- Python
- Tkinter
- JSON
- unittest

## Project Structure

```text
To-Do Desktop App/
├── main.py
├── task_manager.py
├── test_task_manager.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3 with Tkinter support
- No third-party Python packages are required

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/mariamahmed07/To-Do-Desktop-App.git
```

### 2. Open the Project Directory

```bash
cd To-Do-Desktop-App
```

### 3. Run the Application

```bash
python main.py
```

If the `python` command does not work on Windows, run the application using your Python executable's full path.

## Running Tests

Run the following command to test the task management logic:

```bash
python -m unittest -v test_task_manager
```

The project includes 14 unit tests covering task creation, editing, deletion, completion, filtering, statistics, data persistence, and error handling.

## Data Storage

Tasks are saved locally in JSON format, allowing the application to restore them between sessions.

No online account or external database is required.

## Future Improvements

- Add task deadlines and priorities
- Add search functionality
- Support task categories
- Improve the interface with additional customization options

## Author

**Mariam Ahmed**

GitHub: [@mariamahmed07](https://github.com/mariamahmed07)
