import json, os
CONFIG_PATH = 'config.json'
FLOWS_PATH = 'flows.json'
def load_config():
    if not os.path.exists(CONFIG_PATH):
        # create default config to avoid crashes
        default = {
            "token": None,
            "application_id": None,
            "embed_color": "0x2f3136",
            "logos": {},
            "staff_role_id": None,
            "log_channel_id": None,
            "ticket_category_id": None,
            "panel": {
                "title": "💸 Exchange Panel",
                "description": "Choose your sending method below:",
                "placeholder": "Select method"
            }
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default, f, indent=2)
        return default
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_flows():
    if not os.path.exists(FLOWS_PATH):
        # create example flows file
        example = { "methods": {} }
        with open(FLOWS_PATH, 'w', encoding='utf-8') as f:
            json.dump(example, f, indent=2)
        return example
    with open(FLOWS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
