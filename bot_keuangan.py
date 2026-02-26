from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
import json

TOKEN = os.getenv("8327665650:AAEbWNtT6nL7FoIbiZVt-ZXqhzN2Wo8Z81I")
OWNER_ID = int(os.getenv("OWNER_ID"))
SPREADSHEET_NAME = "KeuanganBot"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

google_credentials = os.getenv("GOOGLE_CREDENTIALS")

if not google_credentials:
    raise ValueError("GOOGLE_CREDENTIALS belum diset!")

creds_dict = json.loads(google_credentials)
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)


# ========================
# SIMPAN DATA
# ========================
def simpan_data(jenis, nominal, ket):
    tanggal = datetime.now().strftime("%d-%m-%Y %H:%M")

    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1

    sheet.append_row([tanggal, jenis.capitalize(), nominal, ket])


# ========================
# HITUNG SALDO
# ========================
def hitung_saldo():
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1

    data = sheet.get_all_values()

    total_masuk = 0
    total_keluar = 0

    for row in data[1:]:
        if len(row) < 3:
            continue

        jenis = row[1].lower()
        nominal = int(row[2])

        if jenis == "masuk":
            total_masuk += nominal
        elif jenis == "keluar":
            total_keluar += nominal

    return total_masuk - total_keluar


# ========================
# HANDLE TRANSAKSI
# ========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    text = update.message.text.lower()
    parts = text.split()

    if len(parts) < 3:
        return

    jenis = parts[0]
    nominal = parts[1]
    ket = " ".join(parts[2:])

    if jenis not in ["masuk", "keluar"]:
        return

    if not nominal.isdigit():
        await update.message.reply_text("Nominal harus angka!")
        return

    simpan_data(jenis, int(nominal), ket)

    await update.message.reply_text("✅ Transaksi dicatat!")


# ========================
# COMMAND SALDO
# ========================
async def cek_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    saldo = hitung_saldo()

    await update.message.reply_text(
        f"💰 Saldo kamu sekarang:\nRp {saldo:,}"
    )


# ========================
# MAIN
# ========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CommandHandler("saldo", cek_saldo))

print("Bot aktif (Google Sheets)...")

app.run_polling()