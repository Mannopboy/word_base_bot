import random

from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from backend.base import base as db
from backend.keyboards.keyboard import start_keyboard, word_inline_keyboard, book_reply_keyboard, chap_reply_keyboard, \
    book_inline_keyboard
from backend.states.state import BookState, ChapState, WordState

bot = Bot('6726035555:AAG4HaGtIkSJjmHVETabfneUbSjnWuvRpVc')
dp = Dispatcher(bot, storage=MemoryStorage())

storage = MemoryStorage()
book_status = False
chap_status = False
words_list = []
book_id = 0
chap_id = 0


async def on_startup(_):
    await db.db_start()
    print("Bo't ishga tushdi.")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    username = None
    if message['from']['username']:
        username = message['from']['username']
    await db.add_user(message['from']['id'], username, message['from']['first_name'])
    name = message['from']['first_name']
    await bot.send_message(chat_id=message['from']['id'],
                           text=f"Salom {name}",
                           reply_markup=start_keyboard())


@dp.message_handler(Text(equals="So'z so'rashni boshlash"))
async def start_ask_word(message: types.Message):
    global book_status, chap_status
    book_status = False
    chap_status = False
    await message.reply("So'z so'rash uchun kitob yoki bobni tanlang", reply_markup=book_inline_keyboard())


@dp.callback_query_handler(text='book')
async def answer_word(callback: types.CallbackQuery):
    books = await db.get_books(callback.message['chat']['id'])
    global book_status
    if books:
        book_status = True
        await callback.message.reply(f"So'rash uchun kitoblardan birni tanlang",
                                     reply_markup=book_reply_keyboard(books))


@dp.callback_query_handler(text='chap')
async def answer_word(callback: types.CallbackQuery):
    chaps = await db.get_chaps_for_word(callback.message['chat']['id'])
    global chap_status
    if chaps:
        chap_status = True
        await callback.message.reply(f"So'rash uchun boblardan birni tanlang",
                                     reply_markup=chap_reply_keyboard(chaps))


@dp.message_handler(Text(equals="Kitob qo'shish"))
async def add_book(message: types.Message):
    await message.answer("Yangi kitob nomini kiriting")
    await BookState.name.set()


@dp.message_handler(Text(equals="Orqaga"))
async def back(message: types.Message):
    await bot.send_message(chat_id=message['from']['id'],
                           text="Bosh sahifa",
                           reply_markup=start_keyboard())


@dp.message_handler(Text(equals="Bob qo'shish"))
async def add_chap(message: types.Message):
    books = await db.get_books(message['from']['id'])
    if books:
        await message.answer("Bob qo'shish uchun kitobni tanlang", reply_markup=book_reply_keyboard(books))
        await ChapState.book_id.set()
    else:
        await message.answer("Bob qo'shishdan oldin kitob qo'shing")


@dp.message_handler(Text(equals="Barcha so'zlar"))
async def all_words(message: types.Message):
    words = await db.get_words(message['from']['id'])
    if words:
        text = ''
        for word in words:
            text += f"{word['word']} - {word['answer']} \n"
        await message.answer(text)
    else:
        await message.answer("So'zlar yo'q")


@dp.message_handler(Text(equals="Barcha boblar"))
async def all_chaps(message: types.Message):
    books = await db.get_chaps(message['from']['id'])
    if books:
        for book in books:
            text = f"{book['book']}: \n"
            for chap in book['chaps']:
                text += f"   {chap['name']} \n"
            await message.answer(text)
    else:
        await message.answer("Boblar yo'q")


@dp.message_handler(Text(equals="Barcha kitoblar"))
async def all_books(message: types.Message):
    books = await db.get_books(message['from']['id'])
    if books:
        text = ''
        for book in books:
            text += f"{book['name']}\n"
        await message.answer(text)
    else:
        await message.answer("Kitoblar yo'q")


@dp.message_handler(Text(equals="So'z qo'shish"))
async def add_chap_for_word(message: types.Message):
    books = await db.get_books(message['from']['id'])
    if books:
        await message.answer("So'z qo'shish uchun kitobni tanlang", reply_markup=book_reply_keyboard(books))
        await WordState.book_id.set()
    else:
        await message.answer("So'z qo'shishdan oldin kitob qo'shing")


