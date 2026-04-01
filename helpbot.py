import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Загружаем переменные из файла .env
load_dotenv()

# --- НАСТРОЙКИ (теперь из окружения) ---
SUPPORT_TOKEN = os.getenv("SUPPORT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Хранилище для связи
reply_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("🚀 **Режим Админа активирован.**")
    else:
        await update.message.reply_text("👋 **Служба поддержки Kryloxa Bot.**\nПишите сюда, и я отвечу!")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Если пишет ЮЗЕР
    if user.id != OWNER_ID:
        info_text = f"📩 **Новое обращение!**\n👤 От: {user.first_name}\n🆔 ID: `{user.id}`"
        await context.bot.send_message(chat_id=OWNER_ID, text=info_text, parse_mode="Markdown")
        
        forwarded_msg = await update.message.forward(chat_id=OWNER_ID)
        reply_map[forwarded_msg.message_id] = user.id
        await update.message.reply_text("✅ Доставлено создателю!")
    
    # Если пишет АДМИН (ответ на сообщение)
    else:
        if update.message.reply_to_message:
            orig_msg_id = update.message.reply_to_message.message_id
            target_user_id = reply_map.get(orig_msg_id)
            
            if target_user_id:
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id, 
                        text=f"📩 **Ответ от разработчика:**\n\n{update.message.text}",
                        parse_mode="Markdown"
                    )
                    await update.message.reply_text(f"✅ Ответ отправлен пользователю `{target_user_id}`")
                except Exception as e:
                    await update.message.reply_text(f"❌ Ошибка: {e}")
            else:
                await update.message.reply_text("❌ Ответьте именно на пересланное сообщение.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(SUPPORT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_message))
    
    print("Support Bot started with .env security...")
    app.run_polling()
