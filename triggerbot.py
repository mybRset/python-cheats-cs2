import pymem
import win32api
import time
import requests
import win32con

# URL to fetch latest offsets from CS2 dumper
def get_offsets():
    url = "https://your-source-for-offsets.com/offsets.json"  # Replace with actual source
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Assume it returns a JSON with the offsets
    except requests.exceptions.RequestException as e:
        print(f"Error fetching offsets: {e}")
    return None

def triggerbot():
    offsets = get_offsets()
    if not offsets:
        print("Failed to fetch offsets. Exiting...")
        return

    dwEntityList = offsets['dwEntityList']
    dwLocalPlayerPawn = offsets['dwLocalPlayerPawn']
    m_iCrosshairId = offsets['m_iCrosshairId']
    m_iTeamNum = offsets['m_iTeamNum']

    pm = pymem.Pymem("cs2.exe")
    
    # Find client.dll base address
    client = None
    for module in pm.list_modules():
        if module.name == "client.dll":
            client = module.lpBaseOfDll
            break

    if not client:
        print("Failed to find client.dll")
        return

    print(f"Client.dll base address: {hex(client)}")

    triggerbot_enabled = True  # Triggerbot is enabled by default

    while True:
        time.sleep(0.01)

        # Check for F9 key to toggle triggerbot
        if win32api.GetAsyncKeyState(win32con.VK_F9) & 0x8000:
            triggerbot_enabled = not triggerbot_enabled
            print(f"Triggerbot {'Enabled' if triggerbot_enabled else 'Disabled'}")

        # Only activate triggerbot while right mouse button is held down
        if triggerbot_enabled and win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000:
            # Get local player entity
            local_player = pm.read_int(client + dwLocalPlayerPawn)
            if not local_player:
                continue

            # Get crosshair ID (target under crosshair)
            crosshair_id = pm.read_int(local_player + m_iCrosshairId)

            if crosshair_id <= 0 or crosshair_id > 64:
                continue

            # Get the entity under the crosshair
            entity = pm.read_int(client + dwEntityList + crosshair_id * 0x8)
            if not entity:
                continue

            # Get the team number of the enemy entity
            entity_team = pm.read_int(entity + m_iTeamNum)

            # Get the local player's team
            local_team = pm.read_int(local_player + m_iTeamNum)

            # If the entity is not on the same team (enemy)
            if entity_team != local_team:
                # Simulate mouse click to shoot
                win32api.mouse_event(0x02, 0, 0, 0, 0)  # Left mouse down
                win32api.mouse_event(0x04, 0, 0, 0, 0)  # Left mouse up

if __name__ == "__main__":
    triggerbot()
