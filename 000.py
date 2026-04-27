import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

# Глобальные переменные
root = None
from_currency = None
to_currency = None
amount_entry = None
result_label = None
tree = None
history = []
api_key = "YOUR_API_KEY_HERE"  # Замените на ваш ключ
history_file = "history.json"


def create_widgets():
    global from_currency, to_currency, amount_entry, result_label, tree

    # Выбор валюты "из"
    tk.Label(root, text="Из валюты:").pack(pady=5)
    from_currency = ttk.Combobox(root, width=20)
    from_currency.pack(pady=5)
    from_currency.set("USD")

    # Выбор валюты "в"
    tk.Label(root, text="В валюту:").pack(pady=5)
    to_currency = ttk.Combobox(root, width=20)
    to_currency.pack(pady=5)
    to_currency.set("EUR")

    # Поле ввода суммы
    tk.Label(root, text="Сумма:").pack(pady=5)
    amount_entry = tk.Entry(root, width=20)
    amount_entry.pack(pady=5)

    # Кнопка конвертации
    convert_btn = tk.Button(root, text="Конвертировать",
                            command=convert, bg="green", fg="white")
    convert_btn.pack(pady=10)

    # Результат
    result_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
    result_label.pack(pady=10)

    # Таблица истории
    tk.Label(root, text="История конвертаций", font=("Arial", 10, "bold")).pack(pady=5)

    # Создание таблицы
    columns = ("Дата", "Из", "Сумма", "В", "Результат")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(pady=5)

    # Кнопка загрузки истории
    load_btn = tk.Button(root, text="Загрузить историю", command=load_history_from_file)
    load_btn.pack(pady=5)


def load_currencies():
    """Загрузка списка валют из API"""
    global from_currency, to_currency

    try:
        url = f"https://v6.exchangerate-api.com/v6/b47560290b8e91fc2ae4d8b1/latest/USD"
        response = requests.get(url)
        data = response.json()

        if data['result'] == 'success':
            currencies = list(data['conversion_rates'].keys())
            from_currency['values'] = currencies
            to_currency['values'] = currencies
    except:
        messagebox.showerror("Ошибка", "Не удалось загрузить валюты")


def convert():
    global history, result_label, tree

    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            messagebox.showwarning("Ошибка", "Сумма должна быть положительным числом")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Введите корректное число")
        return

    from_curr = from_currency.get()
    to_curr = to_currency.get()

    try:
        url = f"https://v6.exchangerate-api.com/v6/b47560290b8e91fc2ae4d8b1/latest/{from_curr}"
        response = requests.get(url)
        data = response.json()

        if data['result'] == 'success':
            rate = data['conversion_rates'][to_curr]
            result = amount * rate

            result_label.config(text=f"{amount} {from_curr} = {result:.2f} {to_curr}")

            record = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "from": from_curr,
                "amount": amount,
                "to": to_curr,
                "result": f"{result:.2f}"
            }

            history.append(record)
            save_history()
            update_history_table()
        else:
            messagebox.showerror("Ошибка", "Не удалось получить курс")
    except:
        messagebox.showerror("Ошибка", "Ошибка подключения к API")


def save_history():
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_history():
    global history

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            update_history_table()
    except:
        history = []


def load_history_from_file():
    load_history()
    messagebox.showinfo("Успех", "История загружена")


def update_history_table():
    global tree

    for item in tree.get_children():
        tree.delete(item)

    for record in history:
        tree.insert("", "end", values=(
            record['date'],
            record['from'],
            record['amount'],
            record['to'],
            record['result']
        ))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Currency Converter")
    root.geometry("650x500")

    create_widgets()
    load_currencies()
    load_history()

    root.mainloop()