from aiogram.dispatcher.filters.state import StatesGroup, State


class BookState(StatesGroup):
    name = State()


class ChapState(StatesGroup):
    book_id = State()
    name = State()


class WordState(StatesGroup):
    book_id = State()
    chap_id = State()
    name = State()
    answer = State()


class WordListState(StatesGroup):
    book_id = State()
    chap_id = State()
    list = State()

