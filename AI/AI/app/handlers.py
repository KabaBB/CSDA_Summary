import datetime
import io
import json
import logging
import os
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup
import pdfplumber
from docx import Document
import re
from ebooklib import epub
import ebooklib

import app.keyboards as kb
from bot import bot
from app.summarization import sumextract
from app.parsing import check_news_update
from app.database.requests import create_user, get_user, create_draft, get_drafts, get_draft_by_name, delete_draft, update_user, create_task, get_tasks, delete_task, update_task


router = Router()

# Состояния для суммаризации текста


class SummarizationStates(StatesGroup):
    COLLECTING_TEXT = State()
    COLLECTING_NUM_SENTENCES = State()

# Состояния для суммаризации файла txt


class SummarizationStatesFileTXT(StatesGroup):
    COLLECTING_TEXT = State()
    COLLECTING_NUM_SENTENCES = State()

# Состояния для суммаризации файла pdf


class SummarizationStatesFilePDF(StatesGroup):
    COLLECTING_TEXT = State()
    COLLECTING_NUM_SENTENCES = State()

# Состояния для суммаризации файла docx


class SummarizationStatesFileDocx(StatesGroup):
    COLLECTING_TEXT = State()
    COLLECTING_NUM_SENTENCES = State()


# Состояния для суммаризации файла EPUB
class SummarizationStatesFileEPUB(StatesGroup):
    COLLECTING_TEXT = State()
    COLLECTING_NUM_SENTENCES = State()


# Состояния для регистрации


class RegistrationStates(StatesGroup):
    TG_ID = State()
    COLLECTING_USERNAME = State()
    COLLECTING_NAME = State()
    COLLECTING_SURNAME = State()
    COLLECTING_DATE = State()
    COLLECTING_CITY = State()
    COLLECTING_PHONE = State()
    COLLECTING_EMAIL = State()

# Состояния для обновления данных


class DraftStates(StatesGroup):
    COLLECTING_TEXT = State()
    COLLECTING_NAME = State()
    VIEW_DRAFT = State()

# Состояния для удаления черновика


class DeleteDraftStates(StatesGroup):
    COLLECTING_NAME = State()
    ACCEPT_DELETE = State()

# Состояния для обновления данных


class UpdateUserStates(StatesGroup):
    COLLECTING_NEW_VALUE = State()

# Состояния для черновиков


class TodoStates(StatesGroup):
    ADD_TASK = State()
    VIEW_TASKS = State()
    DELETE_TASK = State()
    UPDATE_TASK = State()
    UPDATE_TASK_TEXT = State()

# Состояния для обновления данных


class TodoStates(StatesGroup):
    ADD_TASK = State()
    VIEW_TASKS = State()
    DELETE_TASK = State()
    UPDATE_TASK = State()
    UPDATE_TASK_TEXT = State()
# Обработчик команды /start


@router.message(CommandStart())
async def start_handler(message: Message):
    tg_id = message.from_user.id
    if not await get_user(tg_id):
        await message.answer('Привествую тебя! Пожалуйста, зарегистрируйтесь', reply_markup=kb.registration)
    else:
        await message.answer('Привествую тебя! Нажми на кнопку ниже, чтобы начать', reply_markup=kb.start)


@router.message(Command('help'))
async def help_handler(message: Message):
    await message.answer(f'Для начала работы нажмите /start\nДля помощи напишите: @chikubrikule322')

# Начало работы с ботом


@router.callback_query(F.data == 'register')
async def register_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Начало регистрации')
    await callback.message.answer('Введите ваше имя')
    await state.set_state(RegistrationStates.COLLECTING_NAME)

# Обработчик регистрации


@router.message(RegistrationStates.COLLECTING_NAME)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите вашу фамилию')
    await state.set_state(RegistrationStates.COLLECTING_SURNAME)

# Обработчик фамилии


