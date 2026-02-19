import pandas as pd
import numpy as np
from datetime import datetime

def calculate_roi():
    """
    Заглушка для расчета ROI на основе тестовых данных
    """
    crm_data = pd.DataFrame({
        'date': ['2026-02-01', '2026-02-01', '2026-02-01', '2026-02-02', '2026-02-02'],
        'source': ['google', 'yandex', 'facebook', 'google', 'yandex'],
        'revenue': [15000, 8200, 5300, 12400, 9100]
    })
    
    ads_data = pd.DataFrame({
        'date': ['2026-02-01', '2026-02-01', '2026-02-01', '2026-02-02', '2026-02-02'],
        'source': ['google', 'yandex', 'facebook', 'google', 'yandex'],
        'spend': [5000, 3000, 2000, 4500, 3200]
    })
    # Объединение данных
    merged = pd.merge(crm_data, ads_data, on=['date', 'source'])
    
    #Расчет ROI
    merged['profit'] = merged['revenue'] - merged['spend']
    merged['roi'] = round((merged['profit'] / merged['spend']) * 100, 2)
    
    # Вывод результатов
    print("\nАггрегированные данные по источникам:")
    print(merged.to_string(index=False))
    
    # Сводка по источникам
    summary = merged.groupby('source').agg({
        'spend': 'sum',
        'revenue': 'sum',
        'profit': 'sum',
        'roi': 'mean'
    }).round(2)
    
    print("\nROI по каналам:")
    print(summary.to_string())
    
    return merged

if __name__ == "__main__":
    result = calculate_roi()
