from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import date

def get_subjects_kb(subjects, hw_date: date):
    builder = InlineKeyboardBuilder()
    date_str = hw_date.strftime("%Y-%m-%d") # Store date in callback to persist state
    
    for subject in subjects:
        builder.button(text=subject, callback_data=f"hw_{date_str}_{subject}")
    
    builder.adjust(1) # 1 column
    return builder.as_markup()