@dp.message_handler(state=WordState.book_id)
async def get_book_name_for_word(message: types.Message, state: FSMContext) -> None:
    book_id = await db.get_book(message['from']['id'], message['text'])
    async with state.proxy() as data:
        data['book_id'] = book_id
    chaps = await db.get_book_chaps(book_id)
    await message.reply("So'z qo'shish uchun bobni tanlang", reply_markup=chap_reply_keyboard(chaps))
    await WordState.next()


@dp.message_handler(state=WordState.chap_id)
async def get_chap_name_for_word(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        chap_id = await db.get_chap(data['book_id'], message['text'])
        async with state.proxy() as data:
            data['chap_id'] = chap_id
        await message.reply("Yangi so'zni kiriting")
        await WordState.next()


@dp.message_handler(state=WordState.name)
async def get_name_for_word(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message['text']
    await message.reply("Yangi so'zni tarjimasini kiriting")
    await WordState.next()


@dp.message_handler(state=WordState.answer)
async def get_answer_for_word(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['answer'] = message['text']
    status = await db.add_word(state)
    if status:
        await message.reply("Yangi so'z kiritildi !!!", reply_markup=start_keyboard())
    else:
        await message.answer("Bunday so'z bor")
    await state.finish()


@dp.message_handler(state=ChapState.book_id)
async def get_book_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['book_id'] = await db.get_book(message['from']['id'], message['text'])
    await message.reply("Yangi bob nomini kiriting")
    await ChapState.next()


@dp.message_handler(state=ChapState.name)
async def add_chap_state(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message['text']
    status = await db.add_chap(state)
    if status:
        await message.reply("Yangi bob kiritildi !!!", reply_markup=start_keyboard())
    await state.finish()


@dp.message_handler(state=BookState.name)
async def add_book_state(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['user_id'] = message['from']['id']
        data['name'] = message['text']

    status = await db.add_book(state)
    if status:
        await message.reply("Yangi kitob kiritildi !!!", reply_markup=start_keyboard())
    else:
        await message.answer("Bunday kitob bor")
    await state.finish()


@dp.callback_query_handler(text='answer')
async def answer_word(callback: types.CallbackQuery):
    global book_id
    word = callback['message']['text']
    answer = await db.get_word(book_id, word)
    await callback.message.answer(f'<i> {answer} </i>', parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text='next_word')
async def next_question(callback: types.CallbackQuery):
    global words_list
    message = callback['message']
    if words_list:
        new_word = random.choice(words_list)
        await message.answer(f"{new_word['name']}", reply_markup=word_inline_keyboard())
        words_list.remove(new_word)
    else:
        await message.answer(f"Boshqa so'z qolmadi", reply_markup=start_keyboard())


@dp.message_handler()
async def text(message: types.Message):
    global book_status, chap_status, words_list, book_id, chap_id
    if book_status and not chap_status:
        book_id = await db.get_book(message['from']['id'], message.text)
        words_list = await db.get_words_in_book(book_id)
        new_word = random.choice(words_list)
        await message.reply(f"{message.text} dan so'z sorashni boshlandi", reply_markup=start_keyboard())
        await message.answer(f"{new_word['name']}", reply_markup=word_inline_keyboard())
        words_list.remove(new_word)
    elif chap_status and not book_status:
        index = None
        for letter in message['text']:
            if letter == '-':
                index = message['text'].index(letter)
        book_id = await db.get_book_next(message['from']['id'], message['text'][:index - 1])
        chap_id = await db.get_chap_next(book_id, message['text'][index + 2:])
        words_list = await db.get_words_in_chap(chap_id)
        if words_list:
            new_word = random.choice(words_list)
            await message.reply(f"{message.text} dan so'z sorashni boshlandi", reply_markup=start_keyboard())
            await message.answer(f"{new_word['name']}", reply_markup=word_inline_keyboard())
            words_list.remove(new_word)
        else:
            await message.answer(f"Boshqa so'z qolmadi", reply_markup=start_keyboard())


executor.start_polling(dp, on_startup=on_startup)
