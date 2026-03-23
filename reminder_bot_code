import telebot
from telebot.types import *
import datetime
import time
import threading
import os

# Импортируем всё из constants
from constants import months, days_in_month, get_days_for_month, data_convert
from DB_reminder_bot import notes, users

# Используем переменные окружения
token = os.getenv('BOT_TOKEN', "8085164089:AAExnhxfcp80IR0sCI9VeRTNXh4z6bIWkfY")
bot = telebot.TeleBot(token)

# Хранилище состояний пользователей
user_sessions = {}

class UserSession:
    def init(self):
        self.month = ""
        self.month_name = ""
        self.day = 0
        self.reminder_time = 0
        self.note_txt = ""

@bot.message_handler(commands=["start"])
def start_function(message: Message):
    # Создаем сессию для пользователя
    user_sessions[message.chat.id] = UserSession()
    
    # Добавляем пользователя в базу данных
    users.add_user(
        message.chat.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    
    keyboard = InlineKeyboardMarkup(row_width=3)
    for i in range(0, len(months), 3):
        if i + 2 < len(months):
            button_month = InlineKeyboardButton(months[i], callback_data=f"month_{months[i]}")
            button_month1 = InlineKeyboardButton(months[i + 1], callback_data=f"month_{months[i + 1]}")
            button_month2 = InlineKeyboardButton(months[i + 2], callback_data=f"month_{months[i + 2]}")
            keyboard.add(button_month, button_month1, button_month2)
    
    bot.send_message(
        message.chat.id, 
        "👋 Привет! Я бот для создания напоминаний.\n\n"
        "Выбери нужный месяц:", 
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("month_"))
def check_input(callback: CallbackQuery):
    month_name = callback.data.replace("month_", "")
    bot.send_message(callback.message.chat.id, f'✅ Вы выбрали месяц: {month_name}')
    
    if callback.message.chat.id in user_sessions:
        user_sessions[callback.message.chat.id].month = months.index(month_name) + 1
        user_sessions[callback.message.chat.id].month_name = month_name
    
    # ИСПРАВЛЕНО: используем другое имя переменной
    days_for_month = get_days_for_month(month_name)
    
    keyboard = InlineKeyboardMarkup(row_width=3)
    for i in range(0, len(days_for_month), 3):
        buttons = []
        for j in range(3):
            if i + j < len(days_for_month):
                day = days_for_month[i + j]
                buttons.append(InlineKeyboardButton(day, callback_data=f"day_{day}"))
        keyboard.add(*buttons)
    
    bot.send_message(
        callback.message.chat.id, 
        f"📅 В {month_name} {days_in_month[month_name]} дней. Выбери нужный день:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("day_"))
def check_input2(callback: CallbackQuery):
    day_value = callback.data.replace("day_", "")
    bot.send_message(callback.message.chat.id, f'✅ Вы выбрали день: {day_value}')
    
    if callback.message.chat.id in user_sessions:
        user_sessions[callback.message.chat.id].day = day_value
    
    bot.send_message(
        callback.message.chat.id, 
        '⏰ Введите время в формате ЧЧ:ММ (например, 9:41 или 14:30)\n'
        'Когда должно прийти напоминание?'
    )
    bot.register_next_step_handler(callback.message, time_input)

def note_text(message: Message):
    if message.chat.id not in user_sessions:
        bot.send_message(message.chat.id, "❌ Сессия истекла. Начните заново с /start")
        return
    
    session = user_sessions[message.chat.id]
    session.note_txt = message.text
    
    # Сохраняем заметку в базу данных
    notes.write([message.chat.id, session.note_txt, session.reminder_time])
    
    # Форматируем время для вывода
    reminder_datetime = datetime.datetime.fromtimestamp(session.reminder_time)
    
    bot.send_message(
        message.chat.id, 
        f'✅ Заметка успешно создана!\n\n'
        f'📝 Текст: {session.note_txt}\n'
        f'⏰ Время: {reminder_datetime.strftime("%d.%m.%Y %H:%M")}\n\n'
        f'Я напомню вам об этом!'
    )
    
    # Очищаем сессию
    del user_sessions[message.chat.id]

def time_input(message: Message):
    if message.chat.id not in user_sessions:
        bot.send_message(message.chat.id, "❌ Сессия истекла. Начните заново с /start")
        return
    
    session = user_sessions[message.chat.id]
    
    try:
        # Проверяем формат времени
        time_obj = datetime.datetime.strptime(message.text.strip(), '%H:%M').time()
        
        # Используем фиксированный год 2026
        target_year = 2026
        
        # Создаем дату напоминания
        reminder_date = datetime.date(target_year, session.month, int(session.day))
        
        # Создаем полную дату и время
        reminder_datetime = datetime.datetime.combine(reminder_date, time_obj)
        session.reminder_time = int(reminder_datetime.timestamp())
        
        # Проверяем, не прошла ли уже дата
        current_time = datetime.datetime.now()
        if reminder_datetime < current_time:
            bot.send_message(
                message.chat.id,
                '❌ Указанное время уже прошло! Пожалуйста, выберите будущую дату.'
            )
            # Возвращаем пользователя к выбору месяца
            start_function(message)
            return
        
        bot.send_message(message.chat.id, '📝 Введите текст заметки:')
        bot.register_next_step_handler(message, note_text)
        
    except ValueError:
        bot.send_message(
            message.chat.id, 
            '❌ Неправильный формат времени!\n'
            'Пожалуйста, введите время в формате ЧЧ:ММ (например, 9:41 или 14:30)'
        )
        bot.register_next_step_handler(message, time_input)
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f'❌ Произошла ошибка: {str(e)}\nПожалуйста, попробуйте еще раз с /start'
        )

# Добавляем команду для отмены
@bot.message_handler(commands=["cancel"])
def cancel_command(message: Message):
    if message.chat.id in user_sessions:
        del user_sessions[message.chat.id]
        bot.send_message(message.chat.id, "❌ Создание заметки отменено. Используйте /start для новой заметки.")
    else:
        bot.send_message(message.chat.id, "❌ Нет активной сессии. Используйте /start для создания заметки.")

@bot.message_handler(commands=["mynotes"])
def show_notes(message: Message):
    user_notes = notes.read("id_user", message.chat.id)
    
    if not user_notes:
        bot.send_message(message.chat.id, "📭 У вас пока нет заметок.")
        return
    
    # Всегда обрабатываем как список
    for note in user_notes:
        try:
            note_text = note[2]  # текст заметки
            note_time = note[3]   # timestamp
            formatted_time = data_convert(note_time)
            bot.send_message(message.chat.id, f"📝 {note_text} - {formatted_time}")
        except Exception as e:
            print(f"Ошибка при отображении заметки: {e}")
            continue

@bot.message_handler(commands=["deletenote"])
def delete_note(message: Message):
    user_notes = notes.read("id_user", message.chat.id)
    
    if not user_notes:
        bot.send_message(message.chat.id, "📭 У вас нет заметок для удаления.")
        return
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # Всегда обрабатываем как список
    for note in user_notes:
        try:
            note_text = note[2]  # текст заметки
            note_time = note[3]   # timestamp
            formatted_time = data_convert(note_time)
            btn_txt = f"{note_text} - {formatted_time}"
            # Обрезаем длинный текст для кнопки
            if len(btn_txt) > 40:
                btn_txt = btn_txt[:37] + "..."
            button_note = InlineKeyboardButton(btn_txt, callback_data=f"delete_{note_time}")
            keyboard.add(button_note)
        except Exception as e:
            print(f"Ошибка при создании кнопки удаления: {e}")
            continue
    
    # Добавляем кнопку отмены
    cancel_button = InlineKeyboardButton("❌ Отмена", callback_data="delete_cancel")
    keyboard.add(cancel_button)
    
    bot.send_message(
        message.chat.id, 
        "🗑 Какую заметку вы хотите удалить?",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("delete_"))
def check_delete_note(callback: CallbackQuery):
    if callback.data == "delete_cancel":
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="❌ Удаление отменено."
        )
        bot.answer_callback_query(callback.id)
        return
    
    try:
        # Извлекаем timestamp из callback_data
        note_time = int(callback.data.replace("delete_", ""))
        
        # Получаем текст заметки до удаления
        user_notes = notes.read("date", note_time)
        note_text = user_notes[0][2] if user_notes else "Неизвестная заметка"
        
        # Удаляем заметку
        notes.delete_row("date", note_time)
        
        # Отправляем подтверждение
        bot.answer_callback_query(callback.id, "✅ Заметка удалена!")
        
        # Обновляем сообщение
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=f"✅ Заметка \"{note_text}\" от {data_convert(note_time)} была удалена."
        )
        
        # Показываем оставшиеся заметки
        show_notes(callback.message)
        
    except Exception as e:
        bot.answer_callback_query(callback.id, "❌ Ошибка при удалении")
        bot.send_message(callback.message.chat.id, f"❌ Произошла ошибка: {e}")