@router.message(RegistrationStates.COLLECTING_SURNAME)
async def collect_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(RegistrationStates.COLLECTING_USERNAME)
    await state.update_data(COLLECTING_USERNAME=message.from_user.username)
    await state.set_state(RegistrationStates.TG_ID)
    await state.update_data(TG_ID=message.from_user.id)
    await message.answer('Введите вашу дату рождения')
    await state.set_state(RegistrationStates.COLLECTING_DATE)

# Обработчик даты рождения


# Обработчик даты рождения
@router.message(RegistrationStates.COLLECTING_DATE)
async def collect_date(message: Message, state: FSMContext):
    try:
        date_text = message.text.strip()
        try:
            # Попытка разбора даты
            date_obj = datetime.datetime.strptime(date_text, '%d.%m.%Y')
        except ValueError:
            await message.answer('Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например, 31.12.2000).')
            return

        # Дополнительная проверка на корректность даты (например, не будущая дата)
        if date_obj > datetime.datetime.now():
            await message.answer('Дата рождения не может быть в будущем. Пожалуйста, введите корректную дату рождения.')
            return

        await state.update_data(date_of_birth=date_text)
        await message.answer('Введите ваш город')
        await state.set_state(RegistrationStates.COLLECTING_CITY)
    except Exception as e:
        logging.error(f'Error in collect_date: {e}')
        await message.answer('Произошла ошибка, попробуйте позже.')

# Обработчик города


@router.message(RegistrationStates.COLLECTING_CITY)
async def collect_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer('Введите ваш номер телефона')
    await state.set_state(RegistrationStates.COLLECTING_PHONE)


# Обработчик телефона
@router.message(RegistrationStates.COLLECTING_PHONE)
async def collect_phone(message: Message, state: FSMContext):
    try:
        phone = message.text.strip()
        if not re.match(r'^\+\d{1,3}\d{10}$', phone):
            await message.answer('Неверный формат номера телефона. Пожалуйста, введите корректный номер телефона.')
            return
        await state.update_data(phone=phone)
        await message.answer('Введите ваш email')
        await state.set_state(RegistrationStates.COLLECTING_EMAIL)
    except Exception as e:
        logging.error(f'Error in collect_phone: {e}')
        await message.answer('Произошла ошибка, попробуйте позже.')


# Обработчик email
@router.message(RegistrationStates.COLLECTING_EMAIL)
async def collect_email(message: Message, state: FSMContext):
    try:
        email = message.text.strip()
        if not re.match(r'^[\w\.-]+@[\w\.-]+(\.[\w]+)+$', email):
            await message.answer('Неверный формат email. Пожалуйста, введите корректный email адрес.')
            return
        await state.update_data(email=email)
        data = await state.get_data()
        await create_user(data['TG_ID'], data['COLLECTING_USERNAME'], data['name'], data['surname'], data['date_of_birth'], data['city'], data['phone'], data['email'])
        await message.answer('Вы успешно зарегистрировались', reply_markup=kb.start)
        await state.clear()
    except Exception as e:
        logging.error(f'Error in collect_email: {e}')
        await message.answer('Произошла ошибка, попробуйте позже.')

# Обработчик обновления данных


@router.callback_query(F.data == 'update_registration')
async def update_registration_handler(callback: CallbackQuery):
    await callback.answer('Обновление данных')
    await callback.message.answer('Выберите поле для обновления', reply_markup=kb.update_fields)

# Обработчик обновления данных


@router.callback_query(F.data.startswith('update_field_'))
async def update_field_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Обновление данных')
    field = callback.data.split('_')[-1]
    field_display = {
        "name": "имя",
        "surname": "фамилию",
        "date_of_birth": "дату рождения",
        "city": "город",
        "phone": "телефон",
        "email": "email"
    }
    await callback.message.answer(f'Введите новое значение для {field_display.get(field, field)}:')
    await state.update_data(field_to_update=field)
    await state.set_state(UpdateUserStates.COLLECTING_NEW_VALUE)


