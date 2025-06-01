import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "7755961632:AAG9da0P1aL2pe5FeuYmxHYH39ZE435m76Y"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

regions = [
    "Toshkent", "Samarqand", "Farg'ona", "Andijon", "Namangan", "Buxoro",
    "Navoiy", "Xorazm", "Qashqadaryo", "Surxondaryo", "Jizzax", "Sirdaryo"
]

# Viloyatlar tugmasi
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

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.delete()
    await message.answer("🕌 Viloyatingizni tanlang:", reply_markup=region_keyboard())

@dp.callback_query(F.data.in_(regions))
async def send_prayer_times(callback: types.CallbackQuery):
    await callback.message.delete()
    region = callback.data
    await callback.answer()

    url = f"http://api.aladhan.com/v1/timingsByCity?city={region}&country=Uzbekistan&method=2"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        timings = data["data"]["timings"]
        date = data["data"]["date"]["readable"]

        text = (
            f"🕌 {region} viloyati uchun bugungi namoz vaqtlari:\n"
            f"📅 Sana: <b>{date}</b>\n\n"
            f"🌙 Bomdod: {timings['Fajr']}\n"
            f"🌅 Quyosh: {timings['Sunrise']}\n"
            f"🏙 Peshin: {timings['Dhuhr']}\n"
            f"🌇 Asr: {timings['Asr']}\n"
            f"🌆 Shom: {timings['Maghrib']}\n"
            f"🌃 Xufton: {timings['Isha']}"
        )
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=back_keyboard())

    except Exception as e:
        await callback.message.answer("⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring.")
        print(f"Xato: {e}")

# "Orqaga" tugmasi bosilganda
@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer("⬅️ Yana viloyatni tanlang:", reply_markup=region_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
