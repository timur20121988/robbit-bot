from aiogram import Router, F, types
from aiogram.filters import Command
from utils.db_api import get_homework, get_schedule, add_chat
from keyboards.keyboards import get_user_main_kb
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.cleaner import schedule_deletion

router = Router()

class UserStates(StatesGroup):
    waiting_for_hw_date = State()

@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных действий.", reply_markup=get_user_main_kb())
        return

    await state.clear()
    await state.clear()
    msg = await message.answer("Действие отменено.", reply_markup=get_user_main_kb())
    schedule_deletion(msg)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await add_chat(message.chat.id)
    msg = await message.answer(
        "Привет! Я бот для домашнего задания и расписания.\n"
        "Нажми **🔎 ДЗ по дате**, чтобы посмотреть задания на ближайшие 10 дней.\n"
        "или **📚 Расписание**, чтобы узнать уроки.",
        reply_markup=get_user_main_kb(),
        parse_mode="Markdown"
    )
    schedule_deletion(msg, delay=60) # Keep welcome a bit longer

@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: types.Message):
    text = (
        "Доступные команды:\n"
        "/dzd - Выбрать дату для ДЗ\n"
        "/raspisanie - Расписание на сегодня\n"
        "Также используйте кнопки меню."
    )
    msg = await message.answer(text)
    schedule_deletion(msg)

from keyboards.user_kb import get_subjects_kb
from utils.db_api import get_homework_subjects, get_homework_by_subject

async def show_hw_dates(message: types.Message, date_obj):
    from utils.db_api import get_schedule_subjects
    subjects = await get_schedule_subjects(date_obj)
    
    if not subjects:
        # Fallback: if no schedule, maybe check if there is HW anyway? 
        # But user wants schedule-based. Let's stick to schedule.
        # Or maybe combine?
        # Let's check actual HW too if schedule is missing (e.g. extra classes)
        existing_hw_subjects = await get_homework_subjects(date_obj)
        # Use dict.fromkeys to preserve order of 'subjects' (schedule) and append new ones from 'existing'
        combined = list(subjects)
        for s in existing_hw_subjects:
            if s not in combined:
                combined.append(s)
        subjects = combined
    
    if not subjects:
        msg = await message.answer(f"На {date_obj.strftime('%d.%m.%Y')} расписания нет и предмета с ДЗ не найдено.")
        schedule_deletion(msg)
        return

    kb = get_subjects_kb(subjects, date_obj)
    msg = await message.answer(f"📚 **ДЗ на {date_obj.strftime('%d.%m.%Y')}**\nВыберите предмет:", reply_markup=kb, parse_mode="Markdown")
    schedule_deletion(msg)

@router.callback_query(F.data.startswith("hw_"))
async def show_hw_content(callback: types.CallbackQuery):
    # Data format: hw_2023-10-25_SubjectName
    _, date_str, subject = callback.data.split("_", 2)
    hw_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    hw_list = await get_homework_by_subject(hw_date, subject)
    
    if not hw_list:
        msg = await callback.message.answer(f"📌 *{subject}*\nНа этот предмет пока не добавлено домашнее задание.", parse_mode="Markdown")
        schedule_deletion(msg)
        await callback.answer()
        return

    for item in hw_list:
        text = f"📌 *{subject}*\n📝 {item['description']}"
        msg = await callback.message.answer(text, parse_mode="Markdown")
        schedule_deletion(msg, delay=120) # Keep content longer
        
        # Send attachments
        if item['attachments']:
            # Create MediaGroup if multiple photos?
            # For simplicity and mixed types, sending one by one or as group
            # aiogram 3 media group builder
            from aiogram.types import InputMediaPhoto, InputMediaDocument
            from aiogram.utils.media_group import MediaGroupBuilder
            
            photos = [a for a in item['attachments'] if a['file_type'] == 'photo']
            docs = [a for a in item['attachments'] if a['file_type'] == 'document']
            
            if photos:
                if len(photos) > 1:
                    media = MediaGroupBuilder()
                    for p in photos:
                        media.add_photo(media=p['file_id'])
                    await callback.message.answer_media_group(media.build())
                else:
                     await callback.message.answer_photo(photos[0]['file_id'])
            
            for doc in docs:
                 await callback.message.answer_document(doc['file_id'])
                 
    await callback.answer()

