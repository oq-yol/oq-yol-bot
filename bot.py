import asyncio
import csv
import os
import logging
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
    truck = State()
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
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

REGIONS = [
    "Андижанская область", "Бухарская область", "Джизакская область",
    "Кашкадарьинская область", "Навоийская область", "Наманганская область",
    "Самаркандская область", "Сурхандарьинская область", "Сырдарьинская область",
    "Ташкентская область", "Ферганская область", "Хорезмская область"
]

def regions_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="✅ Все регионы")
    for r in REGIONS:
        kb.button(text=r)
    kb.button(text="✅ Готово")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

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
        "Постоянные грузы для большегрузных машин по всему Узбекистану.\n\n"
        "Выберите язык / Tilni tanlang:",
        reply_markup=lang_kb()
    )
    await state.set_state(Reg.language)

@dp.message(Reg.language, F.text.in_(["Русский 🇷🇺", "O‘zbekcha 🇺🇿"]))
async def set_lang(message: types.Message, state: FSMContext):
    lang = "ru" if "Русский" in message.text else "uz"
    await state.update_data(lang=lang, registered=False)
    if lang == "ru":
        text = "Отлично! Нажмите «Зарегистрироваться», чтобы начать."
    else:
        text = "Ajoyib! Ro‘yxatdan o‘tish uchun tugmani bosing."
    await message.answer(text, reply_markup=main_kb(lang, registered=False))
    await state.set_state(None)

@dp.message(F.text.in_(["📝 Зарегистрироваться", "📝 Ro‘yxatdan o‘tish"]))
async def start_reg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Введите ваше ФИО (полностью):", "uz": "To‘liq F.I.Sh.ingizni yozing:"}[lang]
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(Reg.name)

@dp.message(Reg.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Ваш номер телефона (+998...):", "uz": "Telefon raqamingiz (+998...):"}[lang]
    await message.answer(text)
    await state.set_state(Reg.phone)

@dp.message(Reg.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Опишите машину (тент / большегруз, объём м³, грузоподъёмность тонн):",
            "uz": "Mashinani tasvirlab bering (tent / og‘ir yuk, hajm m³, yuk ko‘tarish qobiliyati):"}[lang]
    await message.answer(text)
    await state.set_state(Reg.truck)

@dp.message(Reg.truck)
async def get_truck(message: types.Message, state: FSMContext):
    await state.update_data(truck=message.text)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Отправьте фото техпаспорта (лицевая сторона):",
            "uz": "Texnik pasport fotosini yuboring (old tomoni):"}[lang]
    await message.answer(text)
    await state.set_state(Reg.truck_photo_front)

@dp.message(Reg.truck_photo_front, F.photo)
async def get_truck_photo_front(message: types.Message, state: FSMContext):
    await state.update_data(truck_photo_front=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Отправьте фото техпаспорта (задняя сторона):",
            "uz": "Texnik pasport fotosini yuboring (orqa tomoni):"}[lang]
    await message.answer(text)
    await state.set_state(Reg.truck_photo_back)

@dp.message(Reg.truck_photo_back, F.photo)
async def get_truck_photo_back(message: types.Message, state: FSMContext):
    await state.update_data(truck_photo_back=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Отправьте фото водительских прав (лицевая сторона):",
            "uz": "Haydovchilik guvohnomasi fotosini yuboring (old tomoni):"}[lang]
    await message.answer(text)
    await state.set_state(Reg.license_photo_front)

@dp.message(Reg.license_photo_front, F.photo)
async def get_license_photo_front(message: types.Message, state: FSMContext):
    await state.update_data(license_photo_front=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Отправьте фото водительских прав (задняя сторона):",
            "uz": "Haydovchilik guvohnomasi fotosini yuboring (orqa tomoni):"}[lang]
    await message.answer(text)
    await state.set_state(Reg.license_photo_back)

@dp.message(Reg.license_photo_back, F.photo)
async def get_license_photo_back(message: types.Message, state: FSMContext):
    await state.update_data(license_photo_back=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = {"ru": "Есть ли у вас ИП?", "uz": "YaTT bormi?"}[lang]
    await message.answer(text, reply_markup=yatt_kb(lang))
    await state.set_state(Reg.yatt)

@dp.message(Reg.yatt)
async def get_yatt(message: types.Message, state: FSMContext):
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
                "После этого можно продолжить регистрацию в боте."
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
                "Keyin botda ro‘yxatdan o‘tishni davom ettiring."
            )
        await message.answer(guide)

    text = {
        "ru": "Выберите регионы, в которых готовы работать (можно несколько или все сразу). Когда закончите — нажмите «✅ Готово»",
        "uz": "Ishlamoqchi bo‘lgan hududlarni tanlang (bir nechtasini yoki hammasini). Tugatgach «✅ Tayyor» tugmasini bosing"
    }[lang]
    await message.answer(text, reply_markup=regions_kb())
    await state.set_state(Reg.regions)

@dp.message(Reg.regions)
async def get_regions(message: types.Message, state: FSMContext):
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
        await message.answer(f"Выбраны все регионы.\nНажмите «✅ Готово» для продолжения.")
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
                   f"Машина: {data['truck']}\n"
                   f"ИП: {data['yatt']}\n"
                   f"Регионы: {data['regions']}\n\n"
                   f"Всё верно? Напишите «Да» или «Нет»")
    else:
        summary = (f"Ma’lumotlarni tekshiring:\n\n"
                   f"F.I.Sh: {data['name']}\n"
                   f"Telefon: {data['phone']}\n"
                   f"Mashina: {data['truck']}\n"
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
            f"Машина: {data.get('truck')}\n"
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
            "3. Опишите машину\n"
            "4. Отправьте фото техпаспорта (лицевая и задняя)\n"
            "5. Отправьте фото прав (лицевая и задняя)\n"
            "6. Укажите наличие ИП\n"
            "7. Выберите регионы работы\n"
            "8. Подтвердите данные\n\n"
            "После регистрации откроется доступ к грузам."
        )
    else:
        text = (
            "Ro‘yxatdan o‘tish bo‘yicha qisqa qo‘llanma:\n\n"
            "1. «Ro‘yxatdan o‘tish» tugmasini bosing\n"
            "2. F.I.Sh. va telefonni kiriting\n"
            "3. Mashinani tasvirlang\n"
            "4. Texpasport fotosini yuboring (old va orqa)\n"
            "5. Guvohnoma fotosini yuboring (old va orqa)\n"
            "6. YaTT borligini ko‘rsating\n"
            "7. Ish hududlarini tanlang\n"
            "8. Ma’lumotlarni tasdiqlang\n\n"
            "Ro‘yxatdan o‘tgach yuklarga kirish ochiladi."
        )
    await message.answer(text)

async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
