import requests
import uuid

def get_minecraft_skin(player_name):
    """
    取得 Minecraft 玩家的皮膚檔案。

    Args:
        player_name (str): Minecraft 玩家名稱。

    Returns:
        bytes: 皮膚檔案的二進位資料，如果成功取得，否則為 None。
    """

    try:
        # 1. 取得 UUID
        uuid_url = f"https://api.mojang.com/users/profiles/minecraft/{player_name}"
        uuid_response = requests.get(uuid_url)
        uuid_data = uuid_response.json()
        player_uuid = uuid_data["id"]

        # 2. 取得皮膚資訊
        session_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{player_uuid}"
        session_response = requests.get(session_url)
        session_data = session_response.json()

        # 有可能沒有 properties
        if "properties" not in session_data or not session_data["properties"]:
          print(f"找不到玩家 {player_name} 的皮膚資訊")
          return None

        # 皮膚資料在 properties 陣列中
        skin_data = session_data["properties"][0]["value"]
        import base64
        import json
        skin_data_decoded = base64.b64decode(skin_data).decode('utf-8')
        skin_url = json.loads(skin_data_decoded)["textures"]["SKIN"]["url"]

        # 3. 下載皮膚檔案
        skin_response = requests.get(skin_url)
        skin_response.raise_for_status()  # 檢查是否有錯誤

        return skin_response.content

    except requests.exceptions.RequestException as e:
        print(f"發生錯誤：{e}")
        return None
    except (KeyError, json.JSONDecodeError, TypeError) as e:
        print(f"解析 JSON 或處理資料時發生錯誤：{e}")
        return None

if __name__ == "__main__":
    player_name = input("請輸入 Minecraft 玩家名稱：")
    skin_data = get_minecraft_skin(player_name)

    if skin_data:
        # 將皮膚檔案儲存到本地
        with open(f"{player_name}_skin.png", "wb") as f:
            f.write(skin_data)
        print(f"已成功取得 {player_name} 的皮膚並儲存為 {player_name}_skin.png")
    else:
        print("無法取得皮膚。")