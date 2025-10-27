import os, time, requests, json

# === Configuration à partir des variables d'environnement (Render ou GitHub) ===
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
VR_USER_ID = os.getenv("VR_USER_ID", "68fcf81bdf09637be676c640")
VR_RACE_ID = int(os.getenv("VR_RACE_ID", "777"))
VR_LEG_NUM = int(os.getenv("VR_LEG_NUM", "2"))
INTERVAL = int(os.getenv("INTERVAL", "3600"))  # secondes (3600 = 1h)

VR_ENDPOINT = "https://vro-api-client.prod.virtualregatta.com/getboatinfos"
VR_HEADERS = {
    "content-type": "application/json",
    "x-api-key": "qUuxI3LGfRVCgkTi7D3s/4Zpfty99sLRoOxZ1rA/C7g=",
    "x-platform": "WebGLPlayer",
    "x-playerid": VR_USER_ID,
    "x-version": "7.1.5",
    "origin": "https://play.offshore.virtualregatta.com",
    "referer": "https://play.offshore.virtualregatta.com/"
}
VR_PAYLOAD = {
    "user_id": VR_USER_ID,
    "race_id": VR_RACE_ID,
    "leg_num": VR_LEG_NUM,
    "infos": "track,engine",
    "country": "FR"
}

def get_boat_info():
    """Appel de l'API VR"""
    r = requests.post(VR_ENDPOINT, headers=VR_HEADERS, json=VR_PAYLOAD, timeout=25)
    r.raise_for_status()
    return r.json()

def fmt(v, unit=""):
    return f"{v}{unit}" if v not in (None, "", "N/A") else "N/A"

def build_message(data):
    """Construit un message texte simple"""
    d = {}
    for key in ("boat","player","me","self","data"):
        if isinstance(data.get(key), dict):
            d = data[key]
            break
    lat = d.get("lat") or d.get("latitude")
    lon = d.get("lon") or d.get("longitude")
    sog = d.get("sog") or d.get("speed")
    hdg = d.get("hdg") or d.get("heading")
    rank = d.get("rank") or d.get("position")
    wind = d.get("tws") or d.get("windSpeed")
    twa = d.get("twa") or d.get("windAngle")

    return (
        "⛵ **Coyote Seal – Live Update**\n"
        f"📍 Position : {fmt(lat)} / {fmt(lon)}\n"
        f"🧭 Cap : {fmt(hdg,'°')}   💨 Vitesse : {fmt(sog,' kts')}\n"
        f"🌬️ Vent : {fmt(wind,' kts')}  TWA : {fmt(twa,'°')}\n"
        f"🏁 Classement : {fmt(rank)}"
    )

def post_discord(text):
    """Envoi vers Discord"""
    r = requests.post(DISCORD_WEBHOOK, json={"content": text}, timeout=15)
    if not r.ok:
        print("Erreur Discord:", r.status_code, r.text)

def main():
    print("🚀 Bot VR → Discord démarré")
    print("  - Envoi vers :", DISCORD_WEBHOOK)
    print("  - Intervalle :", INTERVAL, "sec")
    while True:
        try:
            data = get_boat_info()
            msg = build_message(data)
            post_discord(msg)
            print("✅ Envoi effectué :", time.ctime())
        except Exception as e:
            print("❌ Erreur:", e)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
