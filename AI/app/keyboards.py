from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Клавиатура для начала работы
start = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Начать', callback_data='start')]])


# Клавиатура для выбора действия
menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Скинуть текст',
                              callback_data='send_text')],
        [InlineKeyboardButton(text='Скинуть файл', callback_data='send_file')],
        [InlineKeyboardButton(text='Узнать новости',
                              callback_data='send_news')],
        [InlineKeyboardButton(text='Создать черновик',
                              callback_data='save_draft')],
        [InlineKeyboardButton(text='Мои черновики',
                              callback_data='view_drafts')],
        [InlineKeyboardButton(text='Удалить черновик',
                              callback_data='delete_draft')],
        [InlineKeyboardButton(text='Добавить задачу',
                              callback_data='add_task')],
        [InlineKeyboardButton(text='Просмотреть задачи',
                              callback_data='view_tasks')],
        [InlineKeyboardButton(text='Обновить задачу',
                              callback_data='update_task')],
        [InlineKeyboardButton(text='Удалить задачу',
                              callback_data='delete_task')],
        [InlineKeyboardButton(text='Обновление данных',
                              callback_data='update_registration')],

    ]
)


# Клавиатура для отправки файла
file = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
    text='Отпрвить PDF', callback_data='send_pdf'), InlineKeyboardButton(text='Отправить TXT', callback_data='send_txt')],
    [InlineKeyboardButton(text='Отправить DOCX', callback_data='send_docx')],
    [InlineKeyboardButton(text='Отправить EPUB', callback_data='send_epub')]])


# Клавиатура для перехода в главное меню
main = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Главное меню', callback_data='start')]])


# Клавиатура для получения новостей
send_news = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Получить все новости', callback_data='send_all_news')],
                                                  [InlineKeyboardButton(text='Получить последнюю новость', callback_data='send_fresh_news')]])

# Клавиатура для регистрации
registration = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
    text='Зарегистрироваться', callback_data='register')]])

# Клавиатура для выбора черновика

menu_drafts = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
    text='Выбрать черновик', callback_data='find_draft_by_name')],])

# Клавиатура для удаления черновика
yes_no = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='Да'),
        KeyboardButton(text='Нет')
    ]
], resize_keyboard=True, one_time_keyboard=True)

# Клавиатура для обновления данных
update_fields = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Имя", callback_data="update_field_name")],
    [InlineKeyboardButton(
        text="Фамилия", callback_data="update_field_surname")],
    [InlineKeyboardButton(text="Дата рождения",
                          callback_data="update_field_birth")],
    [InlineKeyboardButton(text="Город", callback_data="update_field_city")],
    [InlineKeyboardButton(text="Телефон", callback_data="update_field_phone")],
    [InlineKeyboardButton(text="Email", callback_data="update_field_email")]
])
