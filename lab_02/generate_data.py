#!/usr/bin/env python3
"""
Генератор синтетических данных: Эффективность маркетинговых трат (ROI).
Вариант 7 — Анализ эффективности маркетинговых трат.
"""

import csv
import os
import random
from datetime import datetime, timedelta

SEED = 42
NUM_ROWS = 2000  # Количество записей о кампаниях
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "marketing_spend.csv")

# --- Параметры генерации ---
CHANNELS = ["Social Media", "Google Ads", "Email", "TV", "Billboard", "Partners"]
REGIONS = ["North", "South", "East", "West", "Central"]
PRODUCTS = ["Product_A", "Product_B", "Product_C", "Product_D"]

random.seed(SEED)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def random_date(start: datetime, end: datetime) -> datetime:
    """Генерирует случайную дату в диапазоне."""
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def generate() -> None:
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)

    fieldnames = [
        "campaign_id",
        "date",
        "channel",
        "region",
        "product",
        "impressions",
        "clicks",
        "spend",
        "revenue",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, NUM_ROWS + 1):
            campaign_date = random_date(start_date, end_date)
            channel = random.choice(CHANNELS)
            region = random.choice(REGIONS)
            product = random.choice(PRODUCTS)

            # Логика генерации метрик
            impressions = random.randint(1000, 100000)
            ctr = random.uniform(0.01, 0.15)
            clicks = int(impressions * ctr)

            # Стоимость зависит от канала
            channel_cost_multiplier = {
                "TV": 0.8, "Billboard": 0.6, "Google Ads": 1.2,
                "Social Media": 0.9, "Email": 0.3, "Partners": 0.7
            }
            spend = int(clicks * random.uniform(0.5, 2.5) * channel_cost_multiplier.get(channel, 1))

            revenue_multiplier = random.uniform(1.5, 4.0)
            revenue = int(spend * revenue_multiplier * random.uniform(0.7, 1.3))

            writer.writerow({
                "campaign_id": i,
                "date": campaign_date.strftime("%Y-%m-%d"),
                "channel": channel,
                "region": region,
                "product": product,
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "revenue": revenue,
            })

    print(f"Сгенерировано {NUM_ROWS} записей → {OUTPUT_FILE}")

if __name__ == "__main__":
    generate()