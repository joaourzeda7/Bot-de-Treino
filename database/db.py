"""
Módulo de banco de dados para o bot de registro de treinos.

Usa SQLite local (treinos.db) - sem necessidade de servidor externo.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

# Caminho do banco - fica na raiz do projeto
DB_PATH = Path(__file__).parent.parent / "treinos.db"

# Tipos de série aceitos (normalizados)
TIPOS_SERIE = {
    "aquecimento": "aquecimento",
    "warm": "aquecimento",
    "warmup": "aquecimento",
    "preparatoria": "preparatoria",
    "preparatória": "preparatoria",
    "feeder": "preparatoria",
    "trabalho": "trabalho",
    "work": "trabalho",
}


@contextmanager
def get_connection():
    """Context manager para garantir que a conexão é sempre fechada."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def inicializar_banco():
    """Cria as tabelas do banco caso não existam. Chamar uma vez ao iniciar o bot."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercicio TEXT NOT NULL,
                tipo_serie TEXT NOT NULL,
                carga REAL NOT NULL,
                series INTEGER NOT NULL,
                repeticoes INTEGER NOT NULL,
                data_hora TEXT NOT NULL,
                texto_original TEXT
            )
        """)
        # Índices para acelerar consultas de relatório por exercício e por data
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_exercicio
            ON registros (user_id, exercicio)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_data
            ON registros (user_id, data_hora)
        """)


def inserir_registro(user_id: int, exercicio: str, tipo_serie: str,
                      carga: float, series: int, repeticoes: int,
                      texto_original: str = "") -> int:
    """Insere um novo registro de treino. Retorna o id do registro criado."""
    data_hora = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO registros
                (user_id, exercicio, tipo_serie, carga, series, repeticoes, data_hora, texto_original)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, exercicio.lower().strip(), tipo_serie, carga, series, repeticoes,
              data_hora, texto_original))
        return cursor.lastrowid


def buscar_registros_do_dia(user_id: int, data: datetime = None) -> list[sqlite3.Row]:
    """Retorna todos os registros de um usuário num dia específico (default: hoje)."""
    if data is None:
        data = datetime.now()
    data_str = data.strftime("%Y-%m-%d")

    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM registros
            WHERE user_id = ? AND data_hora LIKE ?
            ORDER BY data_hora ASC
        """, (user_id, f"{data_str}%"))
        return cursor.fetchall()


def buscar_historico_exercicio(user_id: int, exercicio: str) -> list[sqlite3.Row]:
    """Retorna todo o histórico de um exercício específico, ordenado por data."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM registros
            WHERE user_id = ? AND exercicio = ? AND tipo_serie = 'trabalho'
            ORDER BY data_hora ASC
        """, (user_id, exercicio.lower().strip()))
        return cursor.fetchall()


def buscar_todos_exercicios(user_id: int) -> list[str]:
    """Retorna a lista de exercícios distintos já registrados pelo usuário."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT DISTINCT exercicio FROM registros
            WHERE user_id = ?
            ORDER BY exercicio ASC
        """, (user_id,))
        return [row["exercicio"] for row in cursor.fetchall()]


def buscar_todos_registros(user_id: int) -> list[sqlite3.Row]:
    """Retorna todos os registros do usuário, do início, ordenados por data."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM registros
            WHERE user_id = ?
            ORDER BY data_hora ASC
        """, (user_id,))
        return cursor.fetchall()
