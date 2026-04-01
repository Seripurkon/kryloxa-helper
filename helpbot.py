import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# --- НАСТРОЙКИ (Вписываешь один раз и забываешь) ---
SUPPORT_TOKEN = "8548759774:AAGynBbPfNS58sE-HJf-TEZ4HNw50fQMZBw"
OWNER_ID = 5679520675

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Словарь для связи: ID сообщения в твоей личке -> ID юзера, который написал боту
reply_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("🚀 **Kryloxa Support: Режим Админа.**\nЖдем сообщений от пользователей.")
    else:
        await update.message.reply_text("👋 **Служба поддержки Kryloxa Bot.**\nНапишите ваш вопрос или баг, и создатель ответит вам прямо здесь!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # 1. Если пишет ПОЛЬЗОВАТЕЛЬ (не ты)
    if user.id != OWNER_ID:
        # Информируем тебя, кто пишет
        info_text = f"📩 **Новое обращение!**\n👤 От: {user.first_name} (@{user.username})\n🆔 ID: `{user.id}`\n\n⬇️ Сообщение:"
        await context.bot.send_message(chat_id=OWNER_ID, text=info_text, parse_mode="Markdown")
        
        # Пересылаем тебе само сообщение
        forwarded_msg = await update.message.forward(chat_id=OWNER_ID)
        
        # Запоминаем, что на это сообщение нужно отвечать этому юзеру
        reply_map[forwarded_msg.message_id] = user.id
        
        await update.message.reply_text("✅ Отправлено создателю. Ожидайте ответа!")

    # 2. Если пишешь ТЫ (ответ на сообщение)
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
                    await update.message.reply_text(f"✅ Ответ доставлен пользователю `{target_user_id}`")
                except Exception as e:
                    await update.message.reply_text(f"❌ Ошибка отправки: {e}")
            else:
                await update.message.reply_text("❌ Ошибка: Я не помню, кто это прислал. Попробуй ответить на более свежее сообщение.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(SUPPORT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # Ловим все текстовые сообщения в приватных чатах
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    
    print("Support Bot (Direct Token) is running...")
    app.run_polling()
