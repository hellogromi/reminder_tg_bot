# Константы для бота
months = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

# Словарь с количеством дней в каждом месяце для 2026 года (невисокосный)
days_in_month = {
    "Январь": 31,
    "Февраль": 28, 
    "Март": 31,
    "Апрель": 30,
    "Май": 31,
    "Июнь": 30,
    "Июль": 31,
    "Август": 31,
    "Сентябрь": 30,
    "Октябрь": 31,
    "Ноябрь": 30,
    "Декабрь": 31
}

# Функция для получения списка дней для конкретного месяца
def get_days_for_month(month_name):
    """Возвращает список дней для указанного месяца"""
    if month_name in days_in_month:
        return [str(i) for i in range(1, days_in_month[month_name] + 1)]
    else:
        return [str(i) for i in range(1, 32)]  # По умолчанию 31 день

# Функция для конвертации timestamp в читаемый формат
def data_convert(timestamp):
    """Конвертирует timestamp в строку с датой и временем"""
    import datetime
    try:
        dt = datetime.datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return str(timestamp)  # Возвращаем как есть в случае ошибки

# Явно указываем, что экспортируем
all = ['months', 'days_in_month', 'get_days_for_month', 'data_convert']
