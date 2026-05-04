# Carousel / UI Component Skill

Builds reusable carousel and data-display UI components.

## When to Use

- Building dashboard cards that display lists (balita, ibu hamil, reports)
- Creating Telegram bot carousel menus with inline keyboard
- Implementing paginated data views

## Dashboard — React Carousel

### Basic Carousel Component

```tsx
// components/ui/Carousel.tsx
import { useState } from "react"

interface CarouselProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => React.ReactNode
  keyExtractor: (item: T) => string
  autoPlay?: boolean
  interval?: number
}

export function Carousel<T>({ items, renderItem, keyExtractor, autoPlay, interval = 3000 }: CarouselProps<T>) {
  const [current, setCurrent] = useState(0)

  // Auto-advance
  useEffect(() => {
    if (!autoPlay) return
    const timer = setInterval(() => {
      setCurrent(c => (c + 1) % items.length)
    }, interval)
    return () => clearInterval(timer)
  }, [autoPlay, interval, items.length])

  return (
    <div className="relative overflow-hidden">
      <div
        className="flex transition-transform duration-300"
        style={{ transform: `translateX(-${current * 100}%)` }}
      >
        {items.map((item, i) => (
          <div key={keyExtractor(item)} className="w-full flex-shrink-0">
            {renderItem(item, i)}
          </div>
        ))}
      </div>
      {/* Dots */}
      <div className="absolute bottom-2 left-1/2 flex gap-1">
        {items.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            className={`w-2 h-2 rounded-full ${i === current ? "bg-blue-600" : "bg-gray-300"}`}
          />
        ))}
      </div>
    </div>
  )
}
```

### Usage with Data Cards

```tsx
<Carousel
  items={recentBalita}
  keyExtractor={(b) => b.id.toString()}
  renderItem={(balita) => (
    <BalitaCard balita={balita} />
  )}
/>
```

## Telegram Bot — Inline Keyboard Carousel

### Paginated Inline Keyboard

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ITEMS_PER_PAGE = 5

def build_pagination_keyboard(items: list, page: int, callback_prefix: str) -> InlineKeyboardMarkup:
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = items[start:end]

    keyboard = []
    for item in page_items:
        keyboard.append([
            InlineKeyboardButton(
                f"📋 {item.name}",
                callback_data=f"{callback_prefix}:view:{item.id}"
            )
        ])

    # Pagination row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"{callback_prefix}:page:{page-1}"))
    if end < len(items):
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"{callback_prefix}:page:{page+1}"))
    if nav:
        keyboard.append(nav)

    return InlineKeyboardMarkup(keyboard)
```

### Usage in Handler

```python
async def list_balita(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balita_list = await db.get_all_balita()
    keyboard = build_pagination_keyboard(balita_list, page=0, callback_prefix="balita")
    await update.message.reply_text(
        f"📋 Daftar Balita ({len(balita_list)} total):",
        reply_markup=keyboard
    )

async def paginate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, _, page_str = query.data.split(":")
    page = int(page_str)

    balita_list = await db.get_all_balita()
    keyboard = build_pagination_keyboard(balita_list, page=page, callback_prefix="balita")
    await query.edit_message_reply_markup(reply_markup=keyboard)
```
