from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import OPERATOR_IDS
from ticket_db import create_ticket

router = Router()

class Ticket(StatesGroup):
    category = State()
    question = State()

@router.message(F.text.lower() == "/start")
async def start(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Общие вопросы", callback_data="cat_common")],
        [InlineKeyboardButton(text="Вопрос по оплате", callback_data="cat_payment")],
        [InlineKeyboardButton(text="Качество сервиса", callback_data="cat_quality")]
    ])
    await message.answer("Выберите категорию вашего вопроса:", reply_markup=kb)

@router.callback_query(F.data.startswith("cat_"))
async def set_category(call: CallbackQuery, state: FSMContext):
    category = call.data.replace("cat_", "")
    await state.update_data(category=category)
    await call.message.answer("Напишите, пожалуйста, ваш вопрос. Вы также можете прикрепить фото.")
    await state.set_state(Ticket.question)
    await call.answer()

@router.message(Ticket.question, F.text | F.photo)
async def get_question(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data["category"]
    text = message.text or message.caption or "(без текста)"
    photo = message.photo[-1].file_id if message.photo else None

    ticket = create_ticket(
        user_id=message.from_user.id,
        username=message.from_user.username,
        category=category,
        text=text,
        photo=photo
    )

    caption = (
        f"<b>Новое обращение</b>\n"
        f"Категория: {ticket['category']}\n"
        f"От: @{ticket['username'] or 'Без username'}\n"
        f"ID тикета: {ticket['id']}\n\n"
        f"{ticket['text']}"
    )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ответить", callback_data=f"reply_{ticket['id']}")],
        [InlineKeyboardButton(text="Закрыть", callback_data=f"close_{ticket['id']}")],
        [InlineKeyboardButton(text="Удалить", callback_data=f"delete_{ticket['id']}")]
    ])

    for admin_id in OPERATOR_IDS:
        if photo:
            await message.bot.send_photo(admin_id, photo=photo, caption=caption, reply_markup=reply_markup)
        else:
            await message.bot.send_message(admin_id, caption, reply_markup=reply_markup)

    await message.answer("Ваше обращение отправлено оператору. Ожидайте ответа.")
    await state.clear()
