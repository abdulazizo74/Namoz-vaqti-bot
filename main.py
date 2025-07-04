import asyncio
import logging
import aiohttp
import traceback
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "YOUR_BOT_TOKEN"  # ← bu yerga tokeningizni yozing

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Foydalanuvchiga ko‘rinadigan viloyatlar nomi
regions = [
    "Toshkent", "Samarqand", "Farg'ona", "Andijon", "Namangan", "Buxoro",
    "Navoiy", "Xorazm", "Qashqadaryo", "Surxondaryo", "Jizzax", "Sirdaryo"
]

# API bilan ishlaydigan shahar nomlari mosligi
region_api_map = {
    "Toshkent": "Tashkent",
    "Samarqand": "Samarkand",
    "Farg'ona": "Fergana",
    "Andijon": "Andijan",
    "Namangan": "Namangan",
    "Buxoro": "Bukhara",
    "Navoiy": "Navoi",
    "Xorazm": "Khiva",
    "Qashqadaryo": "Qarshi",
    "Surxondaryo": "Termiz",
    "Jizzax": "Jizzakh",
    "Sirdaryo": "Guliston"
}


# Viloyat tanlash tugmalari
def region_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=region, callback_data=region)] for region in regions
        ]
    )


# Orqaga tugmasi
def back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")]
        ]
    )


# /start buyrug'i
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("🕌 Viloyatingizni tanlang:", reply_markup=region_keyboard())


# Viloyat tanlanganda
@dp.callback_query(F.data.in_(regions))
async def send_prayer_times(callback: types.CallbackQuery):
    region = callback.data
    await callback.answer()

    api_region = region_api_map.get(region, region)  # APIga mos nom
    url = f"https://api.aladhan.com/v1/timingsByCity?city={api_region}&country=Uzbekistan&method=2"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await callback.message.answer("⚠️ API bilan bog‘lanib bo‘lmadi.")
                    print("Status:", resp.status)
                    print(await resp.text())
                    return

                data = await resp.json()

        timings = data["data"]["timings"]
        date = data["data"]["date"]["readable"]

        text = (
            f"🕌 <b>{region}</b> viloyati uchun bugungi namoz vaqtlari:\n"
            f"📅 Sana: <b>{date}</b>\n\n"
            f"🌙 Bomdod: {timings['Fajr']}\n"
            f"🌅 Quyosh: {timings['Sunrise']}\n"
            f"🏙 Peshin: {timings['Dhuhr']}\n"
            f"🌇 Asr: {timings['Asr']}\n"
            f"🌆 Shom: {timings['Maghrib']}\n"
            f"🌃 Xufton: {timings['Isha']}"
        )
        await callback.message.edit_text(text, reply_markup=back_keyboard(), parse_mode="HTML")

    except Exception:
        await callback.message.answer("⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring.")
        print("Xato:", traceback.format_exc())


# Orqaga tugmasi
@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("⬅️ Yana viloyatni tanlang:", reply_markup=region_keyboard())


# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
