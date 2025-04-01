# -*- coding: utf-8 -*-
import os
import json
import requests
import uuid
import base64
import zipfile # 用於處理 ZIP 檔案
import hashlib # 用於計算 SHA-1

def get_minecraft_skin(player_name, base_textures_path):
    """
    取得 Minecraft 玩家的皮膚檔案並儲存到指定路徑。

    Args:
        player_name (str): Minecraft 玩家名稱。
        base_textures_path (str): 儲存皮膚檔案的目錄。

    Returns:
        str: 儲存的皮膚檔案路徑，如果成功取得並儲存，否則為 None。
    """
    try:
        # 1. 取得 UUID
        uuid_url = f"https://api.mojang.com/users/profiles/minecraft/{player_name}"
        print(f"正在查詢 UUID: {uuid_url}") # 增加調試信息
        uuid_response = requests.get(uuid_url, timeout=10) # 增加超時
        uuid_response.raise_for_status()  # 檢查 HTTP 錯誤
        uuid_data = uuid_response.json()
        if not uuid_data or "id" not in uuid_data:
             print(f"找不到玩家 '{player_name}' 的 UUID 或回傳資料格式錯誤。")
             return None
        player_uuid = uuid_data["id"]
        print(f"取得 UUID: {player_uuid}")

        # 2. 取得皮膚資訊
        session_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{player_uuid}"
        print(f"正在查詢 Session: {session_url}") # 增加調試信息
        session_response = requests.get(session_url, timeout=10) # 增加超時
        session_response.raise_for_status()
        session_data = session_response.json()
        print("Session 資料取得成功。")

        if "properties" not in session_data or not session_data["properties"]:
            print(f"找不到玩家 {player_name} 的 'properties' 資訊")
            return None

        # 尋找 textures 屬性
        textures_property = None
        for prop in session_data["properties"]:
            if prop.get("name") == "textures":
                textures_property = prop
                break

        if not textures_property:
            print(f"在玩家 {player_name} 的資料中找不到 'textures' 屬性")
            return None

        skin_data = textures_property["value"]
        print("正在解碼 Base64 皮膚資料...")
        skin_data_decoded = base64.b64decode(skin_data).decode('utf-8')
        skin_info = json.loads(skin_data_decoded)
        print("皮膚資料解碼與解析成功。")

        if "textures" not in skin_info or "SKIN" not in skin_info["textures"] or "url" not in skin_info["textures"]["SKIN"]:
             print(f"玩家 {player_name} 的皮膚資料格式不符或缺少皮膚 URL")
             return None

        skin_url = skin_info["textures"]["SKIN"]["url"]
        print(f"取得皮膚 URL: {skin_url}")

        # 3. 下載皮膚檔案
        print("正在下載皮膚檔案...")
        skin_response = requests.get(skin_url, timeout=15) # 增加超時
        skin_response.raise_for_status()
        skin_filename = f"{player_name.lower()}.png" # 確保文件名小寫
        skin_file_path = os.path.join(base_textures_path, skin_filename)

        # 確保目標目錄存在
        print(f"確保目錄存在: {base_textures_path}")
        os.makedirs(base_textures_path, exist_ok=True)

        print(f"正在儲存皮膚檔案至: {skin_file_path}")
        with open(skin_file_path, "wb") as f:
            f.write(skin_response.content)
        print(f"已成功取得 {player_name} 的皮膚並儲存為 {skin_file_path}")
        return skin_file_path

    except requests.exceptions.Timeout:
        print(f"請求 Mojang API 超時，請檢查網路連線或稍後再試。")
        return None
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
             if e.response.status_code == 404:
                 print(f"找不到玩家名稱 '{player_name}' 的 UUID 或 Session 資料。請檢查名稱是否正確。")
             elif e.response.status_code == 429:
                 print(f"請求過於頻繁 (429 Too Many Requests)，請稍後再試。 ({e})")
             else:
                 print(f"請求時發生 HTTP 錯誤：{e} (狀態碼: {e.response.status_code})")
        else:
             print(f"請求時發生網路錯誤：{e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"解析 Mojang API 回傳資料時發生錯誤，可能是 API 格式變更或玩家資料不完整：{e}")
        return None
    except (json.JSONDecodeError, TypeError) as e:
        print(f"解析 JSON 或處理 Base64 資料時發生錯誤：{e}")
        return None
    except Exception as e:
        print(f"取得皮膚時發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc() # 打印詳細的追蹤信息
        return None


def create_doll_json(player_id, base_items_path, base_models_path, base_textures_path, template_path):
    """
    生成 Minecraft 物品和模型的 JSON 文件。
    (此版本根據要求修改 items JSON 的結構)

    Args:
        player_id (str): Minecraft 玩家 ID.
        base_items_path (str): 物品 JSON 文件的儲存路徑.
        base_models_path (str): 模型 JSON 文件的儲存路徑.
        base_textures_path (str): 皮膚檔案的儲存路徑. (此函數中未使用，但保留以供參考)
        template_path (str): 模型 JSON 模板檔案的路徑.
    """
    # 確保使用小寫 ID，因為 Minecraft 內部通常區分大小寫且偏好小寫
    model_ref_id = player_id.lower()

    # --- ITEMS JSON ---
    items_file_name = f"doll_{model_ref_id}.json" # 物品文件名也用小寫 ID
    items_file_path = os.path.join(base_items_path, items_file_name)

    # ***** 使用者指定的結構 *****
    items_data = {
        "model": {
            "type": "minecraft:model",
            "model": f"item/doll_{model_ref_id}" # 指向對應的模型文件
        }
    }
    # ***** 結構定義結束 *****

    # --- MODELS JSON ---
    models_file_name = f"doll_{model_ref_id}.json" # 模型文件名也用小寫 ID
    models_file_path = os.path.join(base_models_path, models_file_name)

    try:
        print(f"確保目錄存在: {base_items_path}")
        os.makedirs(base_items_path, exist_ok=True)
        print(f"確保目錄存在: {base_models_path}")
        os.makedirs(base_models_path, exist_ok=True)

        # 檢查模板文件是否存在
        print(f"檢查模板檔案: {template_path}")
        template_exists = os.path.isfile(template_path)
        if not template_exists:
             print(f"警告：找不到模型模板檔案 '{template_path}'，模型 JSON 將不會被創建或更新。")
             # 即使物品 JSON 可以生成，缺少模型模板也意味著資源包不完整

        # 創建物品 JSON (使用新的 items_data 結構)
        print(f"正在創建物品 JSON: {items_file_path}")
        with open(items_file_path, "w", encoding="utf-8") as f:
            json.dump(items_data, f, indent=2, ensure_ascii=False) # 使用 indent=2 匹配使用者範例
        print(f"已成功創建物品 JSON: {items_file_path}")

        # --- 模型 JSON 處理 ---
        # 只有在模板存在時才嘗試生成模型 JSON
        if template_exists:
            print(f"正在處理模型 JSON 模板: {template_path}")
            try:
                # 讀取並處理模型 JSON 模板
                with open(template_path, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                # 替換模板中的佔位符（確保使用小寫 ID）
                # 這裡假設模板中使用 {player_id} 作為皮膚貼圖路徑的一部分
                # 請根據你的 doll_template.json 調整替換邏輯
                print("正在替換模板中的佔位符...")
                models_data_str = json.dumps(template_data, indent=2, ensure_ascii=False)
                models_data_str = models_data_str.replace("{player_id}", model_ref_id)
                # 可能需要替換模型自己的引用，如果模板中有類似 "parent": "item/doll_{player_id}" 的情況
                # models_data_str = models_data_str.replace("{model_id}", f"doll_{model_ref_id}")

                models_data = json.loads(models_data_str)

                # 創建模型 JSON
                print(f"正在創建模型 JSON: {models_file_path}")
                with open(models_file_path, "w", encoding="utf-8") as f:
                    json.dump(models_data, f, indent=2, ensure_ascii=False) # 使用 indent=2
                print(f"已成功創建模型 JSON: {models_file_path}")

            except json.JSONDecodeError as e:
                 print(f"處理模型模板或創建模型 JSON 時解析 JSON 出錯：{e}")
            except Exception as e:
                 print(f"處理模型模板或創建模型 JSON 時發生未預期的錯誤: {e}")
                 import traceback
                 traceback.print_exc()
        # else: # 已在前面打印警告
        #      print(f"由於找不到模板檔案 '{template_path}'，已跳過模型 JSON 的生成。")

    except FileNotFoundError as e:
        print(f"創建 JSON 時發生錯誤：找不到檔案或路徑 {e}")
    except Exception as e:
        print(f"創建 JSON 時發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()


def create_and_hash_resource_pack_zip(resource_pack_dir, output_zip_path):
    """
    檢查並刪除舊的資源包 ZIP 檔，然後重新打包指定內容並計算 SHA-1。

    Args:
        resource_pack_dir (str): 資源包內容的根目錄 (例如 .../SJZ_ResourcePack)。
        output_zip_path (str): 要輸出的 ZIP 檔案完整路徑 (例如 .../resourcepacks/SJZ_ResourcePack.zip)。

    Returns:
        str: 新產生的 ZIP 檔案的 SHA-1 值，若失敗則返回 None。
    """
    try:
        # 1. 檢查並刪除舊的 ZIP 檔案
        if os.path.exists(output_zip_path) and os.path.isfile(output_zip_path):
            print(f"找到現有的 ZIP 檔案: {output_zip_path}，正在刪除...")
            try:
                os.remove(output_zip_path)
                print("舊檔案已刪除。")
            except OSError as e:
                print(f"刪除舊 ZIP 檔案時發生錯誤: {e}。請檢查檔案是否被其他程式佔用。")
                return None # 刪除失敗則不繼續

        # 2. 定義要包含在 ZIP 中的內容
        items_to_zip = {
            "assets": os.path.join(resource_pack_dir, "assets"),
            "pack.png": os.path.join(resource_pack_dir, "pack.png"),
            "pack.mcmeta": os.path.join(resource_pack_dir, "pack.mcmeta"),
        }

        # 檢查必要文件是否存在
        pack_mcmeta_path = items_to_zip["pack.mcmeta"]
        assets_path = items_to_zip["assets"]
        if not os.path.exists(pack_mcmeta_path):
             print(f"錯誤：找不到必要的 'pack.mcmeta' 檔案於 '{pack_mcmeta_path}'。無法建立資源包 ZIP。")
             return None
        if not os.path.exists(assets_path) or not os.listdir(assets_path): # 檢查 assets 是否存在且非空
             print(f"警告：'assets' 資料夾不存在或為空於 '{assets_path}'。建立的 ZIP 可能無效。")
             # 根據需求決定是否要停止
             # return None

        print(f"開始建立新的 ZIP 檔案: {output_zip_path}")
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for name_in_zip, path_on_disk in items_to_zip.items():
                if not os.path.exists(path_on_disk):
                    # 對於 pack.png，不存在是可選的，但 assets 和 pack.mcmeta 通常是必須的
                    if name_in_zip != "pack.png":
                         print(f"警告：找不到要壓縮的項目 '{path_on_disk}'，將跳過。")
                    continue

                if os.path.isfile(path_on_disk):
                    # 如果是文件，直接寫入
                    print(f"  壓縮檔案: {name_in_zip}")
                    zipf.write(path_on_disk, arcname=name_in_zip)
                elif os.path.isdir(path_on_disk):
                    # 如果是目錄，遞迴加入所有內容
                    print(f"  壓縮目錄: {name_in_zip}")
                    for root, dirs, files in os.walk(path_on_disk):
                        # 計算相對路徑，作為在 ZIP 中的路徑
                        relative_root = os.path.relpath(root, resource_pack_dir)
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join(relative_root, file).replace("\\", "/") # 確保使用 Unix 風格路徑分隔符
                            print(f"    壓縮檔案: {arcname}")
                            zipf.write(file_path, arcname=arcname)
                    # 可選：加入空目錄 (通常不需要，除非有特殊需求)
                    # for d in dirs:
                    #    dir_path = os.path.join(root, d)
                    #    arcname = os.path.join(os.path.relpath(dir_path, resource_pack_dir)).replace("\\", "/")
                    #    zip_info = zipfile.ZipInfo(arcname + "/")
                    #    zipf.writestr(zip_info, "")


        print(f"ZIP 檔案創建完成: {output_zip_path}")

        # 3. 計算新 ZIP 檔案的 SHA-1 值
        print("正在計算 SHA-1...")
        sha1_hash = hashlib.sha1()
        try:
            with open(output_zip_path, 'rb') as f:
                while True:
                    # 讀取文件塊，避免一次載入大文件到記憶體
                    chunk = f.read(8192) # 增加塊大小
                    if not chunk:
                        break
                    sha1_hash.update(chunk)
            sha1_hex = sha1_hash.hexdigest()
            print(f"新 {os.path.basename(output_zip_path)} 的 SHA-1 值: {sha1_hex}")
            return sha1_hex
        except FileNotFoundError:
            print(f"錯誤：找不到剛創建的 ZIP 檔案 '{output_zip_path}' 來計算 SHA-1。")
            return None
        except Exception as e:
             print(f"計算 SHA-1 時發生錯誤: {e}")
             return None

    except OSError as e:
        print(f"處理 ZIP 檔案時發生作業系統錯誤: {e}")
        return None
    except Exception as e:
        print(f"創建或處理 ZIP 檔案時發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None


# --- 主程式區塊 ---
if __name__ == "__main__":
    print("腳本開始執行...")
    # --- 路徑設定 ---
    try:
        # 嘗試自動偵測 AppData 路徑
        appdata_path = os.getenv('APPDATA')
        if not appdata_path:
             raise ValueError("無法讀取 APPDATA 環境變數")
        # 請根據你的 Prism Launcher 實際安裝情況調整 'PrismLauncher' 和實例名稱 '1.21.4(1)'
        instance_name = "1.21.4(1)" # <--- 如果你的實例名稱不同，請修改這裡
        instance_base_path = os.path.join(appdata_path, "PrismLauncher", "instances", instance_name, "minecraft")
        print(f"自動偵測到實例路徑: {instance_base_path}")

        if not os.path.isdir(instance_base_path):
             print(f"錯誤：自動偵測的路徑不存在 '{instance_base_path}'")
             print("請手動檢查並修改腳本中的 instance_base_path")
             # 你可以在這裡提供一個手動設定路徑的備選方案
             # instance_base_path = r"C:/手動/指定/路徑/minecraft" # 例如

        resourcepacks_base_path = os.path.join(instance_base_path, "resourcepacks")
        resource_pack_name = "SJZ_ResourcePack" # <--- 你的資源包名稱
        resource_pack_dir = os.path.join(resourcepacks_base_path, resource_pack_name)

        # 檢查核心資源包目錄是否存在，如果不存在則創建它
        if not os.path.isdir(resource_pack_dir):
            print(f"資源包目錄 '{resource_pack_dir}' 不存在，將嘗試創建...")
            try:
                os.makedirs(resource_pack_dir)
                print(f"已創建目錄: {resource_pack_dir}")
                # 同時創建 assets 目錄結構的基礎
                os.makedirs(os.path.join(resource_pack_dir, "assets", "minecraft"), exist_ok=True)
                print(f"已創建基礎 assets 目錄結構")
                # 提醒使用者需要 pack.mcmeta
                print(f"請確保 '{os.path.join(resource_pack_dir, 'pack.mcmeta')}' 檔案存在於資源包目錄中。")
            except OSError as e:
                print(f"創建資源包目錄時發生錯誤: {e}")
                exit() # 無法創建目錄則退出


        base_items_path = os.path.join(resource_pack_dir, "assets", "minecraft", "items")
        base_models_path = os.path.join(resource_pack_dir, "assets", "minecraft", "models", "item")
        base_textures_path = os.path.join(resource_pack_dir, "assets", "minecraft", "textures", "item", "dolls")
        template_path = os.path.join(base_models_path, "doll_template.json") # 模板應放在 models/item 內

 # ZIP 檔案輸出路徑 (修改：輸出到資源包目錄內部)
        output_zip_file = os.path.join(resource_pack_dir, f"{resource_pack_name}.zip")
    except Exception as e:
        print(f"設定路徑時發生錯誤: {e}")
        exit() # 路徑設定失敗則退出

    # --- 主邏輯 ---
    player_id = input("請輸入 Minecraft 玩家名稱: ").strip()
    if not player_id:
        print("玩家名稱不能為空！")
    else:
        print("-" * 20)
        print(f"正在處理玩家: {player_id}")

        # 確保 skins 目錄存在
        os.makedirs(base_textures_path, exist_ok=True)

        skin_file_path = get_minecraft_skin(player_id, base_textures_path)

        if skin_file_path:
            # 只有成功獲取皮膚後才創建 JSON
            create_doll_json(player_id, base_items_path, base_models_path, base_textures_path, template_path)
        else:
            print("無法取得玩家皮膚，跳過 JSON 生成。")

        print("-" * 20)
        # 無論是否成功獲取皮膚和生成 JSON，都嘗試重新打包 ZIP
        print("準備更新資源包 ZIP 檔案...")
        create_and_hash_resource_pack_zip(resource_pack_dir, output_zip_file)

    print("-" * 20)
    # 使用 input() 保持窗口開啟，直到使用者按下 Enter
    input("腳本執行完畢。按 Enter 鍵結束...")