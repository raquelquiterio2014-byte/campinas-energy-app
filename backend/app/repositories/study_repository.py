from __future__ import annotations
import json
import sqlite3
from pathlib import Path

class DuplicateStudyError(Exception):
    pass

class StudyRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def initialize(self) -> None:
        with self._connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS studies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feeder TEXT NOT NULL,
                    study_code TEXT NOT NULL,
                    phase TEXT,
                    network_element_id TEXT,
                    length_km REAL NOT NULL CHECK(length_km >= 0),
                    selected_point TEXT NOT NULL,
                    connection_point TEXT NOT NULL,
                    connection_line TEXT NOT NULL,
                    crs TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(feeder, study_code)
                )
            """)

    @staticmethod
    def _row_to_dict(row):
        if row is None:
            return None
        item = dict(row)
        for key in ("selected_point", "connection_point", "connection_line"):
            item[key] = json.loads(item[key])
        return item

    def save(self, study: dict) -> dict:
        try:
            with self._connect() as con:
                con.execute("""
                    INSERT INTO studies (
                        feeder, study_code, phase, network_element_id, length_km,
                        selected_point, connection_point, connection_line, crs
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    study["feeder"], study["study_code"], study.get("phase"),
                    str(study["network_element_id"]) if study.get("network_element_id") is not None else None,
                    study["length_km"],
                    json.dumps(study["selected_point"]),
                    json.dumps(study["connection_point"]),
                    json.dumps(study["connection_line"]),
                    study["crs"],
                ))
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise DuplicateStudyError from exc
            raise
        return self.get(study["feeder"], study["study_code"])

    def get(self, feeder: str, study_code: str):
        with self._connect() as con:
            row = con.execute(
                "SELECT * FROM studies WHERE feeder = ? AND study_code = ?",
                (feeder.upper(), study_code),
            ).fetchone()
        return self._row_to_dict(row)

    def list_for_feeder(self, feeder: str):
        with self._connect() as con:
            rows = con.execute(
                """SELECT id, feeder, study_code, phase, network_element_id,
                          length_km, crs, created_at
                   FROM studies WHERE feeder = ? ORDER BY created_at, id""",
                (feeder.upper(),),
            ).fetchall()
        return [dict(row) for row in rows]
