#!/usr/bin/env python3
"""
ETL-загрузчик: читает marketing_spend.csv и загружает в PostgreSQL.
Запускается как init-контейнер (loader) после healthy-статуса БД.
"""

import csv
import os
import sys
import time

import psycopg2

# --- Настройки из переменных окружения ---
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "marketing_db")
DB_USER = os.getenv("POSTGRES_USER", "marketing_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "changeme")
CSV_PATH = os.getenv("CSV_PATH", "/data/marketing_spend.csv")

DDL = """
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    campaign_id   INT PRIMARY KEY,
    date          DATE NOT NULL,
    channel       VARCHAR(50) NOT NULL,
    region        VARCHAR(50) NOT NULL,
    product       VARCHAR(50) NOT NULL,
    impressions   INT NOT NULL,
    clicks        INT NOT NULL,
    spend         INT NOT NULL,
    revenue       INT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_channel_date ON marketing_campaigns(channel, date);
"""


def wait_for_db(max_retries: int = 30, delay: int = 2) -> psycopg2.extensions.connection:
    """Ожидание готовности PostgreSQL."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT,
                dbname=DB_NAME, user=DB_USER, password=DB_PASS,
            )
            print(f"[loader] БД доступна (попытка {attempt})")
            return conn
        except psycopg2.OperationalError:
            print(f"[loader] Ожидание БД... ({attempt}/{max_retries})")
            time.sleep(delay)
    print("[loader] БД недоступна, завершение.")
    sys.exit(1)


def load_csv(conn: psycopg2.extensions.connection) -> int:
    """Загрузка CSV в таблицу marketing_campaigns."""
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM marketing_campaigns;")
    if cur.fetchone()[0] > 0:
        print("[loader] Таблица уже содержит данные — пропуск загрузки.")
        return 0

    count = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                """
                INSERT INTO marketing_campaigns
                    (campaign_id, date, channel, region, product, impressions, clicks, spend, revenue)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (campaign_id) DO NOTHING;
                """,
                (
                    int(row["campaign_id"]),
                    row["date"],
                    row["channel"],
                    row["region"],
                    row["product"],
                    int(row["impressions"]),
                    int(row["clicks"]),
                    int(row["spend"]),
                    int(row["revenue"]),
                ),
            )
            count += 1

    conn.commit()
    cur.close()
    print(f"[loader] Загружено {count} строк в таблицу marketing_campaigns.")
    return count


def main() -> None:
    conn = wait_for_db()
    try:
        load_csv(conn)
    finally:
        conn.close()
    print("[loader] Готово.")


if __name__ == "__main__":
    main()