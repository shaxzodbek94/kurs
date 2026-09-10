# Tanishuv Chat Bot (Telegram)

Anonim tanishuv/chat Telegram boti. Foydalanuvchilar ro'yxatdan o'tib,
tasodifiy suhbatdosh topishadi va matn, rasm hamda video almashishadi.
Botda taqiqlangan so'zlar filtri, foydalanuvchilarni bloklash va to'liq
admin panel mavjud.

## Imkoniyatlar

- **Ro'yxatdan o'tish**: ism, yosh, jins va (ixtiyoriy) profil rasmi.
- **Tasodifiy suhbatdosh qidirish**: navbat asosida ikkita foydalanuvchini
  bog'lash (anonim chat).
- **Xabar almashish**: matn, rasm va video xabarlar suhbatdoshga uzatiladi.
- **Taqiqlangan so'zlar filtri**: taqiqlangan so'z ishlatilgan xabar
  suhbatdoshga yuborilmaydi, foydalanuvchi ogohlantiriladi; belgilangan
  sonda (standart 5 marta) qoidabuzarlikdan so'ng foydalanuvchi avtomatik
  bloklanadi.
- **Foydalanuvchilarni bloklash**: suhbatdosh istalgan vaqtda bloklanishi
  mumkin — bloklangan foydalanuvchilar qayta bog'lanmaydi.
- **Moderatsiya**: foydalanuvchilar bir-biriga yuborgan barcha rasm va
  videolar nusxasi avtomatik ravishda administratorlarga yuboriladi.
- **Admin panel** (`/admin`):
  - 📊 Statistika (foydalanuvchilar, faol suhbatlar, bloklanganlar soni)
  - 📢 Barcha foydalanuvchilarga xabar yuborish (broadcast)
  - 🔠 Taqiqlangan so'zlarni qo'shish / o'chirish / ko'rish
  - 🚫 Foydalanuvchini ID orqali bloklash / blokdan chiqarish
  - 📃 Bloklangan foydalanuvchilar ro'yxati

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylini to'ldiring:

```
BOT_TOKEN=<@BotFather bergan token>
ADMIN_IDS=<admin telegram ID lari, vergul bilan ajratilgan>
DATABASE_URL=sqlite+aiosqlite:///bot.db
MAX_VIOLATIONS=5
```

## Ishga tushirish

```bash
python bot.py
```

Ma'lumotlar bazasi (SQLite) birinchi ishga tushirishda avtomatik yaratiladi.

## Loyiha tuzilishi

```
bot.py                  # kirish nuqtasi
config.py                # .env sozlamalari
database/
  models.py               # SQLAlchemy modellari
  engine.py                # DB ulanish/init
  crud.py                   # DB bilan ishlash funksiyalari
handlers/
  user/                      # ro'yxatdan o'tish, qidiruv, chat, profil
  admin/                      # admin panel, broadcast, taqiqlangan so'zlar
keyboards/                 # reply/inline klaviaturalar
middlewares/                # bloklangan foydalanuvchilarni cheklash
states/                       # FSM holatlar
filters/                       # admin filtri
```
