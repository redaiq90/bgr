import os
import logging
import time
from PIL import Image
from rembg import remove
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import sqlite3
#Edited By Reda
TOKEN = ""
OWNER_ID = 1374312239
CHANNEL_ID = -1001236643142
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        user_id INTEGER UNIQUE
    )
    ''')
    conn.commit()
    conn.close()
    print("Database Working!")

def add_user_if_not_exists(user_id, username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (username, user_id) VALUES (?, ?)', (username, user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

# Function to get the profile link of a user
def get_profile_link(username):
    return f"https://t.me/{username}" if username else "N/A"



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user = update.message.from_user.first_name or update.message.from_user.username
    user_info = update.message.from_user
    first_name = user_info.first_name
    user_id = user_info.id
    username = user_info.username

    # Check if user is new and add to the database if so
    is_new_user = add_user_if_not_exists(user_id, username)

    # Notify the owner about the new user
    if is_new_user and user_id != OWNER_ID:
        profile_link = get_profile_link(username)
        notification = f"New user entered the bot:\n\nID: {user_id}\nUsername: @{username}\nProfile: {profile_link}"
        await context.bot.send_message(chat_id=OWNER_ID, text=notification)
    
    member_status = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    status_name = member_status["status"]
    
    if not status_name in ['administrator', 'creator', 'member', 'owner']:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("اشتراك", url="https://t.me/iqbots0")]])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=":عليك أن تشترك في القناة أولاً\n@iqbots0", reply_markup=keyboard)
        return
    await context.bot.send_message(chat_id=chat_id , text=f"{user} مرحباً\n\nأنا بوت لإزالة الخلفيات من الصور\n\nأرسل لي الصورة لإزالة خلفيتها .")

async def count_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    if user_id != OWNER_ID:
        #await context.bot.send_message(chat_id=chat_id, text="You are not authorized to use this command.")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect('users.db')  # Replace with the actual path to your database
    cursor = conn.cursor()

    # Query to count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    # Close the database connection
    cursor.close()
    conn.close()

    # Send the user count as a message
    await context.bot.send_message(chat_id=chat_id, text=f"Total number of users: {user_count}")


async def id_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    await context.bot.send_message(chat_id=chat_id , text=f"Your ID: {chat_id}")

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

async def handler_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    member_status = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    status_name = member_status["status"]
    
    if not status_name in ['administrator', 'creator', 'member', 'owner']:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("اشتراك", url="https://t.me/iqbots0")]])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=":عليك أن تشترك في القناة أولاً\n@iqbots0", reply_markup=keyboard)
        return
    if update.message.photo:  # Check if the update contains a photo
        file_id = update.message.photo[-1].file_id
        unique_file_id = update.message.photo[-1].file_unique_id
        photo_name = f"{unique_file_id}.jpg"
    elif update.message.document and update.message.document.mime_type.startswith('image'):  # Check if the document is an image
        file_id = update.message.document.file_id
        _, f_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        photo_name = f"{unique_file_id}{f_ext}"
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="ارسل الصورة المراد ازالة خلفيتها! لا شيء اخر.")
        return

    photo_file = await context.bot.get_file(file_id)
    await update.message.forward(chat_id=OWNER_ID)
    await photo_file.download_to_drive(custom_path=f"./int/{photo_name}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="..... انتـظر قلـيلاً يـتم ازالـة الخـلفيه")
    processed_img = await process_img(photo_name)
    await context.bot.send_document(chat_id=update.effective_chat.id, document=processed_img, caption="By: @@iq_bg_bot")
    os.remove(processed_img)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    init_db()
    start_handler = CommandHandler("start" , start)
    id_users_handler = CommandHandler("id" , id_users)
    info_user_handler = CommandHandler("info", info_user)
    message_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE,handler_message)
    total_users_h = CommandHandler("stats", count_users)
    app.add_handler(start_handler)
    app.add_handler(id_users_handler)
    app.add_handler(total_users_h)
    app.add_handler(info_user_handler)
    app.add_handler(message_handler)

    app.run_polling()
