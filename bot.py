import asyncio
import csv
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 841472578

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Reg(StatesGroup):
    language = State()
    name = State()
    phone = State()
    truck_type = State()
    capacity = State()
    truck_photo_front = State()
    truck_photo_back = State()
    license_photo_front = State()
    license_photo_back = State()
    yatt = State()
    regions = State()
    confirm = State()

def lang_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Русский 🇷🇺")
    kb.button(text="O‘zbekcha 🇺🇿")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def main_kb(lang="ru", registered=False):
    kb = ReplyKeyboardBuilder()
    if lang == "ru":
        kb.button(text="📝 Зарегистрироваться")
        if registered:
            kb.button(text="📦 Актуальные грузы")
        kb.button(text="❓ Помощь")
    else:
        kb.button(text="📝 Ro‘yxatdan o‘tish")
        if registered:
            kb.button(text="📦 Joriy yuklar")
        kb.button(text="❓ Yordam")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def back_kb(lang="ru"):
    kb = ReplyKeyboardBuilder()
    kb.button(text="⬅️ Назад" if lang == "ru" else "⬅️ Orqaga")
    return kb.as_markup(resize_keyboard=True)

def truck_type_kb(lang="ru"):
    types = [
        "Тент", "Рефрижератор", "Бортовой",
        "Площадка без бортов", "Контейнеровоз",
        "Одиночка 60 куб.м.", "Паровоз 120 куб.м."
    ]
    kb = ReplyKeyboardBuilder()
    for t in types:
        kb.button(text=t)
    kb.button(text="⬅️ Назад" if lang == "ru" else "⬅️ Orqaga")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def yatt_kb(lang="ru"):
    kb = ReplyKeyboardBuilder()
    if lang == "ru":
        kb.button(text="Да, есть ИП")
        kb.button(text="Нет, нужно открыть")
        kb.button(text="В процессе")
    else:
        kb.button(text="Ha, YaTT bor")
        kb.button(text="Yo‘q, ochish kerak")
        kb.button(text="Jarayonda")
    kb.button(text="⬅️ Назад" if lang == "ru" else "⬅️ Orqaga")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

REGIONS = [
    "Андижанская область", "Бухарская область", "Джизакская область",
    "Кашкадарьинская область", "Навоийская область", "Наманганская область",
    "Самаркандская область", "Сурхандарьинская область", "Сырдарьинская область",
    "Ташкентская область", "Ферганская область", "Хорезмская область"
]

def regions_kb(lang="ru"):
    kb = ReplyKeyboardBuilder()
    kb.button(text="✅ Все регионы")
    for r in REGIONS:
        kb.button(text=r)
    kb.button(text="✅ Готово")
    kb.button(text="⬅️ Назад" if lang == "ru" else "⬅️ Orqaga")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def save_driver(data: dict):
    file_exists = os.path.isfile("drivers.csv")
    with open("drivers.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# === Web server для Render ===
async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server started on port {port}")

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! / Здравствуйте!\n\n"
        "OQ YOL — doimiy yuklar tent mashinalar uchun.\n"
        "Постоянные грузы для большегрузных машин по всему Узбекистану.\n\n"
        "Выберите язык / Tilni tanlang:",
        reply_markup=lang_kb()
    )
    await state.set_state(Reg.language)

@dp.message(Reg.language, F.text.in_(["Русский 🇷🇺", "O‘zbekcha 🇺🇿"]))
async def set_lang(message: types.Message, state: FSMContext):
    lang = "ru" if "Русский" in message.text else "uz"
    await state.update_data(lang=lang, registered=False)
    text = "Отлично! Нажмите «Зарегистрироваться», чтобы начать." if lang == "ru" else "Ajoyib! Ro‘yxatdan o‘tish uchun tugmani bosing."
    await message.answer(text, reply_markup=main_kb(lang, registered=False))
    await state.set_state(None)

@dp.message(F.text.in_(["📝 Зарегистрироваться", "📝 Ro‘yxatdan o‘tish"]))
async def start_reg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Введите ваше ФИО (полностью):" if lang == "ru" else "To‘liq F.I.Sh.ingizni yozing:"
    await message.answer(text, reply_markup=back_kb(lang))
    await state.set_state(Reg.name)

