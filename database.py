"""Camada simples de persistência de tarefas em SQLite."""

import sqlite3
from pathlib import Path
from typing import Any


DATABASE_PATH = Path(__file__).resolve().parent / "tasks.db"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão com o banco local."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Cria a tabela de tarefas, caso ainda não exista."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def create_task(title: str) -> dict[str, Any]:
    """Salva uma tarefa e retorna os dados gravados."""
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,),
        )
        row = connection.execute(
            "SELECT id, title, completed, created_at FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return _row_to_task(row)


def list_tasks() -> list[dict[str, Any]]:
    """Retorna todas as tarefas, da mais antiga para a mais nova."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, completed, created_at FROM tasks ORDER BY id"
        ).fetchall()

    return [_row_to_task(row) for row in rows]


def update_task_completed(task_id: int, completed: bool) -> dict[str, Any] | None:
    """Atualiza o estado completed de uma tarefa existente."""
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (int(completed), task_id),
        )
        if cursor.rowcount == 0:
            return None

        row = connection.execute(
            "SELECT id, title, completed, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return _row_to_task(row)


def delete_task(task_id: int) -> bool:
    """Exclui uma tarefa e informa se ela existia."""
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    return cursor.rowcount > 0


def _row_to_task(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
    }
