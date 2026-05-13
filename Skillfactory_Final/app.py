import streamlit as st
import sqlite3
import polars as pl
import plotly.express as px
from datetime import date

DB_PATH = "data/weather.db"

st.set_page_config(page_title="WeatherInsight", layout="wide")
st.title("🌦️ WeatherInsight: Погодные тренды")

@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pl.read_database("SELECT * FROM weather ORDER BY date", conn)
        conn.close()
        
        # Если колонка date — это строки, преобразуем их с указанием формата
        if df["date"].dtype == pl.Utf8:
            try:
                # Попробуем стандартный формат ISO (ГГГГ-ММ-ДД)
                df = df.with_columns(pl.col("date").str.to_date(format="%Y-%m-%d"))
            except Exception:
                # Если в данных есть время (ГГГГ-ММ-ДД ЧЧ:ММ:СС), пробуем этот вариант
                df = df.with_columns(pl.col("date").str.to_datetime().dt.date())
            
        return df
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        st.stop()

df = load_data()

# --- Блок фильтров в боковой панели ---
st.sidebar.header("Фильтры")

# 1. Фильтрация по календарю
min_date = df["date"].min()
max_date = df["date"].max()

date_range = st.sidebar.date_input(
    "Выберите диапазон дат",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="weather_date_range" # Добавляем ключ для стабильности виджета
)

# 2. Фильтрация по городу
# Используем unique().sort() чтобы список всегда был в одном порядке
cities = df["city"].unique().sort().to_list()

# Ключевой момент: убираем default=cities, если хотим, чтобы выбор не "залипал", 
# или оставляем, но проверяем логику ниже.
selected_cities = st.sidebar.multiselect(
    "Выберите города", 
    options=cities, 
    default=cities,
    key="city_selector"
)

# --- Применение фильтров ---

# Создаем копию для фильтрации
f_df = df

# Фильтр по датам
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    f_df = f_df.filter((pl.col("date") >= start_date) & (pl.col("date") <= end_date))

# Фильтр по городам (важно: если список пуст, показываем пустоту или всё)
if selected_cities:
    f_df = f_df.filter(pl.col("city").is_in(selected_cities))
else:
    # Если города не выбраны, технически DataFrame должен быть пустым
    f_df = f_df.filter(pl.col("city") == "NON_EXISTENT_CITY") 

filtered_df = f_df

# --- Вывод статистики ---
st.subheader("📊 Общая статистика")
c1, c2, c3 = st.columns(3)
c1.metric("Записей найдено", len(filtered_df))
c2.metric("Городов выбрано", filtered_df["city"].n_unique())
c3.metric("Средняя темп. за период", f"{filtered_df['avg_temp'].mean():.1f}°C" if len(filtered_df) > 0 else "N/A")

# --- Визуализация распределений ---
st.divider()
st.subheader("📊 Анализ распределения признаков")

# Создаем колонки для настроек графиков
plot_col1, plot_col2 = st.columns(2)

with plot_col1:
    feature_to_plot = st.selectbox(
        "Выберите признак для анализа",
        options=["avg_temp", "total_precip", "avg_wind"],
        format_func=lambda x: {
            "avg_temp": "🌡️ Температура",
            "total_precip": "🌧️ Осадки",
            "avg_wind": "💨 Скорость ветра"
        }.get(x)
    )

with plot_col2:
    chart_type = st.radio(
        "Тип графика",
        options=["Гистограмма", "Boxplot (Ящик с усами)"],
        horizontal=True
    )

if not filtered_df.is_empty():
    if chart_type == "Гистограмма":
        fig = px.histogram(
            filtered_df.to_pandas(),
            x=feature_to_plot,
            color="city" if len(selected_cities) <= 5 else None, # Группируем по городу, если их немного
            marginal="rug", # Добавляет отметки плотности внизу
            title=f"Распределение признака: {feature_to_plot}",
            barmode="overlay",
            template="plotly_white"
        )
    else:
        fig = px.box(
            filtered_df.to_pandas(),
            x="city",
            y=feature_to_plot,
            color="city",
            title=f"Разброс значений {feature_to_plot} по городам",
            points="all", # Показывает все точки данных рядом с боксом
            template="plotly_white"
        )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Нет данных для построения графиков.")

# --- Вывод исходных данных ---
st.divider()
st.subheader("📋 Исходные данные")

# Чтобы пагинация не ломалась при изменении фильтров, сбрасываем страницу 
# через ключ виджета или просто проверяем границы
rows_per_page = st.sidebar.slider("Строк на странице", 10, 100, 20)
total_records = len(filtered_df)
total_pages = max(1, (total_records // rows_per_page) + (1 if total_records % rows_per_page > 0 else 0))

if total_records > 0:
    page_num = st.number_input("Страница", min_value=1, max_value=total_pages, step=1)
    
    # Защита от выхода за границы (если фильтр резко сократил кол-во страниц)
    current_page = min(page_num, total_pages)
    
    start_idx = (current_page - 1) * rows_per_page
    page_df = filtered_df.slice(start_idx, rows_per_page)
    
    st.dataframe(
        page_df.to_pandas(), 
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Показано {start_idx + 1} - {min(start_idx + rows_per_page, total_records)} из {total_records}")
else:
    st.warning("По вашему запросу данных не найдено. Попробуйте изменить фильтры.")