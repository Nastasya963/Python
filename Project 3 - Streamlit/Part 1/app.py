import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta    #библиотека для улучшенной работы с датами

st.set_page_config(page_title="Кредитный калькулятор", layout="wide")

st.title(":moneybag: Кредитный калькулятор")

# Используем st.expander для настроек ввода
with st.expander("Настройки кредита", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("Сумма кредита", min_value=0.0, value=1000000.0, step=1000.0)
        rate = st.number_input("Процентная ставка (% годовых)", min_value=0.0, value=15.0, step=0.1)
        term = st.number_input("Срок кредита (месяцев)", min_value=1, value=12, step=1)

    with col2:
        payment_type = st.selectbox("Тип платежа", ["Аннуитетный", "Дифференцированный"])
        start_date = st.date_input("Дата первого платежа", value=datetime.now())

# 5. Обработка неправильного ввода
if amount <= 0 or rate <= 0 or term <= 0:
    st.error("Ошибка: Сумма кредита, процентная ставка и срок кредита должны быть больше нуля.")
    st.stop()  # Остановка выполнения

# Вспомогательные расчеты
monthly_rate = rate / 100 / 12  #расчет ежемесячного процента
schedule = []
remaining_balance = amount

# Вычисление ежемесячного платежа и вывод таблицы
if payment_type == "Аннуитетный":
    # Формула аннуитетного платежа
    if monthly_rate > 0:
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
    else:
        monthly_payment = amount / term

    st.info(f"**Ежемесячный платеж:** {monthly_payment:,.2f} ₽")

    current_balance = amount
    for i in range(term):
        interest_part = current_balance * monthly_rate
        debt_part = monthly_payment - interest_part
        end_balance = current_balance - debt_part

        schedule.append({
            "Дата": start_date + relativedelta(months=i),
            "Остаток долга (нач)": current_balance,
            "Платеж": monthly_payment,
            "Проценты": interest_part,
            "Тело долга": debt_part,
            "Остаток долга (кон)": max(0, end_balance)
        })
        current_balance = end_balance

else:  # Дифференцированный
    principal_part = amount / term
    current_balance = amount
    for i in range(term):
        interest_part = current_balance * monthly_rate
        monthly_payment = principal_part + interest_part
        end_balance = current_balance - principal_part

        schedule.append({
            "Дата": start_date + relativedelta(months=i),
            "Остаток долга (нач)": current_balance,
            "Платеж": monthly_payment,
            "Проценты": interest_part,
            "Тело долга": principal_part,
            "Остаток долга (кон)": max(0, end_balance)
        })
        current_balance = end_balance

# Создание DataFrame
df = pd.DataFrame(schedule)

# Форматирование вывода
st.subheader("График платежей")

# Пример условного рендеринга
show_table = st.checkbox("Показать таблицу выплат", value=True)

if show_table:
    # Применяем форматирование для красоты (оставляя 2 знака после запятой)
    st.dataframe(
        df.style.format({
            "Дата": lambda x: x.strftime('%d.%m.%Y'),
            "Остаток долга (нач)": "{:,.2f} ₽",
            "Платеж": "{:,.2f} ₽",
            "Проценты": "{:,.2f} ₽",
            "Тело долга": "{:,.2f} ₽",
            "Остаток долга (кон)": "{:,.2f} ₽"
        }),
        use_container_width=True
    )
else:
    st.write("Таблица скрыта.")

# Кнопка сброса (демонстрация st.rerun)
if st.button("Сбросить расчеты"):
    st.rerun()

# Итоговая статистика
total_paid = df["Платеж"].sum()
total_interest = total_paid - amount

st.write("---")
c1, c2, c3 = st.columns(3)
c1.metric("Всего выплачено", f"{total_paid:,.2f} ₽")
c2.metric("Переплата (проценты)", f"{total_interest:,.2f} ₽")
c3.metric("Действующая ставка", f"{rate} %")
