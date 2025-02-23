import pymem
import time
import requests
import json
import win32api
import threading

# URL to fetch latest offsets from CS2 dumper
URL = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/cs2.json"

def get_offsets():
    """Fetches the latest offsets from the CS2 dumper."""
    response = requests.get(URL)
    if response.status_code == 200:
        offsets = json.loads(response.text)["signatures"]
        netvars = json.loads(response.text)["netvars"]
        return {
            "dwEntityList": offsets["dwEntityList"],
            "dwLocalPlayerPawn": offsets["dwLocalPlayerPawn"],
            "dwGlowObjectManager": offsets["dwGlowObjectManager"],
            "m_iTeamNum": netvars["m_iTeamNum"],
            "m_iGlowIndex": netvars["m_iGlowIndex"]
        }
    else:
        print("Failed to fetch offsets. Check your internet connection.")
        return None

# Global variable to control whether the ESP is active or not
glow_enabled = True

def glow_esp():
    offsets = get_offsets()
    if not offsets:
        return  # Stop if offsets couldn't be retrieved

    pm = pymem.Pymem("cs2.exe")

    # Find client.dll base
    client = None
    for module in pm.list_modules():
        if module.name == "client.dll":
            client = module.lpBaseOfDll
            break

    if not client:
        print("Failed to find client.dll")
        return

    print(f"Client.dll base address: {hex(client)}")

    while True:
        time.sleep(0.01)

        if not glow_enabled:
            continue  # Skip if ESP is disabled

        # Get local player
        local_player = pm.read_int(client + offsets["dwLocalPlayerPawn"])
        if not local_player:
            continue

        # Get local player team
        local_team = pm.read_int(local_player + offsets["m_iTeamNum"])

        # Get glow object manager
        glow_manager = pm.read_int(client + offsets["dwGlowObjectManager"])

        # Loop through all entities
        for i in range(1, 64):  # Max players
            entity = pm.read_int(client + offsets["dwEntityList"] + i * 0x8)
            if not entity:
                continue

            # Get team number
            entity_team = pm.read_int(entity + offsets["m_iTeamNum"])

            # Only glow enemies
            if entity_team == local_team:
                continue

            # Get Glow Index
            glow_index = pm.read_int(entity + offsets["m_iGlowIndex"])

            # Apply glow color (#fc3030)
            pm.write_float(glow_manager + (glow_index * 0x40) + 0x8, 0.988)  # Red
            pm.write_float(glow_manager + (glow_index * 0x40) + 0xC, 0.188)  # Green
            pm.write_float(glow_manager + (glow_index * 0x40) + 0x10, 0.188) # Blue
            pm.write_float(glow_manager + (glow_index * 0x40) + 0x14, 1.0)   # Alpha (full opacity)
            pm.write_int(glow_manager + (glow_index * 0x40) + 0x2C, 1)  # Render when occluded

def toggle_glow():
    global glow_enabled
    while True:
        if win32api.GetAsyncKeyState(0x78):  # F9 key (0x78 is the virtual key for F9)
            glow_enabled = not glow_enabled  # Toggle the ESP state
            print("Glow ESP enabled" if glow_enabled else "Glow ESP disabled")
            time.sleep(0.5)  # To prevent multiple toggles in a short time

if __name__ == "__main__":
    threading.Thread(target=toggle_glow, daemon=True).start()  # Start the toggle thread
    glow_esp()
