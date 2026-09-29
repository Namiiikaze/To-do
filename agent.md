# agent.md

Guide for AI coding agents (and humans) working on this project.

## What this is
A beginner-friendly todo app. Add tasks, check them off, delete them, reorder them.

## Stack
- Backend: Python + FastAPI (`main.py`)
- Database: SQLite, file `todos.db` (auto-created on first run)
- Frontend: React 18 in a single file, `static/index.html` (loaded from a CDN with Babel, so there is no build step)
- FastAPI serves both the API (`/api/...`) and the page (`/`)

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
# open http://127.0.0.1:8000
```
API docs are at http://127.0.0.1:8000/docs

## API
| Method | Path | Purpose |
|---|---|---|
| GET | /api/tasks | List tasks, ordered by position |
| POST | /api/tasks | Create `{title, category}` |
| PATCH | /api/tasks/{id} | Update `title`, `done`, or `category` |
| PUT | /api/tasks/order | Save order: `{ids: [3,1,2]}` |
| DELETE | /api/tasks/{id} | Delete a task |

## Conventions
- Keep it simple: no extra dependencies unless truly needed.
- Backend: one file, plain `sqlite3`, parameterised queries only (never string-format SQL).
- Frontend: state lives in `App`; all server calls go through the `api()` helper.
- Responsive: layout breakpoint is 700px. Below it the sidebar becomes a chip row, drag handles are hidden and the ▲/▼ buttons are the way to reorder (touch screens can't drag).
- Categories are `Personal` and `Work` (the `CATS` object in `index.html`). Add new ones there.

## Ideas for next steps
Due dates, subtasks, tags, editing titles, user accounts, a real build step (Vite).

## Rules for agents
- Explain changes in plain language; the owner is a beginner.
- Test the API (`curl`) after backend changes and reload the page after frontend changes.
- Don't delete `todos.db` without asking, since it holds the user's tasks.
