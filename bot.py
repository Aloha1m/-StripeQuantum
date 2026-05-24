from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import sqlite3

TOKEN = "8995499896:AAGh4t3QZRvg9HSeRfowsAnoZ_4hGK6k2do"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# DATABASE
db = sqlite3.connect("guardian.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS warns(
user_id INTEGER,
warns INTEGER
)
""")

db.commit()

# START COMMAND
@dp.message(Command("start"))
async def start(message: Message):

    text = """
⚡ <b>【IMU】 GUARDIAN</b> ⚡

🛡 Group Security: Active
🚫 Anti-Spam: Enabled
👮 Moderation: Online

Choose an option below 👇
"""

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📜 Rules")],
            [types.KeyboardButton(text="👤 Profile")],
            [types.KeyboardButton(text="🛡 Admin Panel")]
        ],
        resize_keyboard=True
    )

    await message.answer(text, reply_markup=keyboard)

# RULES
@dp.message(lambda message: message.text == "📜 Rules")
async def rules(message: Message):

    await message.answer(
        "📜 <b>Group Rules</b>\n\n"
        "• No spam\n"
        "• No links\n"
        "• Respect everyone\n"
        "• No abuse"
    )

# PROFILE
@dp.message(lambda message: message.text == "👤 Profile")
async def profile(message: Message):

    user = message.from_user

    await message.answer(
        f"👤 Name: {user.full_name}\n"
        f"🆔 ID: {user.id}"
    )

# WELCOME MESSAGE
@dp.message(lambda message: message.new_chat_members)
async def welcome(message: Message):

    for member in message.new_chat_members:
        await message.answer(
            f"👋 Welcome {member.full_name} to the group!"
        )

# ANTI LINK
@dp.message()
async def anti_link(message: Message):

    if not message.text:
        return

    text = message.text.lower()

    links = ["http", "https", "t.me", "www."]

    if any(link in text for link in links):

        try:
            await message.delete()

            await message.answer(
                f"🚫 {message.from_user.full_name}, links are not allowed!"
            )

        except:
            pass

# WARN COMMAND
@dp.message(Command("warn"))
async def warn_user(message: Message):

    admins = await bot.get_chat_administrators(message.chat.id)
    admin_ids = [admin.user.id for admin in admins]

    if message.from_user.id not in admin_ids:
        return

    if not message.reply_to_message:
        await message.answer("Reply to a user.")
        return

    target = message.reply_to_message.from_user.id

    cursor.execute(
        "SELECT warns FROM warns WHERE user_id=?",
        (target,)
    )

    data = cursor.fetchone()

    if data is None:
        warns = 1

        cursor.execute(
            "INSERT INTO warns VALUES(?,?)",
            (target, warns)
        )

    else:
        warns = data[0] + 1

        cursor.execute(
            "UPDATE warns SET warns=? WHERE user_id=?",
            (warns, target)
        )

    db.commit()

    await message.answer(
        f"⚠️ User warned.\nTotal warns: {warns}"
    )

    # AUTO MUTE
    if warns >= 3:

        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target,
            permissions=types.ChatPermissions(
                can_send_messages=False
            )
        )

        await message.answer(
            "🔇 User muted after 3 warns."
        )

# ADMIN PANEL
@dp.message(lambda message: message.text == "🛡 Admin Panel")
async def admin_panel(message: Message):

    admins = await bot.get_chat_administrators(message.chat.id)
    admin_ids = [admin.user.id for admin in admins]

    if message.from_user.id not in admin_ids:
        await message.answer("❌ Admin only")
        return

    await message.answer(
        "🛡 <b>Admin Panel</b>\n\n"
        "/warn → Warn user\n"
        "/ban → Ban user\n"
        "/mute → Mute user"
    )

# MAIN
async def main():
    print("Guardian Bot Running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())