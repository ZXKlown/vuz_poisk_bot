import json
from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN
from cities import letters, cities_by_letter

# Инициализация бота и роутера
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()

# Классы CallbackData
class CitiesCallbackFactory(CallbackData, prefix="cities"):
    letter_id: int

class CitySelectCallbackFactory(CallbackData, prefix="city"):
    city_name: str

class SpecializationSelectCallbackFactory(CallbackData, prefix="spec"):
    specialization_id: int
    city_name: str

class ConfirmationCallbackFactory(CallbackData, prefix="confirm"):
    city_name: str
    specialization_name: str
    confirmed: bool

# Загрузка данных
with open("vuz_data_full.json", "r", encoding="utf-8") as file:
    vuz_data = json.load(file)

# Словарь для хранения данных пользователей
user_data = {}


# Создание клавиатуры с буквами
builder = InlineKeyboardBuilder()
for letter_id, letter in enumerate(letters):
    builder.add(
        InlineKeyboardButton(
            text=letter,
            callback_data=CitiesCallbackFactory(letter_id=letter_id).pack()
        )
    )
markup = builder.adjust(7).as_markup()


# Обработчик команды /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text="Выбери первую букву своего города!",
        reply_markup=markup
    )


@router.message(Command("help"))
async def info_command(message: Message):
    text = (f"Добро пожаловать! Этот бот поможет тебе быстро найти информацию о вузах России.\n"
            f"Чтобы начать, просто нажми /start или напиши команду /start.")
    await message.answer(text)

# Обработчик выбора буквы
@router.callback_query(CitiesCallbackFactory.filter())
async def process_letter_selection(callback: CallbackQuery, callback_data: CitiesCallbackFactory):
    letter = letters[callback_data.letter_id]
    city_list = cities_by_letter.get(letter, [])

    builder = InlineKeyboardBuilder()
    for city in city_list:
        builder.add(
            InlineKeyboardButton(
                text=city,
                callback_data=CitySelectCallbackFactory(city_name=city).pack()
            )
        )

    await callback.message.edit_text(
        text=f"Города на букву {letter}:",
        reply_markup=builder.adjust(2).as_markup()
    )
    await callback.answer()


# Загрузка данных о специализациях по городам
with open("cities_specializations.json", "r", encoding="utf-8") as file:
    city_specializations = json.load(file)


# Обработчик выбора города
@router.callback_query(CitySelectCallbackFactory.filter())
async def process_city_selection(callback: CallbackQuery, callback_data: CitySelectCallbackFactory):
    city_name = callback_data.city_name
    specializations = city_specializations.get(city_name, [])

    builder = InlineKeyboardBuilder()
    for idx, (spec_name, spec_count, _) in enumerate(specializations):
        builder.add(
            InlineKeyboardButton(
                text=f"{spec_name} ({spec_count})",
                callback_data=SpecializationSelectCallbackFactory(city_name=city_name, specialization_id=idx).pack()
            )
        )

    await callback.message.edit_text(
        text=f"Отлично! Теперь выбери специальность, которая тебя интересует в городе {city_name}",
        reply_markup=builder.adjust(1).as_markup()
    )
    await callback.answer()


# Обработчик выбора специализации
@router.callback_query(SpecializationSelectCallbackFactory.filter())
async def process_specialization_selection(callback: CallbackQuery, callback_data: SpecializationSelectCallbackFactory):
    city_name = callback_data.city_name
    specialization_id = callback_data.specialization_id
    specialization = city_specializations[city_name][specialization_id][0]

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✅ Да",
            callback_data=ConfirmationCallbackFactory(city_name=city_name, specialization_name=specialization,
                                                      confirmed=True).pack()
        ),
        InlineKeyboardButton(
            text="🔙 Вернуться в начало",
            callback_data="go_back_to_start"  # Уникальный callback для возврата
        )
    )

    await callback.message.edit_text(
        text=f"Вы выбрали:\nГород: {city_name}\nСпециальность: {specialization}\nВы уверены?",
        reply_markup=builder.adjust(2).as_markup()
    )
    await callback.answer()


