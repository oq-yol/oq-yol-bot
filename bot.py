import asyncio
import csv
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = "8856474842:AAGDUx4Yfz5LmjsmqR9U07aKXZZnbl5qDiM"  # ← замените

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния регистрации
class Reg(StatesGroup):
    language = State()
    name = State()
    phone = State()
    truck = State()
    plate = State()
    yatt = State()
    region = State()
    confirm = State()

# Клавиатуры
def lang_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Русский 🇷🇺")
    kb.button(text="O‘zbekcha 🇺🇿")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def main_kb(lang="ru"):
    kb = ReplyKeyboardBuilder()
    if lang == "ru":
        kb.button(text="📝 Зарегистрироваться")
        kb.button(text="📦 Актуальные грузы")
        kb.button(text="❓ Помощь")
    else:
        kb.button(text="📝 Ro‘yxatdan o‘tish")
        kb.button(text="📦 Joriy yuklar")
        kb.button(text="❓ Yordam")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def yatt_kb(lang="ru"):
    kb = ReplyKeyboardBuilder()
    if lang == "ru":
        kb.button(text="Да, есть ЯТТ")
        kb.button(text="Нет, нужно открыть")
        kb.button(text="В процессе")
    else:
        kb.button(text="Ha, YaTT bor")
        kb.button(text="Yo‘q, ochish kerak")
        kb.button(text="Jarayonda")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

# Сохранение в CSV
def save_driver(data: dict):
    file_exists = os.path.isfile("drivers.csv")
    with open("drivers.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! / Здравствуйте!\n\n"
        "OQ YOL — doimiy yuklar tent mashinalar uchun.\n"
        "Постоянные грузы для тентов по всему Узбекистану.\n\n"
        "Выберите язык / Tilni tanlang:",
        reply_markup=lang_kb()
    )
    await state.set_state(Reg.language)

@dp.message(Reg.language, F.text.in_(["Русский 🇷🇺", "O‘zbekcha 🇺🇿"]))
async def set_lang(message: types.Message, state: FSMContext):
    lang = "ru" if "Русский" in message.text else "uz"
    await state.update_data(lang=lang)
    
    text = {
        "ru": "Отлично! Нажмите «Зарегистрироваться», чтобы начать.",
        "uz": "Ajoyib! Ro‘yxatdan o‘tish uchun tugmani bosing."
    }[lang]
    await message.answer(text, reply_markup=main_kb(lang))
    await state.set_state(None)

@dp.message(F.text.in_(["📝 Зарегистрироваться", "📝 Ro‘yxatdan o‘tish"]))
async def start_reg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {
        "ru": "Введите ваше ФИО (полностью):",
        "uz": "To‘liq F.I.Sh.ingizni yozing:"
    }[lang]
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.name)

@dp.message(Reg.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {
        "ru": "Ваш номер телефона (+998...):",
        "uz": "Telefon raqamingiz (+998...):"
    }[lang]
    await message.answer(text)
    await state.set_state(Reg.phone)

@dp.message(Reg.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {
        "ru": "Опишите машину (тент, объём м³, грузоподъёмность тонн):",
        "uz": "Mashinani tasvirlab bering (tent, hajm m³, yuk ko‘tarish qobiliyati):"
    }[lang]
    await message.answer(text)
    await state.set_state(Reg.truck)

@dp.message(Reg.truck)
async def get_truck(message: types.Message, state: FSMContext):
    await state.update_data(truck=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {
        "ru": "Государственный номер автомобиля:",
        "uz": "Davlat raqami:"
    }[lang]
    await message.answer(text)
    await state.set_state(Reg.plate)

@dp.message(Reg.plate)
async def get_plate(message: types.Message, state: FSMContext):
    await state.update_data(plate=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {
        "ru": "Есть ли у вас ЯТТ?",
        "uz": "YaTT bormi?"
    }[lang]
    await message.answer(text, reply_markup=yatt_kb(lang))
    await state.set_state(Reg.yatt)

@dp.message(Reg.yatt)
async def get_yatt(message: types.Message, state: FSMContext):
    await state.update_data(yatt=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {
        "ru": "В каком регионе вы базируетесь? (город / область)",
        "uz": "Qaysi hududda joylashgansiz? (shahar / viloyat)"
    }[lang]
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.region)

@dp.message(Reg.region)
async def get_region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text, user_id=message.from_user.id, username=message.from_user.username)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    
    summary = (
        f"Проверьте данные:\n\n"
        f"ФИО: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Машина: {data['truck']}\n"
        f"Номер: {data['plate']}\n"
        f"ЯТТ: {data['yatt']}\n"
        f"Регион: {data['region']}\n\n"
        f"Всё верно? Напишите «Да» или «Нет»"
        if lang == "ru" else
        f"Ma’lumotlarni tekshiring:\n\n"
        f"F.I.Sh: {data['name']}\n"
        f"Telefon: {data['phone']}\n"
        f"Mashina: {data['truck']}\n"
        f"Raqam: {data['plate']}\n"
        f"YaTT: {data['yatt']}\n"
        f"Hudud: {data['region']}\n\n"
        f"Hammasi to‘g‘rimi? «Ha» yoki «Yo‘q» deb yozing"
    )
    await message.answer(summary)
    await state.set_state(Reg.confirm)

@dp.message(Reg.confirm, F.text.lower().in_(["да", "ha", "yes"]))
async def confirm_reg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    save_driver(data)
    
    lang = data.get("lang", "ru")
    text = {
        "ru": "✅ Регистрация принята!\n\nМенеджер свяжется с вами в течение 24 часов.\nПока подписывайтесь на канал с грузами: @OQYOL_Gruz",
        "uz": "✅ Ro‘yxatdan o‘tish qabul qilindi!\n\nMenejer 24 soat ichida bog‘lanadi.\nHozircha yuklar kanaliga obuna bo‘ling: @OQYOL_Gruz"
    }[lang]
    await message.answer(text, reply_markup=main_kb(lang))
    await state.clear()
    
    # Уведомление вам (замените на свой chat_id)
    # await bot.send_message(YOUR_CHAT_ID, f"Новый водитель:\n{data}")

@dp.message(F.text.in_(["📦 Актуальные грузы", "📦 Joriy yuklar"]))
async def show_loads(message: types.Message, state: FSMContext):
    await message.answer("Актуальные грузы публикуются в канале:\n@OQYOL_Gruz\n\nПодписывайтесь!")

@dp.message(F.text.in_(["❓ Помощь", "❓ Yordam"]))
async def help_cmd(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {
        "ru": "По вопросам регистрации и работы пишите менеджеру.\nИли перезапустите бота командой /start",
        "uz": "Ro‘yxatdan o‘tish va ish bo‘yicha savollar uchun menejerga yozing.\nYoki /start buyrug‘ini bosing"
    }[lang]
    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())