@bot.message_handler(commands=["help"])
def help_command(message: Message):
    help_text = """
📚 Доступные команды:

/start - Начать работу с ботом и создать новое напоминание
/mynotes - Показать все мои заметки
/deletenote - Удалить заметку
/cancel - Отменить создание заметки
/help - Показать это сообщение

✨ Особенности:
- Для каждого месяца правильное количество дней
- Февраль 2026 года - 28 дней
- Все напоминания создаются на 2026 год

Как пользоваться ботом:
1. Выберите месяц
2. Выберите день
3. Введите время в формате ЧЧ:ММ
4. Введите текст заметки

Я пришлю вам напоминание в указанное время!
    """
    bot.send_message(message.chat.id, help_text)

def check_and_send_notes():
    """Проверка и отправка напоминаний"""
    current_time = int(time.time())
    
    # Получаем все заметки
    all_notes = notes.read_all()
    
    if not all_notes:
        return
    
    for note in all_notes:
        try:
            user_id = note[1]
            note_text = note[2]
            note_time = note[3]
            
            # Отправляем напоминание за минуту до указанного времени
            if note_time <= current_time + 60 and note_time > current_time - 60:
                try:
                    bot.send_message(
                        user_id, 
                        f"🔔 НАПОМИНАНИЕ!\n\n"
                        f"📝 Заметка: {note_text}\n"
                        f"⏰ Время: {data_convert(note_time)}"
                    )
                    
                    # Удаляем отправленную заметку
                    notes.delete_row("date", note_time)
                    
                except Exception as e:
                    print(f"Ошибка при отправке заметки пользователю {user_id}: {e}")
                    # Если не удалось отправить, удаляем заметку
                    notes.delete_row("date", note_time)
        except Exception as e:
            print(f"Ошибка при обработке заметки: {e}")
            continue

def start_reminder_checker():
    """Запуск проверки напоминаний в отдельном потоке"""
    while True:
        try:
            check_and_send_notes()
            time.sleep(60)  # Проверяем каждую минуту
        except Exception as e:
            print(f"Ошибка в проверке напоминаний: {e}")
            time.sleep(60)

# Запускаем проверку напоминаний в отдельном потоке
reminder_thread = threading.Thread(target=start_reminder_checker, daemon=True)
reminder_thread.start()

print("Бот запущен и готов к работе!")
print("✅ Для каждого месяца правильное количество дней")
print("📅 Все напоминания создаются на 2026 год")
bot.infinity_polling(timeout=30, long_polling_timeout=30)
