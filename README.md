## SJZ_SkinToDoll
方便管理員協助玩家製作專屬玩偶材質的小py


## 主要功能：
### ・檢查玩家皮膚檔案是否存在：

在 textures/item/dolls/ 目錄下查找 {player_id}.png 檔案。
若檔案存在，則提示「已偵測到對應的皮膚檔案」。

若檔案不存在，則提示「您還沒上傳對應的皮膚至 dolls」。

### ・生成兩個 JSON 文件：
items/doll_{player_id}.json：定義物品的模型路徑。

models/item/doll_{player_id}.json：定義 3D 模型的結構、貼圖及顯示方式。

### ・確保目錄存在：
使用 os.makedirs() 確保 items/ 和 models/item/ 目錄存在，避免因目錄缺失而導致寫入失敗。

### ・錯誤處理：
若發生異常，則會捕獲並輸出錯誤訊息，避免腳本崩潰。

這個腳本的目的是讓管理員可以輕鬆將自訂娃娃模型加入 Minecraft 資源包，並確保對應的皮膚貼圖已經上傳。

僅適用於1.21.4石家庄伺服器。