@dp.message(Reg.name)
async def get_name(message: types.Message, state: FSMContext):
    if message.text in ["⬅️ Назад", "⬅️ Orqaga"]:
        await start(message, state)
        return
    await state.update_data(name=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Ваш номер телефона (+998...):" if lang == "ru" else "Telefon raqamingiz (+998...):"
    await message.answer(text, reply_markup=back_kb(lang))
    await state.set_state(Reg.phone)

@dp.message(Reg.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if message.text in ["⬅️ Назад", "⬅️ Orqaga"]:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = "Введите ваше ФИО (полностью):" if lang == "ru" else "To‘liq F.I.Sh.ingizni yozing:"
        await message.answer(text, reply_markup=back_kb(lang))
        await state.set_state(Reg.name)
        return
    await state.update_data(phone=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Выберите тип кузова:" if lang == "ru" else "Kuzov turini tanlang:"
    await message.answer(text, reply_markup=truck_type_kb(lang))
    await state.set_state(Reg.truck_type)

@dp.message(Reg.truck_type)
async def get_truck_type(message: types.Message, state: FSMContext):
    if message.text in ["⬅️ Назад", "⬅️ Orqaga"]:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = "Ваш номер телефона (+998...):" if lang == "ru" else "Telefon raqamingiz (+998...):"
        await message.answer(text, reply_markup=back_kb(lang))
        await state.set_state(Reg.phone)
        return
    if message.text not in ["Тент", "Рефрижератор", "Бортовой", "Площадка без бортов", "Контейнеровоз", "Одиночка 60 куб.м.", "Паровоз 120 куб.м."]:
        await message.answer("Выберите тип из списка.")
        return
    await state.update_data(truck_type=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Укажите грузоподъёмность в тоннах (например: 20):" if lang == "ru" else "Yuk ko‘tarish qobiliyatini tonnada yozing (masalan: 20):"
    await message.answer(text, reply_markup=back_kb(lang))
    await state.set_state(Reg.capacity)

@dp.message(Reg.capacity)
async def get_capacity(message: types.Message, state: FSMContext):
    if message.text in ["⬅️ Назад", "⬅️ Orqaga"]:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = "Выберите тип кузова:" if lang == "ru" else "Kuzov turini tanlang:"
        await message.answer(text, reply_markup=truck_type_kb(lang))
        await state.set_state(Reg.truck_type)
        return
    await state.update_data(capacity=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Отправьте фото техпаспорта (лицевая сторона):" if lang == "ru" else "Texnik pasport fotosini yuboring (old tomoni):"
    await message.answer(text, reply_markup=back_kb(lang))
    await state.set_state(Reg.truck_photo_front)

@dp.message(Reg.truck_photo_front, F.photo)
async def get_truck_photo_front(message: types.Message, state: FSMContext):
    await state.update_data(truck_photo_front=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Отправьте фото техпаспорта (задняя сторона):" if lang == "ru" else "Texnik pasport fotosini yuboring (orqa tomoni):"
    await message.answer(text, reply_markup=back_kb(lang))
    await state.set_state(Reg.truck_photo_back)

@dp.message(Reg.truck_photo_back, F.photo)
async def get_truck_photo_back(message: types.Message, state: FSMContext):
    await state.update_data(truck_photo_back=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Отправьте фото водительских прав (лицевая сторона):" if lang == "ru" else "Haydovchilik guvohnomasi fotosini yuboring (old tomoni):"
    await message.answer(text, reply_markup=back_kb(lang))
    await state.set_state(Reg.license_photo_front)

@dp.message(Reg.license_photo_front, F.photo)
async def get_license_photo_front(message: types.Message, state: FSMContext):
    await state.update_data(license_photo_front=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Отправьте фото водительских прав (задняя сторона):" if lang == "ru" else "Haydovchilik guvohnomasi fotosini yuboring (orqa tomoni):"
    await message.answer(text, reply_markup=back_kb(lang))
    await state.set_state(Reg.license_photo_back)

@dp.message(Reg.license_photo_back, F.photo)
async def get_license_photo_back(message: types.Message, state: FSMContext):
    await state.update_data(license_photo_back=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = "Есть ли у вас ИП?" if lang == "ru" else "YaTT bormi?"
    await message.answer(text, reply_markup=yatt_kb(lang))
    await state.set_state(Reg.yatt)

@dp.message(Reg.yatt)
async def get_yatt(message: types.Message, state: FSMContext):
    if message.text in ["⬅️ Назад", "⬅️ Orqaga"]:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = "Отправьте фото водительских прав (задняя сторона):" if lang == "ru" else "Haydovchilik guvohnomasi fotosini yuboring (orqa tomoni):"
        await message.answer(text, reply_markup=back_kb(lang))
        await state.set_state(Reg.license_photo_back)
        return

    await state.update_data(yatt=message.text, selected_regions=[])
    data = await state.get_data()
    lang = data.get("lang", "ru")

    if "Нет" in message.text or "Yo‘q" in message.text:
        if lang == "ru":
            guide = (
                "Пошаговый план открытия ИП онлайн:\n\n"
                "1. Получите ЭЦП (электронную подпись) на e-imzo.uz или в Центре госуслуг.\n"
                "2. Зайдите на my.gov.uz или new.birdarcha.uz.\n"
                "3. Выберите услугу «Регистрация индивидуального предпринимателя».\n"
                "4. Заполните данные (ПИНФЛ, адрес, вид деятельности, налоговый режим).\n"
                "5. Подпишите заявление ЭЦП и оплатите госпошлину (онлайн дешевле).\n"
                "6. Получите подтверждение (обычно до 30 минут).\n\n"
                "После этого можно продолжить регистрацию в боте.\n\n"
                "Если возникнут трудности с открытием ИП — напишите мне лично: @ваш_username"
            )
        else:
            guide = (
                "YaTTni onlayn ochish bo‘yicha qisqa reja:\n\n"
                "1. ERI (elektron imzo) oling — e-imzo.uz yoki DXM.\n"
                "2. my.gov.uz yoki new.birdarcha.uz ga kiring.\n"
                "3. «Yakka tartibdagi tadbirkorni ro‘yxatdan o‘tkazish» xizmatini tanlang.\n"
                "4. Ma’lumotlarni to‘ldiring (JShShIR, manzil, faoliyat turi).\n"
                "5. ERI bilan imzolang va boj to‘lang (onlayn arzonroq).\n"
                "6. Tasdiq oling (odatda 30 daqiqagacha).\n\n"
                "Keyin botda ro‘yxatdan o‘tishni davom ettiring.\n\n"
                "Agar qiyinchiliklar bo‘lsa — menga yozing: @ваш_username"
            )
        await message.answer(guide)

    text = "Выберите регионы, в которых готовы работать (можно несколько или все сразу). Когда закончите — нажмите «✅ Готово»" if lang == "ru" else "Ishlamoqchi bo‘lgan hududlarni tanlang (bir nechtasini yoki hammasini). Tugatgach «✅ Tayyor» tugmasini bosing"
    await message.answer(text, reply_markup=regions_kb(lang))
    await state.set_state(Reg.regions)

@dp.message(Reg.regions)
async def get_regions(message: types.Message, state: FSMContext):
    if message.text in ["⬅️ Назад", "⬅️ Orqaga"]:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = "Есть ли у вас ИП?" if lang == "ru" else "YaTT bormi?"
        await message.answer(text, reply_markup=yatt_kb(lang))
        await state.set_state(Reg.yatt)
        return

    data = await state.get_data()
    selected = data.get("selected_regions", [])
    lang = data.get("lang", "ru")

    if message.text == "✅ Готово":
        if not selected:
            await message.answer("Выберите хотя бы один регион.")
            return
        await state.update_data(regions=", ".join(selected))
        await show_summary(message, state)
        return

    if message.text == "✅ Все регионы":
        selected = REGIONS.copy()
        await state.update_data(selected_regions=selected)
        await message.answer("Выбраны все регионы.\nНажмите «✅ Готово» для продолжения.")
        return

    if message.text in REGIONS:
        if message.text not in selected:
            selected.append(message.text)
            await state.update_data(selected_regions=selected)
            await message.answer(f"Добавлено: {message.text}\nВыбрано: {', '.join(selected)}")
        else:
            await message.answer("Этот регион уже выбран.")
    else:
        await message.answer("Выберите регион из списка, «✅ Все регионы» или «✅ Готово».")

async def show_summary(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    
    if lang == "ru":
        summary = (f"Проверьте данные:\n\n"
                   f"ФИО: {data['name']}\n"
                   f"Телефон: {data['phone']}\n"
                   f"Тип кузова: {data['truck_type']}\n"
                   f"Грузоподъёмность: {data['capacity']} т\n"
                   f"ИП: {data['yatt']}\n"
                   f"Регионы: {data['regions']}\n\n"
                   f"Всё верно? Напишите «Да» или «Нет»")
    else:
        summary = (f"Ma’lumotlarni tekshiring:\n\n"
                   f"F.I.Sh: {data['name']}\n"
                   f"Telefon: {data['phone']}\n"
                   f"Kuzov: {data['truck_type']}\n"
                   f"Yuk: {data['capacity']} t\n"
                   f"YaTT: {data['yatt']}\n"
                   f"Hududlar: {data['regions']}\n\n"
                   f"Hammasi to‘g‘rimi? «Ha» yoki «Yo‘q» deb yozing")
    
    await message.answer(summary, reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.confirm)

@dp.message(Reg.confirm, F.text.lower().in_(["да", "ha", "yes"]))
async def confirm_reg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    save_driver(data)
    
    lang = data.get("lang", "ru")
    text = {
        "ru": "✅ Регистрация принята!\n\nМенеджер свяжется с вами в течение 24 часов.\nТеперь вам доступны актуальные грузы.",
        "uz": "✅ Ro‘yxatdan o‘tish qabul qilindi!\n\nMenejer 24 soat ichida bog‘lanadi.\nEndi joriy yuklar sizga ochiq."
    }[lang]
    await state.update_data(registered=True)
    await message.answer(text, reply_markup=main_kb(lang, registered=True))
    
    try:
        text_admin = (
            f"🚛 Новый водитель!\n\n"
            f"ФИО: {data.get('name')}\n"
            f"Телефон: {data.get('phone')}\n"
            f"Тип: {data.get('truck_type')}\n"
            f"Грузоподъёмность: {data.get('capacity')} т\n"
            f"ИП/YaTT: {data.get('yatt')}\n"
            f"Регионы: {data.get('regions')}\n"
            f"Username: @{data.get('username', '')}"
        )
        await bot.send_message(ADMIN_ID, text_admin)
        for key, caption in [
            ("truck_photo_front", "Техпаспорт лицевая"),
            ("truck_photo_back", "Техпаспорт задняя"),
            ("license_photo_front", "Права лицевая"),
            ("license_photo_back", "Права задняя"),
        ]:
            if data.get(key):
                await bot.send_photo(ADMIN_ID, data[key], caption=caption)
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление: {e}")
    
    await state.clear()

@dp.message(F.text.in_(["📦 Актуальные грузы", "📦 Joriy yuklar"]))
async def show_loads(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("registered"):
        await message.answer("Сначала завершите регистрацию.")
        return
    await message.answer("Актуальные грузы публикуются в канале:\n@OQYOL_Gruz\n\nПодписывайтесь!")

@dp.message(F.text.in_(["❓ Помощь", "❓ Yordam"]))
async def help_cmd(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if lang == "ru":
        text = (
            "Краткий справочник по регистрации:\n\n"
            "1. Нажмите «Зарегистрироваться»\n"
            "2. Введите ФИО и телефон\n"
            "3. Выберите тип кузова и укажите грузоподъёмность\n"
            "4. Отправьте фото техпаспорта (лицевая и задняя)\n"
            "5. Отправьте фото прав (лицевая и задняя)\n"
            "6. Укажите наличие ИП\n"
            "7. Выберите регионы работы\n"
            "8. Подтвердите данные\n\n"
            "После регистрации откроется доступ к грузам.\n"
            "На любом этапе можно нажать «⬅️ Назад»."
        )
    else:
        text = (
            "Ro‘yxatdan o‘tish bo‘yicha qisqa qo‘llanma:\n\n"
            "1. «Ro‘yxatdan o‘tish» tugmasini bosing\n"
            "2. F.I.Sh. va telefonni kiriting\n"
            "3. Kuzov turini tanlang va yuk ko‘tarish qobiliyatini yozing\n"
            "4. Texpasport fotosini yuboring (old va orqa)\n"
            "5. Guvohnoma fotosini yuboring (old va orqa)\n"
            "6. YaTT borligini ko‘rsating\n"
            "7. Ish hududlarini tanlang\n"
            "8. Ma’lumotlarni tasdiqlang\n\n"
            "Ro‘yxatdan o‘tgach yuklarga kirish ochiladi.\n"
            "Har qanday bosqichda «⬅️ Orqaga» tugmasini bosish mumkin."
        )
    await message.answer(text)

async def main():
    print("Бот запускается...")
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
