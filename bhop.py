import pymem
import win32api
import time

# Offsets (CHECK CS2 Dumper for latest ones (https://github.com/a2x/cs2-dumper/blob/main/output/offsets.cs))
LOCAL_PLAYER = 0x1910F28  # dwLocalPlayerPawn
FORCE_JUMP = 0x1A5FA80    # dwForceJump
FLAGS = 0x3E4            # m_fFlags
HEALTH = 0x32C           # m_iHealth

def bhop():
    pm = pymem.Pymem('cs2.exe')  # Attach to CS2
    
    # Get the client module
    client = None
    for module in list(pm.list_modules()):
        if module.name == 'client.dll':
            client = module.lpBaseOfDll
            break  # stop once found

    if not client:
        print("Failed to find client.dll")
        return
    
    print(f"Client.dll base address: {hex(client)}")
    
    # loop       
    while True:
        time.sleep(0.01)

        # if spacebar is pressed
        if not win32api.GetAsyncKeyState(0x20):
            continue

        local_player = pm.read_int(client + LOCAL_PLAYER)
        if not local_player:
            continue

        # is alive
        if pm.read_int(local_player + HEALTH) <= 0:
            continue

        # is on groud
        if pm.read_uint(local_player + FLAGS) & 1:
            pm.write_uint(client + FORCE_JUMP, 6)
            time.sleep(0.01)
            pm.write_uint(client + FORCE_JUMP, 4)

if __name__ == '__main__':
    bhop()
