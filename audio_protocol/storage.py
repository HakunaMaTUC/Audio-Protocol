from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .schema import MeetingProtocol


class ProtocolStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS protocols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    project TEXT NOT NULL,
                    payload TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS critical_numbers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_id INTEGER NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    context TEXT NOT NULL,
                    speaker TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source_quote TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    FOREIGN KEY(protocol_id) REFERENCES protocols(id)
                );
                """
            )

    def save_protocol(self, protocol: MeetingProtocol) -> int:
        protocol.validate()
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO protocols (date, project, payload) VALUES (?, ?, ?)",
                (
                    protocol.metadata.date,
                    protocol.metadata.project,
                    json.dumps(protocol.to_dict()),
                ),
            )
            protocol_id = int(cur.lastrowid)
            cur.executemany(
                """
                INSERT INTO critical_numbers (
                  protocol_id, value, unit, context, speaker, timestamp, source_quote, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        protocol_id,
                        cn.value,
                        cn.unit,
                        cn.context,
                        cn.speaker,
                        cn.timestamp,
                        cn.source_quote,
                        cn.confidence,
                    )
                    for cn in protocol.critical_numbers
                ],
            )
            return protocol_id

    def query_numbers(
        self,
        question: str,
    ) -> list[dict]:
        q = f"%{question.lower()}%"
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT p.id AS protocol_id, p.date, p.project, n.value, n.unit, n.context,
                       n.speaker, n.timestamp, n.source_quote, n.confidence
                FROM critical_numbers n
                JOIN protocols p ON p.id = n.protocol_id
                WHERE LOWER(n.context) LIKE ?
                   OR LOWER(n.source_quote) LIKE ?
                   OR LOWER(p.project) LIKE ?
                ORDER BY p.date DESC, n.confidence DESC
                LIMIT 25
                """,
                (q, q, q),
            ).fetchall()
        return [dict(row) for row in rows]

