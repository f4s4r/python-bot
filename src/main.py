import os
import logging
import json
from random import randint as ri
from db import set_user_state, get_user_state, add_book, get_book, get_all_books, delete_book, get_dict_ganres, close_connection
from states import States
from admins import is_user_admin
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv



load_dotenv() # загружаем перменнные окружения из .env

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


with open("./src/texts.json", "r") as my_file:
    texts_json = my_file.read()

texts = json.loads(texts_json)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


logger = logging.getLogger(__name__)


def show_book(book_dict):
    id = book_dict["id"]
    genre = book_dict["genre"]
    name_arabic = book_dict["name_arabic"]
    name_russian = book_dict["name_russian"]
    description = book_dict["description"]
    return f"Id книги - {id}\nЖанр - {genre}\nНазвание на арабском - {name_arabic}\nПереведенное название - {name_russian}\nОписание книги - {description}\nКнига добавлена в базу данных"


def logging_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text 
    logger.info(f"\n\nUser {user.first_name} ({user.id}), STATE: {get_user_state(user.id)} sent message: {message_text}\n\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    logger.info(f"User {user_id}" + texts["command"]["start"])

    try:
        set_user_state(user_id, States.None_state.value)

        text = texts["bot_description"]
        logging_message(update=update, context=context)

        keyboard = [
            ["/start"],
            ["/help", "/add", "/delete"],
            ["/all", "/genres", "/books"]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    except Exception as e:
        text_err = texts["error_with_start"]
        logger.error(f"\n\nInvalid using of add, exception {e}\n\n")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=text_err)


    


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    set_user_state(user_id, States.None_state.value)

    logger.info(f"User {user_id}" + texts["command"]["help"])
    
    try:
        text = texts["help"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        logger.info(f"\n\nBot's answer {text}")

    except Exception as e:
        text_err = texts["error_with_help"]
        logger.error(f"Error with {e} in /help")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_err)




async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    set_user_state(user_id, States.None_state.value)
    
    logger.info(f"User {user_id}" + texts["command"]["add"])
    
    if is_user_admin(user_id):
        try:
            context.user_data[user_id] = {}
            text = texts["add_description"] + '\n'

            # пишем возможные жанры, просим создать новый, если нельзя выбрать текущий
            genres_dict = get_dict_ganres()
            keyboard = [[InlineKeyboardButton(key, callback_data=key)] for key in genres_dict.keys()]


            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            set_user_state(update.effective_user.id, States.wait_for_genre.value)
        
        except Exception as e:
            text_err = texts["error_with_add"]
            logger.error(f"\n\nInvalid using of add, exception {e}\n\n")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text_err)
    else:
        text = texts["u_are_not_admin"]
        logger.warning(f"Пользователь {user_id} не является администратором")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def all(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    set_user_state(user_id, States.None_state.value)

    logger.info(f"User {user_id}" + texts["command"]["all"])

    try:
        list_of_dicts = get_all_books()
        text = ""
        if list_of_dicts != []:
            for i in range(len(list_of_dicts)):
                text += show_book(list_of_dicts[i]) + '\n\n'
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            logger.info(f"\n\nBot's answer {text}")
        else:
            text_err = texts["no_books"]
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text_err)
    except Exception as e:
            text_err = texts["errors"]["all"]
            logger.error(f"\n\nInvalid using of add, exception {e}\n\n")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text_err)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    set_user_state(user_id, States.None_state.value)

    logger.info(f"User {user_id}" + texts["command"]["delete"])

    if is_user_admin(user_id):
        try:
            text = texts["wait_for_delete"]
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            set_user_state(user_id, States.wait_for_delete.value) 

        except Exception as e:
            text_err = texts["errors"]["delete"]
            logger.info(f"\n\nInvalid use of delete, exception: {e}\n\n")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text_err)
    else:
        text_warn = texts["u_are_not_admin"]
        logger.warning[f"Пользователь {user_id} не является администратором"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_warn)


async def genres(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    set_user_state(user_id, States.None_state.value)

    logger.info(f"User {user_id}" + texts["command"]["genres"])

    try:
        text = ""
        genre_list = get_dict_ganres()

        for key, list in genre_list.items():
            text += "Жанр " + key + '\n'
            for j in range(len(list)):
                text += '    ' + "Id - " + str(list[j][0]) + ", Название - " + str(list[j][1]) + '\n'

        logging_message(update=update, context=context)
        if text == "":
            text = texts["no_books"]
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)    
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    except Exception as e:
        text_error = texts["error_with_genre"]
        logger.info(f"\n\nInvalid use of genres, exception: {e}\n\n")
        logging_message(update=update, context=context)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)


