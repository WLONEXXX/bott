import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ================== НАСТРОЙКИ ==================

TOKEN = "8250737324:AAFAGLchB2XdNN3VUHFMfifltRpTVLeIr1I"
OPERATOR_ID = 7892937398

# ================== ДАННЫЕ ==================

products = {
    "food": {
        "title": "Еда",
        "items": [
            {
                "id": 1,
                "name": "Пицца Маргарита",
                "price": 32,
                "desc": "Классическая пицца 32 см, сыр моцарелла, томаты.",
                "photo": "https://via.placeholder.com/400x300.png?text=Pizza"
            },
            {
                "id": 2,
                "name": "Бургер Классический",
                "price": 28,
                "desc": "Сочный говяжий бургер с сыром и соусом.",
                "photo": "https://via.placeholder.com/400x300.png?text=Burger"
            },
            {
                "id": 3,
                "name": "Суши сет",
                "price": 55,
                "desc": "24 кусочка: калифорния, филадельфия, маки.",
                "photo": "https://via.placeholder.com/400x300.png?text=Sushi"
            },
            {
                "id": 4,
                "name": "Шаурма XL",
                "price": 22,
                "desc": "Большая шаурма с курицей, овощами и фирменным соусом.",
                "photo": "https://via.placeholder.com/400x300.png?text=Shawarma"
            }
        ]
    }
}

# ================== КЛАВИАТУРЫ ==================

def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каталог", callback_data="catalog")]
    ])
    return kb

def categories_kb():
    kb = InlineKeyboardMarkup()
    for key, cat in products.items():
        kb.add(InlineKeyboardButton(cat["title"], callback_data=f"cat_{key}"))
    return kb

def products_kb(cat_key):
    kb = InlineKeyboardMarkup()
    for item in products[cat_key]["items"]:
        kb.add(InlineKeyboardButton(item["name"], callback_data=f"item_{item['id']}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="catalog"))
    return kb

def buy_kb(item_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Заказать", callback_data=f"buy_{item_id}")]
    ])

# ================== БОТ ==================

bot = Bot(token=TOKEN)
dp = Dispatcher()

pending = {}  # message_id -> user_id

# ================== ХЕНДЛЕРЫ ==================

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Добро пожаловать в магазин еды!", reply_markup=main_menu())

@dp.callback_query(F.data == "catalog")
async def open_catalog(callback: CallbackQuery):
    await callback.message.edit_text("Выберите категорию:", reply_markup=categories_kb())

@dp.callback_query(F.data.startswith("cat_"))
async def open_category(callback: CallbackQuery):
    cat_key = callback.data.split("_")[1]
    await callback.message.edit_text(
        f"Категория: {products[cat_key]['title']}",
        reply_markup=products_kb(cat_key)
    )

@dp.callback_query(F.data.startswith("item_"))
async def open_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])

    item = None
    for cat in products.values():
        for it in cat["items"]:
            if it["id"] == item_id:
                item = it
                break

    caption = f"{item['name']}\nЦена: {item['price']} zł\n\n{item['desc']}"

    await callback.message.answer_photo(
        item["photo"],
        caption=caption,
        reply_markup=buy_kb(item_id)
    )

@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])

    item = None
    for cat in products.values():
        for it in cat["items"]:
            if it["id"] == item_id:
                item = it
                break

    user = callback.from_user

    text = (
        "🆕 Новый заказ!\n\n"
        f"Товар: {item['name']}\n"
        f"Цена: {item['price']} zł\n\n"
        f"Пользователь: {user.full_name}\n"
        f"Username: @{user.username}\n"
        f"User ID: {user.id}\n\n"
        "Ответь на это сообщение реплаем, чтобы написать клиенту."
    )

    msg = await bot.send_message(OPERATOR_ID, text)
    pending[msg.message_id] = user.id

    await callback.message.answer("Ваш заказ отправлен оператору!")
    await callback.answer()

@dp.message(F.chat.id == OPERATOR_ID)
async def operator_reply(message: Message):
    if not message.reply_to_message:
        return

    orig = message.reply_to_message.message_id
    user_id = pending.get(orig)

    if user_id:
        await bot.send_message(user_id, f"Оператор: {message.text}")

# ================== ЗАПУСК ==================

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
