import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# --- Настройки страницы ---
st.set_page_config(page_title="Data Analyzer Pro", layout="wide", page_icon="📊")

st.title("📊💰 Анализатор данных")


@st.cache_data
def load_data(uploaded_file):
    try:
        # sep=None с engine='python' автоматически определяет разделитель (запятая, точка с запятой и т.д.)
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        for col in df.columns:
            # Пытаемся конвертировать в даты только если это объект/строка
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    pass
        return df
    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
        return None


uploaded_file = st.sidebar.file_uploader("Загрузите CSV-файл", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        st.subheader("📋 Предпросмотр данных")
        st.dataframe(df.head(10), use_container_width=True)

        all_columns = df.columns.tolist()

        st.divider()
        st.header("📈 Построение графиков")

        # Интерфейс выбора столбцов
        col_settings_1, col_settings_2 = st.columns(2)

        with col_settings_1:
            x_col = st.selectbox("Выберите ось X (Категории или время)", all_columns, key="x_axis")
            y_col = st.selectbox("Выберите ось Y (Числовые значения)", all_columns, key="y_axis")

        with col_settings_2:
            chart_choice = st.selectbox(
                "Выберите тип графика",
                ["Линейный график", "Диаграмма рассеяния (Scatter)", "Столбчатая диаграмма (Bar)",
                 "Гистограмма (Histogram)"],
                key="chart_type"
            )
            if chart_choice == "Гистограмма (Histogram)":
                st.info("ℹ️ Гистограмма строится только по оси X.")

        # Создание контейнера для графика
        fig, ax = plt.subplots(figsize=(10, 5))

        try:
            success = True
            if chart_choice == "Линейный график":
                sns.lineplot(data=df, x=x_col, y=y_col, ax=ax)
                ax.set_title(f"Линейная зависимость {y_col} от {x_col}")

            elif chart_choice == "Диаграмма рассеяния (Scatter)":
                sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
                ax.set_title(f"Точечный график: {x_col} vs {y_col}")

            elif chart_choice == "Столбчатая диаграмма (Bar)":
                # Если уникальных значений больше 30, график будет перегружен
                if df[x_col].nunique() > 30:
                    st.warning("⚠️ Слишком много категорий на оси X. График может быть нечитаемым.")
                sns.barplot(data=df, x=x_col, y=y_col, ax=ax)
                ax.set_title(f"Средние значения {y_col} по {x_col}")
                plt.xticks(rotation=45)

            elif chart_choice == "Гистограмма (Histogram)":
                sns.histplot(data=df, x=x_col, kde=True, ax=ax, color="skyblue")
                ax.set_title(f"Распределение значений в: {x_col}")

            # Тонкая настройка сетки
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)

            # --- Подготовка к скачиванию ---
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
            buf.seek(0)

            st.download_button(
                label="💾 Скачать график в PNG",
                data=buf,
                file_name=f"plot_{x_col}_vs_{y_col}.png",
                mime="image/png"
            )

            # Освобождаем память
            plt.close(fig)

        except Exception as e:
            st.error(f"Ошибка построения: {e}")
            st.warning(
                "Убедитесь, что выбранные столбцы содержат подходящие типы данных (числа для Y, категории/даты для X).")

else:
    # Приветственный экран
    st.info("👋 Добро пожаловать! Пожалуйста, загрузите CSV-файл через боковую панель.")
    st.image("https://via.placeholder.com/800x400.png?text=Waiting+for+Data...")