# Обработчик кнопки "Вернуться в начало"
@router.callback_query(lambda c: c.data == "go_back_to_start")
async def go_back_to_start(callback: CallbackQuery):
    await process_start_command(callback.message)
    await callback.answer()


@router.callback_query(ConfirmationCallbackFactory.filter())
async def process_confirmation(callback: CallbackQuery, callback_data: ConfirmationCallbackFactory):
    city_name = callback_data.city_name
    specialization_name = callback_data.specialization_name

    universities = vuz_data.get(city_name, {}).get(specialization_name, [])

    if not universities:
        await callback.message.edit_text("❌ Университеты не найдены по выбранной специальности.")
        await callback.answer()
        return

    user_data[callback.from_user.id] = {"city": city_name, "spec": specialization_name, "index": 0}
    await send_university_info(callback, callback.from_user.id)
    await callback.answer()

# Функция отправки информации об университете
async def send_university_info(callback: CallbackQuery, user_id: int):
    data = user_data.get(user_id, {})
    city_name = data.get("city")
    specialization_name = data.get("spec")
    index = data.get("index", 0)

    universities = vuz_data.get(city_name, {}).get(specialization_name, [])

    if not universities or index >= len(universities):
        await callback.message.edit_text("❌ Университеты не найдены.")
        return

    university = universities[index]

    text = (
        f"🏫 <b><a href='{university['vuz_link']}'>{university['title']}</a></b>\n"
        f"📚 {university['description']}\n\n"
        f"💰 <b>Стоимость</b>: {' '.join(university['cost'].split()[1:4])}\n"
    )

    # Проверяем наличие бюджета
    if "нет" not in university["budget"].lower():
        budget_parts = university["budget"].split()
        text += f"🎓 <b>Бюджет</b>: {budget_parts[2]}, {budget_parts[-2]} мест\n"

    # Проверяем наличие платного обучения
    if "нет" not in university["paid"].lower():
        paid_parts = university["paid"].split()
        text += f"📖 <b>Платное</b>: {paid_parts[2]}, {paid_parts[-2]} мест\n"

    # Добавляем сворачивающуюся цитату
    text += (
        f"\n📝 <b>Дополнительно</b>: <blockquote>\n"
        f"Общежитие: {university['options_check']['Общежитие']}\n"
        f"Государственный: {university['options_check']['Государственный']}\n"
        f"Воен. уч. центр: {university['options_check']['Воен. уч. центр']}\n"
        f"Бюджетные места: {university['options_check']['Бюджетные места']}\n"
        f"Лицензия/аккредитация: {university['options_check']['Лицензия/аккредитация']}\n"
        f"</blockquote>"
    )

    # Проверка наличия изображения
    image_url = university.get("image_url", "https://example.com/default.jpg")

    # Кнопки навигации
    builder = InlineKeyboardBuilder()
    if index > 0:
        builder.add(InlineKeyboardButton(text="⬅️ Предыдущий", callback_data="previous"))
    if index < len(universities) - 1:
        builder.add(InlineKeyboardButton(text="➡️ Следующий", callback_data="next"))

    # Обновление сообщения
    media = InputMediaPhoto(media=image_url, caption=text, parse_mode=ParseMode.HTML)
    await callback.message.edit_media(media, reply_markup=builder.as_markup())

# Обработчик кнопок "предыдущий" и "следующий"
@router.callback_query(lambda c: c.data in ["previous", "next"])
async def navigate_universities(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})

    if not data:
        await callback.answer("Выберите город и специальность сначала.", show_alert=True)
        return

    city_name = data.get("city")
    specialization_name = data.get("spec")
    universities = vuz_data.get(city_name, {}).get(specialization_name, [])

    if not universities:
        await callback.answer("Университеты не найдены.", show_alert=True)
        return

    if callback.data == "previous" and data["index"] > 0:
        user_data[user_id]["index"] -= 1
    elif callback.data == "next" and data["index"] < len(universities) - 1:
        user_data[user_id]["index"] += 1

    await send_university_info(callback, user_id)
    await callback.answer()