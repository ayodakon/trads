import requests

# Ganti dengan token kamu
TOKEN = "8039080652:AAHo4kc5WAGavNRKNnsYM3PsNy9wCorXGCM"  # Ganti!

response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
data = response.json()

if data.get('ok'):
    if data['result']:
        for update in data['result']:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                first_name = update['message']['chat'].get('first_name', 'User')
                print(f"✅ Chat ID ditemukan!")
                print(f"   Nama: {first_name}")
                print(f"   Chat ID: {chat_id}")
                break
    else:
        print("❌ Tidak ada pesan di bot.")
        print("   Pastikan kamu sudah kirim /start ke bot")
else:
    print("❌ Error:", data.get('description', 'Unknown error'))
