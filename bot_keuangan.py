from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import asyncio

TOKEN = "8327665650:AAEbWNtT6nL7FoIbiZVt-ZXqhzN2Wo8Z81I"
OWNER_ID = 8178584693
SPREADSHEET_NAME = "KeuanganBot"
JSON_FILE = "bot-keuangan-488317-2ff869c45041.json"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(JSON_FILE, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1


def simpan_data(jenis, nominal, ket):
    tanggal = datetime.now().strftime("%d-%m-%Y %H:%M")
    sheet.append_row([tanggal, jenis, nominal, ket])


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Bot ini private.")
        return

    text = update.message.text.strip()
    parts = text.split()

    if len(parts) < 3:
        await update.message.reply_text("Format salah")
        return

    jenis = parts[0].lower()
    nominal = parts[1]

    if not nominal.isdigit():
        await update.message.reply_text("Nominal harus angka")
        return

    ket = " ".join(parts[2:])

    if jenis == "masuk":
        simpan_data("Masuk", int(nominal), ket)
        await update.message.reply_text("Pemasukan dicatat")

    elif jenis == "keluar":
        simpan_data("Keluar", int(nominal), ket)
        await update.message.reply_text("Pengeluaran dicatat")

    else:
        await update.message.reply_text("Gunakan: masuk atau keluar")


async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot aktif (Google Sheets)...")
    await app.run_polling()


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot aktif (Google Sheets)...")
    app.run_polling()