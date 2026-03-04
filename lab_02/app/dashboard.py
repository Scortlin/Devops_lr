#!/usr/bin/env python3
"""
Dash-приложение: Дашборд эффективности маркетинговых трат (ROI).
Вариант 7 — Маркетинговая аналитика.
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import psycopg2

# --- Подключение к БД ---
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "marketing_db")
DB_USER = os.getenv("POSTGRES_USER", "marketing_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "changeme")

# --- Инициализация Dash приложения ---
app = Dash(__name__)
server = app.server  # для gunicorn

# --- Функция загрузки данных ---
def load_data():
    """Загрузка данных из PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT,
            dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        )
        # Вычисление ROI прямо в SQL запросе
        query = """
        SELECT 
            *,
            CASE 
                WHEN spend > 0 THEN ((revenue - spend)::float / spend::float) * 100
                ELSE 0 
            END as roi_percent
        FROM marketing_campaigns;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame() # Возвращение пустого DataFrame в случае ошибки

# --- Layout приложения ---
app.layout = html.Div([
    html.H1("Маркетинговая аналитика: Эффективность трат (ROI)", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Выберите канал:"),
            dcc.Dropdown(
                id='channel-dropdown',
                multi=True,
                placeholder="Все каналы"
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Выберите продукт:"),
            dcc.Dropdown(
                id='product-dropdown',
                multi=True,
                placeholder="Все продукты"
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    html.Div([
        dcc.Graph(id='roi-by-channel-graph'),
    ]),

    html.Div([
        dcc.Graph(id='spend-vs-revenue-graph'),
    ]),

    html.Div([
        dcc.Graph(id='roi-trend-over-time'),
    ]),

    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 1 minute
        n_intervals=0
    )
])

# --- Callback для обновления опций Dropdown ---
@app.callback(
    [Output('channel-dropdown', 'options'),
     Output('product-dropdown', 'options')],
    [Input('interval-component', 'n_intervals')]
)
def update_dropdowns(n):
    df = load_data()
    if df.empty:
        return [], []
    channel_options = [{'label': i, 'value': i} for i in sorted(df['channel'].unique())]
    product_options = [{'label': i, 'value': i} for i in sorted(df['product'].unique())]
    return channel_options, product_options

# --- Callback для обновления графиков ---
@app.callback(
    [Output('roi-by-channel-graph', 'figure'),
     Output('spend-vs-revenue-graph', 'figure'),
     Output('roi-trend-over-time', 'figure')],
    [Input('channel-dropdown', 'value'),
     Input('product-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graphs(selected_channels, selected_products, n):
    df = load_data()
    if df.empty:
        no_data_fig = go.Figure()
        no_data_fig.add_annotation(text="Нет данных или ошибка подключения к БД", showarrow=False)
        return no_data_fig, no_data_fig, no_data_fig

    # Фильтрация данных
    filtered_df = df.copy()
    if selected_channels and len(selected_channels) > 0:
        filtered_df = filtered_df[filtered_df['channel'].isin(selected_channels)]
    if selected_products and len(selected_products) > 0:
        filtered_df = filtered_df[filtered_df['product'].isin(selected_products)]

    if filtered_df.empty:
        no_data_fig = go.Figure()
        no_data_fig.add_annotation(text="Нет данных для выбранных фильтров", showarrow=False)
        return no_data_fig, no_data_fig, no_data_fig

    # 1. График ROI по каналам
    roi_by_channel = filtered_df.groupby('channel')['roi_percent'].mean().reset_index().sort_values('roi_percent', ascending=False)
    fig_roi_channel = px.bar(roi_by_channel, x='channel', y='roi_percent',
                              title='Средний ROI по каналам (%)',
                              color='roi_percent', color_continuous_scale='RdYlGn',
                              labels={'channel': 'Канал', 'roi_percent': 'ROI (%)'})

    # 2. Scatter plot: Траты vs Выручка
    fig_spend_revenue = px.scatter(filtered_df, x='spend', y='revenue', color='channel',
                                    size='clicks', hover_data=['campaign_id', 'product'],
                                    title='Зависимость Выручки от Трат',
                                    labels={'spend': 'Траты (усл. ед.)', 'revenue': 'Выручка (усл. ед.)'})

    max_val = max(filtered_df['spend'].max(), filtered_df['revenue'].max())
    fig_spend_revenue.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val], mode='lines',
                                            line=dict(dash='dash', color='grey'), name='y=x'))

    # 3. Тренд ROI во времени
    df_time = filtered_df.copy()
    df_time['date'] = pd.to_datetime(df_time['date'])
    roi_over_time = df_time.groupby([pd.Grouper(key='date', freq='W-MON'), 'channel'])['roi_percent'].mean().reset_index()
    fig_trend = px.line(roi_over_time, x='date', y='roi_percent', color='channel',
                         title='Динамика среднего ROI (по неделям)',
                         labels={'date': 'Дата', 'roi_percent': 'ROI (%)', 'channel': 'Канал'})

    return fig_roi_channel, fig_spend_revenue, fig_trend


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)