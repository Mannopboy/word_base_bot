from aiogram import Dispatcher, Bot, types, executor
from backend.base import base as db
from backend.keyboards.keyboard import start_keyboard

bot = Bot('6726035555:AAG4HaGtIkSJjmHVETabfneUbSjnWuvRpVc')
dp = Dispatcher(bot)

word = None
word_status = False
word_answer_status = False


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


# @dp.message_handler(commands=["So'z qo'shish"])
# async def add_word(message: types.Message):
#
#     await message.answer("Yangi so'zni kiriting")
#

@dp.message_handler()
async def text(message: types.Message):
    global word_status, word_answer_status, word
    print(word_status)
    print(word_answer_status)
    print(word)
    if word_status and not word_answer_status:
        print(message)
        # await db.add_word(message['from']['id'], )
        word_answer_status = True
        word_status = message['text']
        await message.answer("Yangi so'zni tarjimasini kiriting")
    elif word_status and word_answer_status:
        print(message)
        print(True)
        await db.add_word(message['from']['id'], word, message['text'])
        word_answer_status = False
        word_status = False
        await message.answer("Yangi so'zni kiritildi")
    elif message['text'] == "So'z qo'shish":
        word_status = True
        await message.answer("Yangi so'zni kiriting")
    else:
        print('Nigga')


executor.start_polling(dp, on_startup=on_startup)
