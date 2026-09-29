"""Todo API: FastAPI + SQLite. Also serves the React page (index.html)."""
import os
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Vercel's filesystem is read-only except /tmp (data there is temporary).
DB = Path("/tmp/todos.db") if os.environ.get("VERCEL") else Path(__file__).parent / "todos.db"
app = FastAPI(title="Todo API")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


with db() as c:  # create the table on first run
    c.execute("""CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0,
        category TEXT NOT NULL DEFAULT 'Personal',
        position INTEGER NOT NULL DEFAULT 0)""")


class TaskIn(BaseModel):
    title: str
    category: str = "Personal"


class TaskPatch(BaseModel):
    title: str | None = None
    done: bool | None = None
    category: str | None = None


class Order(BaseModel):
    ids: list[int]


def row(r):
    return {**dict(r), "done": bool(r["done"])}


@app.get("/api/tasks")
def list_tasks():
    with db() as c:
        return [row(r) for r in c.execute("SELECT * FROM tasks ORDER BY position, id")]


@app.post("/api/tasks", status_code=201)
def add_task(t: TaskIn):
    title = t.title.strip()
    if not title:
        raise HTTPException(400, "Title is required")
    with db() as c:
        pos = c.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM tasks").fetchone()[0]
        cur = c.execute("INSERT INTO tasks(title, category, position) VALUES (?,?,?)",
                        (title, t.category, pos))
        return row(c.execute("SELECT * FROM tasks WHERE id=?", (cur.lastrowid,)).fetchone())


@app.put("/api/tasks/order")
def reorder(o: Order):
    with db() as c:
        for pos, tid in enumerate(o.ids):
            c.execute("UPDATE tasks SET position=? WHERE id=?", (pos, tid))
    return {"ok": True}


@app.patch("/api/tasks/{tid}")
def update_task(tid: int, p: TaskPatch):
    with db() as c:
        cur = c.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
        if not cur:
            raise HTTPException(404, "Task not found")
        title = p.title.strip() if p.title is not None else cur["title"]
        done = int(p.done) if p.done is not None else cur["done"]
        cat = p.category if p.category is not None else cur["category"]
        c.execute("UPDATE tasks SET title=?, done=?, category=? WHERE id=?", (title, done, cat, tid))
        return row(c.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone())


@app.delete("/api/tasks/{tid}")
def delete_task(tid: int):
    with db() as c:
        c.execute("DELETE FROM tasks WHERE id=?", (tid,))
    return {"ok": True}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / "index.html")
