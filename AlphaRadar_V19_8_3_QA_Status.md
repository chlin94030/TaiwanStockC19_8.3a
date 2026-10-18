# Alpha Radar V19.8.3a — QA 與分階段實測

## 目的

修正 V19.8.2 在開始歷史研究後仍可能一次載入過大資料／建立過大輸出的問題。V19.8.3 不宣稱已找到新最佳權重，不以同一批開發資料反覆調權重直到變成正報酬。

## Cloud 安全階梯

40×4 → 60×6 → 80×8 → 100×12。150 檔以上改由離線 staged runner；300、600 檔仍可研究，但必須循序擴大。

## 已完成測試

- V19.8.3 stage tests：4 passed。
- V19.8 universe tests：32 passed。
- V19 / V19.1 UI tests：20 passed。
- V19.2 staged/default/download targeted tests：4 passed（另 25 deselected）。
- Python compile：新增 runner 及修改模組通過。
- 先前將多組較大型測試綁成單次命令時，曾碰到外層 120／180 秒工具時限，但在時限前沒有測試失敗訊息；因此本版不再以「一個超長工作」作為 Cloud 設計。

## 真實歷史 replay（既有 91 equities + 0050）

| 階段 | 股票 | 日期 | 完成案例 | 秒 | Peak RSS |
|---|---:|---:|---:|---:|---:|
| 1 | 40 | 4 | 12/12 | 7.890 | 329.3 MiB |
| 2 | 60 | 6 | 18/18 | 10.735 | 436.5 MiB |
| 3 | 80 | 8 | 23/24 | 15.469 | 550.6 MiB |
| 4 | 90 | 12 | 35/36 | 15.927 | 610.8 MiB |

四個規模的最新 5／20／60 日研究權重皆相同（相鄰階段 support Jaccard=1.0、weight L1=0）。這只支持「權重沒有因擴大到 90 檔而漂移」。績效並未同步證明有效：90 檔階段平均相對 0050 超額約為 5日 -0.14%、20日 -3.63%、60日 -12.52%。因此沒有把權重穩定誤判為獲利收斂，也沒有自動修改正式權重。

## 仍未驗證

- 100 檔以上真實 replay：既有歷史包只有 91 檔股票。
- 真實 150／300／600 檔的 Cloud／離線峰值資源與資料完整度。
- Streamlit Community Cloud 實際容器 RAM、WebSocket、供應商 API 配額。
- 新的獨立盲測／forward holdout 與真實成交。


## V19.8.3a hotfix checks
- Reproduced the reported logic path as a mocked `FinMind TaiwanStockInfo` 402 and verified automatic fallback to a TWSE/TPEx official-current-master dataframe: PASS.
- Verified universe progress is emitted before any price download, including the 2/3 fallback state and 3/3 ready state: PASS.
- Verified a failed task still renders its saved overall progress and stopping stage in the UI: PASS.
- `test_v19_ui.py`: 18 passed. `test_v1983_stages.py`: 4 passed. Focused Cloud/universe fallback tests: 11 passed.
- Modified Python files compile successfully. Actual Streamlit Community Cloud connectivity to TWSE/TPEx is still environment-dependent and cannot be certified from this local test environment.