@router.message(F.text == "🔎 ДЗ по дате")
@router.message(Command("dzd")) 
async def show_10_days_menu(message: types.Message):
    """Show next 10 days for selection (replaces old manual input)"""
    from keyboards.keyboards import get_next_days_kb
    kb = get_next_days_kb(callback_prefix="dzd_date_")
    msg = await message.answer("📅 Выберите дату для просмотра ДЗ (кроме воскресенья):", reply_markup=kb)
    schedule_deletion(msg)

@router.callback_query(F.data.startswith("dzd_date_"))
async def process_dzd_date(callback: types.CallbackQuery):
    date_str = callback.data.split("dzd_date_", 1)[1]
    hw_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Reuse show_hw_dates logic but adapted for inline response/update if possible,
    # or just send new message. show_hw_dates sends a new message.
    # Let's verify if show_hw_dates works well here.
    # It calls get_subjects_kb and sends message. 
    # To keep it clean in groups/inline, maybe we edit the message?
    
    from utils.db_api import get_schedule_subjects
    subjects = await get_schedule_subjects(hw_date)
    # Combine with existing HW subjects preserving order
    existing_hw_subjects = await get_homework_subjects(hw_date)
    combined = list(subjects)
    for s in existing_hw_subjects:
        if s not in combined:
            combined.append(s)
    subjects = combined
    
    if not subjects:
        await callback.message.edit_text(f"На {hw_date.strftime('%d.%m.%Y')} расписания нет.")
        return

    kb = get_subjects_kb(subjects, hw_date)
    await callback.message.edit_text(f"📚 **ДЗ на {hw_date.strftime('%d.%m.%Y')}**\nВыберите предмет:", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

    




from keyboards.keyboards import get_week_days_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@router.message(Command("raspisanie"))
@router.message(Command("rs"))
@router.message(F.text == "📚 Расписание")
@router.message(F.text == "📚 Расписание на неделю")
async def cmd_schedule(message: types.Message):
    # Show inline keyboard with days
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    buttons = [[InlineKeyboardButton(text=day, callback_data=f"view_sched_{day}")] for day in days]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    msg = await message.answer("Выберите день недели для просмотра расписания:", reply_markup=kb)
    schedule_deletion(msg)

@router.callback_query(F.data.startswith("view_sched_"))
async def process_view_sched(callback: types.CallbackQuery):
    day = callback.data.split("_")[2]
    lessons = await get_schedule(day)
    
    if lessons:
        msg = await callback.message.answer(f"📅 **Расписание на {day}:**\n\n{lessons}", parse_mode="Markdown")
    else:
        msg = await callback.message.answer(f"На {day} расписания нет.")
    schedule_deletion(msg, delay=60)
    await callback.answer()

# --- Auto-register chats ---
@router.my_chat_member()
async def on_bot_added(event: types.ChatMemberUpdated):
    # If bot is added to group or user unblocked bot
    if event.new_chat_member.status in ['member', 'administrator']:
        await add_chat(event.chat.id)

@router.message(F.new_chat_members)
async def on_new_member(message: types.Message):
    # Check if bot itself was added
    bot_id = message.bot.id
    for member in message.new_chat_members:
        if member.id == bot_id:
            await add_chat(message.chat.id)
            msg = await message.answer("Всем привет! Я готов помогать с ДЗ и расписанием. Убедитесь, что я админ, если хотите, чтобы я публиковал объявления.")
            schedule_deletion(msg)

