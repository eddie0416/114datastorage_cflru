# 114DataStorage CFLRU

## 專案簡介
**114DataStorage CFLRU** 是針對成功大學 114-1「資料儲存系統導論」期末專案所開發的程式，旨在針對學術論文 **"CFLRU: a replacement algorithm for flash memory"** 中的演算法。此專案專注於模擬與測試提升快閃記憶體效率的頁面置換算法，並對 CFLRU（Clean First Least Recently Used）進行復現，從而分析其效能。

CFLRU 提供了一種較具優勢的快取替換策略，透過優先移除乾淨頁面（clean pages）來優化快閃記憶體的寫入成本。

## 功能概述
- **實現 CFLRU 置換演算法**：支援多種測試場景，包含實驗配置及分析結果匯出。
- **多重緩存策略模擬**：額外支援模組化 LRU 及 Belady MIN（理論最佳）等演算法。
- **實驗數據前處理與分析**：生成可用於後續處理的規範化資料。

## 專案結構
```
114datastorage_cflru/
├── algorithm/           # 各式置換算法實作 (e.g., CFLRU, LRU, Belady MIN)
├── clean_spc.py         # 跨頁面數據轉換腳本
├── data_clean.py        # 追蹤檔處理與格式轉換
├── main.py              # 測試框架主程式
├── spec.py              # 演算法的基本類別定義
└── utils.py             # 分析和匯總 trace 數據的工具程式
```

## 啟動指南

### 1. Clone
```bash
git clone https://github.com/eddie0416/114datastorage_cflru.git
cd 114datastorage_cflru
```

### 2. 清理原始 trace
運行數據清理模塊，將原始 `.trace` 或 `.txt` 文件轉換為標準化的 `.csv` 文件：
```bash
python data_clean.py traces/
```

### 3. 運行模擬實驗
執行主程式進行演算法測試：
```bash
python main.py
```
- 預設使用 `/traces_cleaned/` 資料夾中的測試檔案。
- 可自訂快取容量與演算法進行模擬。
