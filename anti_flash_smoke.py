import pymem
import time
import requests
import json

# URL to fetch latest offsets from CS2 dumper
URL = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/cs2.json"

def get_offsets():
    """Fetches the latest offsets from the CS2 dumper."""
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            offsets = response.json()["signatures"]
            netvars = response.json()["netvars"]
            return {
                "FLASHBANG_OPACITY": offsets["dwFlashbangOpacity"],  # Flashbang opacity address
                "SMOKE_OPACITY": offsets["dwSmokeOpacity"],  # Smoke opacity address
                "LOCAL_PLAYER": offsets["dwLocalPlayerPawn"],
                "HEALTH": netvars["m_iHealth"]
            }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching offsets: {e}")
    return None

def anti_flash_smoke():
    offsets = get_offsets()
    if not offsets:
        print("Failed to fetch offsets. Exiting...")
        return

    pm = pymem.Pymem("cs2.exe")  # Attach to CS2

    # Game loop to constantly monitor and adjust opacity
    while True:
        time.sleep(0.1)

        # Anti-Flash: Reduce opacity to 10%
        flashbang_opacity = pm.read_float(offsets["FLASHBANG_OPACITY"])
        if flashbang_opacity > 0.1:  # Flashbang effect is active
            pm.write_float(offsets["FLASHBANG_OPACITY"], 0.1)

        # Anti-Smoke: Reduce opacity to 30%
        smoke_opacity = pm.read_float(offsets["SMOKE_OPACITY"])
        if smoke_opacity > 0.3:  # Smoke effect is active
            pm.write_float(offsets["SMOKE_OPACITY"], 0.3)

if __name__ == "__main__":
    anti_flash_smoke()
