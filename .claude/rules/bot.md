# Bot Rules — Telegram Bot

Loads automatically when working in `bot/**` paths.

## Handler Patterns

### Basic Message Handler

```python
from telegram import Update
from telegram.ext import ContextTypes

async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello!")
```

### Always Handle Errors

```python
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling {update}: {context.error}")
    if update and update.message:
        await update.message.reply_text("Terjadi kesalahan. Silakan coba lagi.")

app.add_error_handler(error_handler)
```

### Callback Query Handler

```python
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Always answer callback queries!
    # Acknowledge immediately, then process
    _, action, item_id = query.data.split(":", 2)
    await process_action(action, item_id)
```

## State Management

### Simple State (user_data)

```python
context.user_data["state"] = "awaiting_photo"
context.user_data["pending_report"] = {"category": "SAMPAH_TERBANG"}
```

### Conversation Handler Pattern

```python
from telegram.ext import ConversationHandler

async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nama balita?")
    return NAME

async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Tanggal lahir (YYYY-MM-DD)?")
    return DOB

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dibatalkan.")
    return ConversationHandler.END

conv = ConversationHandler(
    entry_points=[CommandHandler("register", entry)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)],
        DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, dob_received)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
```

## Message Sending

### Formatting

```python
# Use HTML formatting for cleaner messages
await update.message.reply_text(
    "<b> Nama:</b> {balita.nama}\n"
    "<b> Berat:</b> {balita.berat_kg} kg\n"
    "<b> Status:</b> {status_emoji}",
    parse_mode="HTML",
)
```

### Reply vs Direct Message

- Use `update.message.reply_text()` to reply in the same chat
- Use `context.bot.send_message(chat_id=admin_id, ...)` to DM admins

## Keyboard Patterns

### Inline Keyboard

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [
    [
        InlineKeyboardButton("✅ Ya", callback_data="confirm:yes"),
        InlineKeyboardButton("❌ Tidak", callback_data="confirm:no"),
    ]
]
await update.message.reply_text("Lanjutkan?", reply_markup=InlineKeyboardMarkup(keyboard))
```

### Location Keyboard

```python
from telegram import ReplyKeyboardMarkup, KeyboardButton

keyboard = [[KeyboardButton("📍 Kirim Lokasi", request_location=True)]]
await update.message.reply_text(
    "Kirim lokasi anda:",
    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
)
```

## Best Practices

1. **Always `await query.answer()`** on callback queries — or the bot shows a loading spinner forever
2. **Handle photos with `update.message.photo[-1]`** — gets the largest photo
3. **Download files before processing** — `await file.download_to_drive()`
4. **Don't block the main loop** — use `asyncio` for long operations
5. **Log errors with context** — `logger.error(f"Error: {context.error}")`
6. **Use conversation timeouts** — prevent stuck conversations

## Testing

```python
# Test a handler in isolation
async def test_handler():
    update = MockUpdate()
    context = ContextTypes.DEFAULT_TYPE()
    await my_handler(update, context)
    assert update.message.reply_text.called
```
