import pymem
import time
import requests
import json

# URL to fetch the latest offsets from CS2 dumper
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
            "m_iInventory": netvars["m_iInventory"],  # Inventory offset
            "m_iItemDefinitionIndex": netvars["m_iItemDefinitionIndex"],  # Weapon skin ID offset
        }
    else:
        print("Failed to fetch offsets. Check your internet connection.")
        return None

def change_to_custom_skins():
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

    # Skin IDs for the requested skins
    skin_ids = {
        "t_side_knives": {
            "Butterfly Blue Steel": 3875,  # Example ID, replace with actual
            "Karambit Fade": 5002,  # Example ID, replace with actual
        },
        "ct_side_knives": {
            "Karambit Fade": 5002,  # Example ID, replace with actual
            "Butterfly Blue Steel": 3875,  # Example ID, replace with actual
        },
        "weapons": {
            "Blaze Desert Eagle": 5080,  # Example ID
            "Whiteout USP-S": 5100,  # Example ID
            "AK-47 Inheritance": 5140,  # Example ID
            "AUG Wings": 5150,  # Example ID
            "Galil AR Tuxedo": 5200,  # Example ID
            "M4A4 Decimator": 5220,  # Example ID
            "AWP Gungnir": 5230,  # Example ID
            "Sport Gloves Noctis": 5300,  # Example ID
        }
    }

    while True:
        time.sleep(0.1)

        # Get local player
        local_player = pm.read_int(client + offsets["dwLocalPlayerPawn"])
        if not local_player:
            continue

        # Read player's inventory
        inventory = pm.read_int(local_player + offsets["m_iInventory"])

        # Loop through inventory to change weapon skins
        for i in range(0, 40):  # Example loop for a max of 40 items
            item = pm.read_int(inventory + i * 0x4)  # Assuming 4-byte item slot
            if not item:
                continue

            # Change T-side and CT-side knife skins
            knife_skin_id = pm.read_int(item + offsets["m_iItemDefinitionIndex"])
            if knife_skin_id == 500:  # Default T-side knife (e.g., Butterfly)
                # Set the T-side knife skin to Butterfly Blue Steel (example ID)
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["t_side_knives"]["Butterfly Blue Steel"])
                print("Changed T-side knife to Butterfly Blue Steel")
            
            elif knife_skin_id == 5001:  # Default CT-side knife (e.g., Karambit)
                # Set the CT-side knife skin to Karambit Fade (example ID)
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["ct_side_knives"]["Karambit Fade"])
                print("Changed CT-side knife to Karambit Fade")

            # Change other weapons skins
            weapon_skin_id = pm.read_int(item + offsets["m_iItemDefinitionIndex"])
            if weapon_skin_id == 1:  # Example: default Desert Eagle
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["Blaze Desert Eagle"])
                print("Changed Desert Eagle to Blaze skin")
            elif weapon_skin_id == 7:  # Example: default USP-S
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["Whiteout USP-S"])
                print("Changed USP-S to Whiteout skin")
            elif weapon_skin_id == 9:  # Example: default AK-47
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["AK-47 Inheritance"])
                print("Changed AK-47 to Inheritance skin")
            elif weapon_skin_id == 11:  # Example: default AUG
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["AUG Wings"])
                print("Changed AUG to Wings skin")
            elif weapon_skin_id == 13:  # Example: default Galil
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["Galil AR Tuxedo"])
                print("Changed Galil AR to Tuxedo skin")
            elif weapon_skin_id == 15:  # Example: default M4A4
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["M4A4 Decimator"])
                print("Changed M4A4 to Decimator skin")
            elif weapon_skin_id == 16:  # Example: default AWP
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["AWP Gungnir"])
                print("Changed AWP to Gungnir skin")
            elif weapon_skin_id == 20:  # Example: default gloves
                pm.write_int(item + offsets["m_iItemDefinitionIndex"], skin_ids["weapons"]["Sport Gloves Noctis"])
                print("Changed gloves to Noctis skin")

if __name__ == "__main__":
    change_to_custom_skins()