@router.message(UpdateUserStates.COLLECTING_NEW_VALUE)
async def collect_new_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field_to_update = data.get('field_to_update')
    new_value = message.text
    tg_id = message.from_user.id

    await update_user(tg_id, field_to_update, new_value)
    await message.answer(f'{field_to_update.capitalize()} успешно обновлено')
    await state.clear()

# Обработчик начала работы


@router.callback_query(F.data == 'start')
async def start_handler(callback: CallbackQuery):
    await callback.answer('Вы начали работу')
    await callback.message.answer('Выберете действие', reply_markup=kb.menu)

# Обработчик отправки текста


@router.callback_query(F.data == 'send_text')
async def send_text_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отправьте текст и напишите "end" чтобы закончить')
    await callback.message.answer('Отправьте текст и напишите "end" чтобы закончить')
    await state.set_state(SummarizationStates.COLLECTING_TEXT)

# Обработчик сбора текста


@router.message(SummarizationStates.COLLECTING_TEXT)
async def collect_text(message: Message, state: FSMContext):
    data = await state.get_data()
    collected_text = data.get('COLLECTING_TEXT', '')
    if message.text == 'end':
        await message.answer('Введите количество предложений для суммаризации, их должно быть не больше предложений в исходном тексте')
        await state.update_data(COLLECTING_TEXT=collected_text)
        await state.set_state(SummarizationStates.COLLECTING_NUM_SENTENCES)
    else:
        collected_text += message.text + ' '
        await state.update_data(COLLECTING_TEXT=collected_text)

# Обработчик сбора количества предложений


@router.message(SummarizationStates.COLLECTING_NUM_SENTENCES)
async def collect_num_sentences(message: types.Message, state: FSMContext):
    num_sentences = int(message.text)
    data = await state.get_data()
    collected_text = data.get('COLLECTING_TEXT', '')
    summary = sumextract(collected_text, num_sentences)
    await message.answer(summary, reply_markup=kb.main)
    await state.clear()

# Обработчик отправки файла


@router.callback_query(F.data == 'send_file')
async def send_file_handler(callback: CallbackQuery):
    await callback.answer('Выберите тип файла')
    await callback.message.answer('Выберите тип файла', reply_markup=kb.file)

# Обработчик отправки файла txt


@router.callback_query(F.data == 'send_txt')
async def send_file_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отправьте файл')
    await callback.message.answer('Отправьте файл')
    await state.set_state(SummarizationStatesFileTXT.COLLECTING_TEXT)

# Обработчик сбора текста из файла txt


