from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import OPERATOR_IDS
from ticket_db import (
    get_open_tickets,
    get_ticket_by_id,
    close_ticket_by_user_id,
    delete_ticket_by_user_id
)

router = Router()

class Operator(StatesGroup):
    replying_to = State()

# 👇 Используется ID тикета, а не user_id
@router.callback_query(F.data.startswith("reply_"))
async def reply_ticket(call: CallbackQuery, state: FSMContext):
    ticket_id = int(call.data.split("_")[1])
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await call.answer("Тикет не найден.")
        return

    await state.set_state(Operator.replying_to)
    await state.update_data(ticket=ticket)
    await call.message.answer(f"Напишите ответ пользователю @{ticket['username']}")
    await call.answer()

@router.message(Operator.replying_to)
async def send_operator_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket = data.get("ticket")
    if ticket:
        await message.bot.send_message(
            ticket["user_id"],
            f"<b>Оператор Дуся:</b>\n{message.text}"
        )
        await message.answer("Ответ отправлен пользователю.")
    await state.clear()

@router.callback_query(F.data.startswith("close_"))
async def close_ticket(call: CallbackQuery):
    ticket_id = int(call.data.split("_")[1])
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await call.answer("Тикет не найден.")
        return
    close_ticket_by_user_id(ticket["user_id"])
    await call.message.edit_text("Обращение закрыто.")
    await call.answer("Закрыто.")

@router.callback_query(F.data.startswith("delete_"))
async def delete_ticket(call: CallbackQuery):
    ticket_id = int(call.data.split("_")[1])
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await call.answer("Тикет не найден.")
        return
    delete_ticket_by_user_id(ticket["user_id"])
    await call.message.edit_text("Обращение удалено.")
    await call.answer("Удалено.")

@router.message(F.text.startswith("/view "))
async def view_ticket(message: Message):
    if message.chat.id not in OPERATOR_IDS:
        return

    try:
        ticket_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Неверный формат. Используйте /view <id>")
        return

    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await message.answer("Тикет с таким ID не найден.")
        return

    text = (
        f"<b>Тикет #{ticket['id']}</b>\n"
        f"Категория: {ticket['category']}\n"
        f"Пользователь: @{ticket['username']}\n"
        f"Статус: {ticket['status']}\n"
        f"Создан: {ticket['created_at']}\n\n"
        f"{ticket['text']}"
    )
    if ticket["photo"]:
        await message.bot.send_photo(message.chat.id, photo=ticket["photo"], caption=text)
    else:
        await message.answer(text)

@router.message(F.text == "/list")
async def list_tickets(message: Message):
    if message.chat.id not in OPERATOR_IDS:
        return

    tickets = get_open_tickets()
    if not tickets:
        await message.answer("Нет открытых обращений.")
        return

    text = "\n\n".join([
        f"#{t['id']} | @{t['username']} | {t['category']}\n{t['text'][:100]}..."
        for t in tickets
    ])
    await message.answer(f"<b>Открытые обращения:</b>\n\n{text}")
