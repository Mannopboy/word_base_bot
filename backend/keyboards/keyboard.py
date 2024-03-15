from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData


def start_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("So'z so'rashni boshlash")],
        [KeyboardButton("So'z qo'shish"), KeyboardButton("Barcha so'zlar")],
        [KeyboardButton("Bob qo'shish"), KeyboardButton("Barcha boblar")],
        [KeyboardButton("Kitob qo'shish"), KeyboardButton("Barcha kitoblar")],
    ], resize_keyboard=True)

    return kb


def word_reply_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Yangi so'z")],
        [KeyboardButton("Orqaga")],
    ], resize_keyboard=True)

    return kb


def word_inline_keyboard() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Javobi', callback_data='answer')],
        [InlineKeyboardButton("Keyingi so'z", callback_data='next_word')]
    ])

    return ikb


def book_inline_keyboard() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Kitobdan so'rash", callback_data='book')],
        [InlineKeyboardButton("Bobdan so'rash", callback_data='chap')]
    ])

    return ikb


def book_reply_keyboard(books) -> ReplyKeyboardMarkup:
    list = []
    for book in books:
        list.append([KeyboardButton(book['name'])])
    kb = ReplyKeyboardMarkup(keyboard=list, resize_keyboard=True)

    return kb


def chap_reply_keyboard(chaps) -> ReplyKeyboardMarkup:
    list = []
    for chap in chaps:
        list.append([KeyboardButton(chap['text'])])
    kb = ReplyKeyboardMarkup(keyboard=list, resize_keyboard=True)

    return kb