@router.message(SummarizationStatesFileTXT.COLLECTING_TEXT)
async def collect_file(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_data = await bot.download_file(file_info.file_path)
    text = file_data.getvalue().decode()
    await state.update_data(COLLECTING_TEXT=text)
    await message.answer('Введите количество предложений для суммаризации, их должно быть не больше предложений в исходном тексте')
    await state.set_state(SummarizationStatesFileTXT.COLLECTING_NUM_SENTENCES)

# Обработчик сбора количества предложений


@router.message(SummarizationStatesFileTXT.COLLECTING_NUM_SENTENCES)
async def collect_num_sentences(message: types.Message, state: FSMContext):
    num_sentences = int(message.text)
    data = await state.get_data()
    collected_text = data.get('COLLECTING_TEXT', '')
    summary = sumextract(collected_text, num_sentences)
    file = io.StringIO(summary)
    await message.answer(summary, reply_markup=kb.main)
    await message.answer_document(
        document=types.BufferedInputFile(
            file=file.getvalue().encode("utf-8"),
            filename='summary.txt')
    )
    os.remove('summary.txt')
    await state.clear()

# Обработчик отправки файла pdf


@router.callback_query(F.data == 'send_pdf')
async def send_file_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отправьте файл')
    await callback.message.answer('Отправьте файл')
    await state.set_state(SummarizationStatesFilePDF.COLLECTING_TEXT)

# Обработчик сбора текста из файла pdf


@router.message(SummarizationStatesFilePDF.COLLECTING_TEXT)
async def collect_file(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_data = await bot.download_file(file_info.file_path)

    with pdfplumber.open(file_data) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()

    await state.update_data(COLLECTING_TEXT=text)
    await message.answer('Введите количество предложений для суммаризации, их должно быть не больше предложений в исходном тексте')
    await state.set_state(SummarizationStatesFilePDF.COLLECTING_NUM_SENTENCES)

# Обработчик сбора количества предложений


@router.message(SummarizationStatesFilePDF.COLLECTING_NUM_SENTENCES)
async def collect_num_sentences(message: types.Message, state: FSMContext):
    num_sentences = int(message.text)
    data = await state.get_data()
    collected_text = data.get('COLLECTING_TEXT', '')
    summary = sumextract(collected_text, num_sentences)
    await message.answer(summary, reply_markup=kb.main)
    file = io.StringIO(summary)
    await message.answer_document(
        document=types.BufferedInputFile(
            file=file.getvalue().encode("utf-8"),
            filename='summary.txt')
    )
    os.remove('summary.txt')
    await state.clear()

# Обработчик отправки файла docx


@router.callback_query(F.data == 'send_docx')
async def send_file_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отправьте файл')
    await callback.message.answer('Отправьте файл')
    await state.set_state(SummarizationStatesFileDocx.COLLECTING_TEXT)

# Обработчик сбора текста из файла docx


@router.message(SummarizationStatesFileDocx.COLLECTING_TEXT)
async def collect_file(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_data = await bot.download_file(file_info.file_path)

    doc = Document(file_data)
    text = '\n'.join([p.text for p in doc.paragraphs])

    await state.update_data(COLLECTING_TEXT=text)
    await message.answer('Введите количество предложений для суммаризации, их должно быть не больше предложений в исходном тексте')
    await state.set_state(SummarizationStatesFileDocx.COLLECTING_NUM_SENTENCES)

# Обработчик сбора количества предложений


@router.message(SummarizationStatesFileDocx.COLLECTING_NUM_SENTENCES)
async def collect_num_sentences(message: types.Message, state: FSMContext):
    num_sentences = int(message.text)
    data = await state.get_data()
    collected_text = data.get('COLLECTING_TEXT', '')
    summary = sumextract(collected_text, num_sentences)
    await message.answer(summary, reply_markup=kb.main)
    file = io.StringIO(summary)
    await message.answer_document(
        document=types.BufferedInputFile(
            file=file.getvalue().encode("utf-8"),
            filename='summary.txt')
    )
    os.remove('summary.txt')
    await state.clear()


# Обработчик отправки файла epub
@router.callback_query(F.data == 'send_epub')
async def send_file_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Отправьте файл')
    await callback.message.answer('Отправьте файл')
    await state.set_state(SummarizationStatesFileEPUB.COLLECTING_TEXT)

# Обработчик сбора текста из файла epub


@router.message(SummarizationStatesFileEPUB.COLLECTING_TEXT)
async def collect_file(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_data = await bot.download_file(file_info.file_path)

    # Сохранение файла на диск
    temp_file_path = 'temp.epub'
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_data.read())

    # Чтение и извлечение текста из EPUB
    book = epub.read_epub(temp_file_path)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    text = []
    for item in items:
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        text.append(soup.get_text())

    collected_text = '\n'.join(text)

    # Удаление временного файла
    os.remove(temp_file_path)

    await state.update_data(COLLECTING_TEXT=collected_text)
    await message.answer('Введите количество предложений для суммаризации, их должно быть не больше предложений в исходном тексте')
    await state.set_state(SummarizationStatesFileEPUB.COLLECTING_NUM_SENTENCES)

# Обработчик сбора количества предложений для epub


@router.message(SummarizationStatesFileEPUB.COLLECTING_NUM_SENTENCES)
async def collect_num_sentences(message: types.Message, state: FSMContext):
    num_sentences = int(message.text)
    data = await state.get_data()
    collected_text = data.get('COLLECTING_TEXT', '')
    summary = sumextract(collected_text, num_sentences)

    await message.answer(summary, reply_markup=kb.main)
    file = io.StringIO(summary)
    await message.answer_document(
        document=types.BufferedInputFile(
            file=file.getvalue().encode("utf-8"),
            filename='summary.txt')
    )
    await state.clear()

# Обработчик отправки новостей


@router.callback_query(F.data == 'send_news')
async def send_news_handler(callback: CallbackQuery):
    await callback.answer('Выберите новость')
    await callback.message.answer(text='Выберите новость', reply_markup=kb.send_news)

# Обработчик отправки всех новостей


@router.callback_query(F.data == 'send_all_news')
async def send_news_handler(callback: CallbackQuery):
    await callback.answer('Все новости')
    with open("app/news_dict.json") as file:
        news_dict = json.load(file)
        for k, v in sorted(news_dict.items()):
            news = f"{datetime.datetime.fromtimestamp(v['article_date_timestamp'])}\n" \
                f"{v['article_url']}"
            await callback.message.answer(news)

# Обработчик отправки последней новости


@router.callback_query(F.data == 'send_fresh_news')
async def send_news_handler(callback: CallbackQuery):
    await callback.answer('Последние новости')
    with open("app/news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-1:]:
        news = f"{datetime.datetime.fromtimestamp(v['article_date_timestamp'])}\n" \
            f"{v['article_url']}"

        await callback.message.answer(news)

# Сохранение черновиков


@router.callback_query(F.data == 'save_draft')
async def save_draft_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Введите текст черновика')
    await callback.message.answer('Введите текст черновика')
    await state.set_state(DraftStates.COLLECTING_TEXT)

# Обработчик сбора текста черновика


@router.message(DraftStates.COLLECTING_TEXT)
async def collect_draft_text(message: Message, state: FSMContext):
    await state.update_data(COLLECTING_TEXT=message.text)
    await message.answer('Введите имя черновика')
    await state.set_state(DraftStates.COLLECTING_NAME)

# Обработчик сбора имени черновика


@router.message(DraftStates.COLLECTING_NAME)
async def collect_draft_name(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get('COLLECTING_TEXT', '')
    name = message.text
    tg_id = message.from_user.id
    await create_draft(tg_id, name, text)
    await message.answer(f'Черновик "{name}" сохранен', reply_markup=kb.main)
    await state.clear()

# Просмотр черновиков


@router.callback_query(F.data == "view_drafts")
async def view_drafts_handler(callback: CallbackQuery):
    await callback.answer('Черновики')
    tg_id = callback.from_user.id
    drafts = await get_drafts(tg_id)
    if drafts:
        await callback.message.answer('Ваши черновики:')
        await callback.message.answer('\n'.join([f'{draft.name}' for draft in drafts]), reply_markup=kb.menu_drafts)
    else:
        await callback.message.answer('У вас нет сохраненных черновиков', reply_markup=kb.menu)

# Просмотр черновика по имени


@router.callback_query(F.data == "find_draft_by_name")
async def get_draft_by_name_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Просмотр черновиков')
    await callback.message.answer('Введите название черновика')
    await state.set_state(DraftStates.VIEW_DRAFT)

# Обработчик просмотра черновика по имени


@router.message(DraftStates.VIEW_DRAFT)
async def view_draft_by_name(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    name = message.text
    draft = await get_draft_by_name(tg_id, name)
    if draft:
        await message.answer(f'Черновик "{name}":\n{draft.text}', reply_markup=kb.menu)
    else:
        await message.answer(f'Черновик с названием "{name}" не найден', reply_markup=kb.menu)
    await state.clear()

# Удаление черновика


@router.callback_query(F.data == 'delete_draft')
async def delete_draft_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Удаление черновика')
    await callback.message.answer('Введите название черновика')
    await state.set_state(DeleteDraftStates.COLLECTING_NAME)

# Обработчик сбора имени черновика для удаления


@router.message(DeleteDraftStates.COLLECTING_NAME)
async def delete_draft_name(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    name = message.text
    draft = await get_draft_by_name(tg_id, name)
    if not draft:
        await message.answer(f'Черновик с названием "{name}" не найден', reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer('Вы уверены, что хотите удалить черновик?', reply_markup=kb.yes_no)
        await state.update_data(draft=draft)
        await state.set_state(DeleteDraftStates.ACCEPT_DELETE)

# Обработчик подтверждения удаления черновика


@router.message(DeleteDraftStates.ACCEPT_DELETE)
async def delete_draft_handler(message: Message, state: FSMContext):
    await state.update_data(accept=message.text)
    data = await state.get_data()
    draft = data['draft']
    accept = data['accept']
    if accept == 'Да':
        await delete_draft(draft.tg_id, draft.name)
        await message.answer('Черновик удален', reply_markup=kb.main)
    else:
        await message.answer('Черновик не удален', reply_markup=kb.main)

        # Добавление задачи

# Обработчик добавления задачи


@router.callback_query(F.data == 'add_task')
async def add_task_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Введите задачу')
    await callback.message.answer('Введите задачу')
    await state.set_state(TodoStates.ADD_TASK)

# Обработчик сохранения задачи


@router.message(TodoStates.ADD_TASK)
async def save_task(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    task_text = message.text
    await create_task(tg_id, task_text)
    await message.answer(f'Задача "{task_text}" добавлена', reply_markup=kb.main)
    await state.clear()

# Просмотр задач


@router.callback_query(F.data == 'view_tasks')
async def view_tasks_handler(callback: CallbackQuery):
    await callback.answer('Задачи')
    tg_id = callback.from_user.id
    tasks = await get_tasks(tg_id)
    if tasks:
        await callback.message.answer('Ваши задачи:')
        await callback.message.answer('\n'.join([f'{task.id}. {task.text}' for task in tasks]), reply_markup=kb.menu)
    else:
        await callback.message.answer('У вас нет задач', reply_markup=kb.main)

# Удаление задачи


@router.callback_query(F.data == 'delete_task')
async def delete_task_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Введите номер задачи для удаления')
    await callback.message.answer('Введите номер задачи для удаления')
    await state.set_state(TodoStates.DELETE_TASK)

# Обработчик сбора номера задачи для удаления


@router.message(TodoStates.DELETE_TASK)
async def confirm_delete_task(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    task_id = int(message.text)
    await delete_task(tg_id, task_id)
    await message.answer(f'Задача номер {task_id} удалена', reply_markup=kb.menu)
    await state.clear()

# Обновление задачи


@router.callback_query(F.data == 'update_task')
async def update_task_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Введите номер задачи для обновления')
    await callback.message.answer('Введите номер задачи для обновления')
    await state.set_state(TodoStates.UPDATE_TASK)

# Обработчик сбора номера задачи для обновления


@router.message(TodoStates.UPDATE_TASK)
async def collect_update_task_id(message: Message, state: FSMContext):
    await state.update_data(task_id=int(message.text))
    await message.answer('Введите новый текст задачи')
    await state.set_state(TodoStates.UPDATE_TASK_TEXT)

# Обработчик обновления текста задачи


@router.message(TodoStates.UPDATE_TASK_TEXT)
async def update_task_text(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get('task_id')
    new_text = message.text
    tg_id = message.from_user.id
    await update_task(tg_id, task_id, new_text)
    await message.answer(f'Задача номер {task_id} обновлена', reply_markup=kb.menu)
    await state.clear()
