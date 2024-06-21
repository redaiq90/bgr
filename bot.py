import os
import time
from PIL import Image
from rembg import remove
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user = update.message.from_user.first_name
    await context.bot.send_message(chat_id=chat_id , text=f"""
        اهلا بيك حبي 👤 {user}
        Command ::
        ID : 🆔 /id
        Username : 👤 /user
        content : @pythonforbot1
        Help : /help

""")
    await context.bot.send_message(chat_id=chat_id , text="انا بوت ازالة الخلفية من الصور كل ما عليك ارسال لي الصورة التي تريد ازالة الخلفية منها ")
time.sleep(2)
async def id_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    await context.bot.send_message(chat_id=chat_id , text=f"The ID IS : {chat_id}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    username = update.message.from_user.first_name

    await context.bot.send_message(chat_id=chat_id , text=f"""
        اهلا بيك حبي 👤 {username}
        Command ::
        ID : 🆔 /id
        Username : 👤 /user
        content : @pythonforbot1
        Help : /help
        
""")
async def info_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    lastname = update.message.from_user.last_name

    await context.bot.send_message(chat_id=update.effective_chat.id , text=f"""
         Username 👤 @{username} 👤\n
         ---------------------------------
         First Name 📛 {first_name} 📛
         Last Name 📛 {lastname} 📛
         ID 🆔 {user_id} 🆔
""")

async def process_img(photo_name: str):
    name, _ = os.path.splitext(photo_name)
    output_photo_path = f"./processed/{name}.png"
    input_img = Image.open(f"./int/{photo_name}")
    output_img = remove(input_img)
    output_img.save(output_photo_path)
    os.remove(f"./int/{photo_name}")
    return output_photo_path
time.sleep(2)
async def handler_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if filters.PHOTO.check_update(update):
        file_id = update.message.photo[-1].file_id
        unique_file_id = update.message.photo[-1].file_unique_id
        photo_name = f"{unique_file_id}.jpg"
    elif filters.Document.check_update(update) and filters.Document.IMAGE.check_update(update):
        file_id = update.message.document.file_id
        _, f_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        photo_name = f"{unique_file_id}{f_ext}"
    else:
        context.bot.send_message(chat_id=update.effective_chat.id , text="ارسل الصورة المراد ازالة خلفيتها ! لا شيء اخر.")
    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive(custom_path=f"./int/{photo_name}")
    await context.bot.send_message(chat_id=update.effective_chat.id , text=".....يـتم ازالـة الخـلفيه")
    processed_img = await process_img(photo_name)
    await context.bot.send_document(chat_id=update.effective_chat.id , document=processed_img)
    os.remove(processed_img)
    os.remove(f"./int/{photo_name}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start" , start)
    id_users_handler = CommandHandler("id" , id_users)
    help_handler = CommandHandler("help" , help_command)
    info_user_handler = CommandHandler("info", info_user)
    message_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE,handler_message)

    app.add_handler(start_handler)
    app.add_handler(id_users_handler)
    app.add_handler(help_handler)
    app.add_handler(info_user_handler)
    app.add_handler(message_handler)

    app.run_polling()
