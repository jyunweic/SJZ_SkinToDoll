import os
import json


def create_doll_json():
    base_items_path = r"C:/Users/chenjyunwei/AppData/Roaming/PrismLauncher/instances/1.21.4/minecraft/resourcepacks/SJZ_ResourcePack_v1/assets/minecraft/items"
    base_models_path = r"C:/Users/chenjyunwei/AppData/Roaming/PrismLauncher/instances/1.21.4/minecraft/resourcepacks/SJZ_ResourcePack_v1/assets/minecraft/models/item"
    base_textures_path = r"C:/Users/chenjyunwei/AppData/Roaming/PrismLauncher/instances/1.21.4/minecraft/resourcepacks/SJZ_ResourcePack_v1/assets/minecraft/textures/item/dolls"
    template_path = os.path.join(base_models_path, "doll_template.json")
    
    player_id = input("請輸入 player_ID: ").strip()
    if not player_id:
        print("player_ID 不能為空！")
        return
    
    texture_file_path = os.path.join(base_textures_path, f"{player_id}.png")
    if not os.path.exists(texture_file_path):
        print("您還沒上傳對應的皮膚至 textures/item/dolls")
    else:
        print("已偵測到對應的皮膚檔案")
    
    items_file_name = f"doll_{player_id}.json"
    items_file_path = os.path.join(base_items_path, items_file_name)
    items_data = {
        "model": {
            "type": "minecraft:model",
            "model": f"item/doll_{player_id}"
        }
    }
    
    # 使用 doll_template.json 作為基礎
    models_file_name = f"doll_{player_id}.json"
    models_file_path = os.path.join(base_models_path, models_file_name)
    
    try:
        os.makedirs(base_items_path, exist_ok=True)
        os.makedirs(base_models_path, exist_ok=True)
        
        with open(items_file_path, "w", encoding="utf-8") as f:
            json.dump(items_data, f, indent=2, ensure_ascii=False)
        print(f"已成功創建: {items_file_path}")
        
        with open(template_path, "r", encoding="utf-8") as f:
            template_data = json.load(f)
        
        # 替換 {player_id}
        models_data = json.dumps(template_data).replace("{player_id}", player_id)
        models_data = json.loads(models_data)
        
        with open(models_file_path, "w", encoding="utf-8") as f:
            json.dump(models_data, f, indent=2, ensure_ascii=False)
        print(f"已成功創建: {models_file_path}")
        
    except Exception as e:
        print(f"發生錯誤: {e}")


if __name__ == "__main__":
    create_doll_json()