async def books(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    set_user_state(user_id, States.None_state.value)
    
    logger.info(f"User {user_id}" + texts["command"]["books"])
    
    try:
        text = ""
        logging_message(update=update, context=context)
        genres_dict = get_dict_ganres()
        if genres_dict != {}:
            genres = [key for key, _ in genres_dict.items()]
            random_genre = genres[ri(0, len(genres) - 1)]
            text += f"Случайный жанр - {random_genre}\n\n"
                
            list = genres_dict[random_genre]
            for i in range(len(list)):
                id = list[i][0]
                book_dict = get_book(id)
                text += show_book(book_dict) + '\n\n'
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        else:
            text_err = texts["no_books"]
            logger.warning(text_err)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text_err)
    except Exception as e:
        text_error = texts["error_with_books"]
        logger.error(f"\n\nInvalid use of books, exception: {e}\n\n")
        logging_message(update=update, context=context)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    cur_text = update.effective_message.text

    logging_message(update, context)
    CURRENT_STATE = get_user_state(user_id)

    try:
        if CURRENT_STATE == States.wait_for_genre.value:

            logger.info(f"\n\nUser {update.effective_user.name} trying to pick genre \"{cur_text}\"\n\n")

            try:
                text = texts["genre_was_choosed"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                logger.info(f"\n\nBot's answer: {text}\n\n")
                
                context.user_data.setdefault(user_id, {})  # Создаст пустой dict, если его нет
                context.user_data[user_id]["genre"] = cur_text

                set_user_state(user_id, States.wait_arabic.value)
                
                text_wait = texts["choose_arabic"]
                logger.info(f"\n\nBot's answer: {text_wait}\n\n")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_wait)
                
            except Exception as e:
                text_error = texts["error_with_add"]
                logger.info(f"\n\nError with choosing genre by text, {e}\n\n")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)

        elif CURRENT_STATE == States.wait_for_delete.value:

            logger.info(f"\n\nUser{update.effective_user.name} trying to delete id: {cur_text}\n\n")

            try:
                book_id = int(cur_text)
                book = get_book(book_id)
                if book:
                    delete_book(book_id)
                    text = texts["book_deleted"]
                    logger.info(f"\n\nUser{update.effective_user.name} deleted id {cur_text}\n\n")
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Книга с ID {book_id} не найдена.")
            except Exception as e:
                text_error = texts["error_with_delete"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)
                set_user_state(user_id)
                logger.info(f"\n\nInvalid using add, exception, wrong response {e}\n\n")
                
        elif CURRENT_STATE == States.wait_arabic.value:

            logger.info(f"\n\nUser {update.effective_user.name} trying to pick arabic name \"{cur_text}\"\n\n")
            
            try:
                context.user_data.setdefault(user_id, {})
                context.user_data[user_id]["name_arabic"] = cur_text


                set_user_state(user_id, States.wait_rus.value)
                
                text = texts["arabic_was_choosed"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                logger.info(f"\n\nBot's answer: {text}\n\n")

            except Exception as e:
                text_error = texts["error_with_arabic"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)
                logger.info(f"\n\Error with arabic name, wrong response {e}\n\n")

        elif CURRENT_STATE == States.wait_rus.value:

            logger.info(f"\n\nUser {update.effective_user.name} trying to pick rus name \"{cur_text}\"\n\n")

            try:
                context.user_data.setdefault(user_id, {})
                context.user_data[user_id]["name_russian"] = cur_text
                
                set_user_state(user_id, States.wait_decr.value)

                text = texts["rus_was_choosed"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                logger.info(f"\n\nBot's answer: {text}\n\n")
                
            except Exception as e:
                text_error = texts["error_with_rus"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)
                logger.info(f"\n\Error with rus name, wrong response {e}\n\n")

        elif CURRENT_STATE == States.wait_decr.value:

            logger.info(f"\n\nUser {update.effective_user.name} trying to write description \"{cur_text}\"\n\n")

            try:
                # проверяем наличие context.user_data
                #if user_id not in context.user_data:

                context.user_data.setdefault(user_id, {})  # Если словаря нет, создаем пустой
                context.user_data[user_id]["description"] = cur_text

                book_id = add_book(
                    update.effective_user.id,
                    context.user_data[user_id]["genre"],
                    context.user_data[user_id]["name_arabic"],
                    context.user_data[user_id]["name_russian"],
                    context.user_data[user_id]["description"]
                )
                #else:
                #    logging.error(f"context.user_data отустствует, context")
                
                
                text_confirm_write = show_book(get_book(book_id))
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_confirm_write)
                logger.info(f"\n\nBot's answer: {text_confirm_write}\n\n")

                set_user_state(user_id)

                text = texts["desc_was_choosed"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                logger.info(f"\n\nBot's answer: {text}\n\n")
                
            except Exception as e:
                text_error = texts["error_with_desc"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)
                logger.info(f"\n\Error with desctiption, wrong response {e}\n\n")


    except Exception as e:
        text = texts["errors"]["handle_message"]
        logger.info(f"\n\nInvalid response, exception {e}\n\n")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_error)

    


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user_id = update.effective_user.id
    query = update.callback_query
    data = query.data

    logger.info(f"\n\nUser {user_id} clicked on \"{data}\"\n\n")

    
    await query.answer()

    
    logger.info(f"\n\nUser {user_id} нажал кнопку: {data}\n\n")

    text = texts["genre_was_choosed"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    logger.info(f"\n\nBot's answer: {text}\n\n")

    context.user_data.setdefault(user_id, {}) 
    context.user_data[user_id]["genre"] = data

    
    set_user_state(user_id, States.wait_arabic.value)

    text_wait = texts["choose_arabic"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_wait)
    logger.info(f"\n\nBot's answer: {text_wait}\n\n")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    add_handler = CommandHandler('add', add)
    all_handler = CommandHandler('all', all)
    delete_handler = CommandHandler('delete', delete)
    genres_handler = CommandHandler('genres', genres)
    books_handler = CommandHandler('books', books)
    help_handler = CommandHandler('help', help)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    button_handler = CallbackQueryHandler(button)
    application.add_handlers([start_handler, help_handler, add_handler, all_handler, delete_handler, message_handler, genres_handler, books_handler, button_handler])
    
    
    application.run_polling()
    close_connection()
