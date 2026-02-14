from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def get_user_main_kb():
    kp = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 ДЗ по дате"), KeyboardButton(text="📚 Расписание на неделю")],
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔐 Админ-панель")]
        ],
        resize_keyboard=True
    )
    return kp

def get_admin_panel_kb():
    kp = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить ДЗ"), KeyboardButton(text="🗑 Удалить ДЗ")],
            [KeyboardButton(text="✏ Редактировать расписание"), KeyboardButton(text="📢 Объявление")],
            [KeyboardButton(text="⬅ Назад")]
        ],
        resize_keyboard=True
    )
    return kp

def get_cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Отмена")]], resize_keyboard=True)

def get_week_days_kb():
    # Only Monday-Saturday
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    buttons = [[KeyboardButton(text=day)] for day in days]
    buttons.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_days_kb():
    """Inline keyboard for days of week"""
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    buttons = [[InlineKeyboardButton(text=day, callback_data=day)] for day in days]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")])
    return InlineKeyboardMarkup(inline_keyboard=buttons) 

def get_next_days_kb(callback_prefix: str = "date_"):
    """
    Generates inline keyboard with next 10 days, skipping Sundays.
    callback_prefix: prefix for callback_data (e.g. 'hw_view_', 'hw_add_', 'hw_del_')
    """
    today = datetime.now().date()
    days_reverse = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    rows = []
    count = 0
    i = 0
    while count < 10:
        date_opt = today + timedelta(days=i)
        weekday = date_opt.weekday()
        if weekday != 6: # Skip Sunday (6)
            day_name = days_reverse[weekday]
            btn_text = f"{date_opt.strftime('%d.%m.%Y')} ({day_name})"
            rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"{callback_prefix}{date_opt.isoformat()}")])
            count += 1
        i += 1
        
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
