import pymem
import win32api
import time
import requests
import json

# URL to fetch latest offsets from CS2 dumper
URL = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/cs2.json"

def get_offsets():
    """Fetches the latest offsets from the CS2 dumper."""
    response = requests.get(URL)
    if response.status_code == 200:
        offsets = json.loads(response.text)["signatures"]
        netvars = json.loads(response.text)["netvars"]
        return {
            "LOCAL_PLAYER": offsets["dwLocalPlayerPawn"],
            "FORCE_JUMP": offsets["dwForceJump"],
            "FLAGS": netvars["m_fFlags"],
            "HEALTH": netvars["m_iHealth"]
        }
    else:
        print("Failed to fetch offsets. Check your internet connection.")
        return None

def bhop():
    offsets = get_offsets()
    if not offsets:
        return  # Stop if offsets couldn't be retrieved

    pm = pymem.Pymem('cs2.exe')  # Attach to CS2

    # Get the client module
    client = None
    for module in list(pm.list_modules()):
        if module.name == 'client.dll':
            client = module.lpBaseOfDll
            break  # Stop once found

    if not client:
        print("Failed to find client.dll")
        return
    
    print(f"Client.dll base address: {hex(client)}")
    
    # Game loop       
    while True:
        time.sleep(0.01)

        # If spacebar is pressed
        if not win32api.GetAsyncKeyState(0x20):
            continue

        local_player = pm.read_int(client + offsets["LOCAL_PLAYER"])
        if not local_player:
            continue

        # Is alive
        if pm.read_int(local_player + offsets["HEALTH"]) <= 0:
            continue

        # Is on ground
        if pm.read_uint(local_player + offsets["FLAGS"]) & 1:
            pm.write_uint(client + offsets["FORCE_JUMP"], 6)
            time.sleep(0.01)
            pm.write_uint(client + offsets["FORCE_JUMP"], 4)

if __name__ == '__main__':
    bhop()
