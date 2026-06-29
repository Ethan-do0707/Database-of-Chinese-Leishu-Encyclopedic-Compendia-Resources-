# 《唐類函》結構化數據

本目錄保存《唐類函》卷一至卷二百的結構化抓取結果。數據來源為識典古籍頁面：

https://www.shidianguji.com/book/HY7244/chapter/1l1u7tac5qr0f?page_from=searching_page&version=14

## 內容

- `catalog.json`：識典古籍目錄元數據。
- `summary.json`：本次抓取與結構化統計。
- `tang_leihan.json`：全量合併 JSON，因文件較大使用 Git LFS 管理。
- `json/`：200 卷分卷 JSON。
- `md/`：200 卷分卷 Markdown。
- `docs/structure.md`：字段與解析規則說明。
- `scripts/scrape_tang_leihan.py`：可復跑的抓取與導出腳本。

## 結構字段

數據按卷數、部類、門目、層次、條目與注文整理：

- `volume`：卷名。
- `category`：部類。
- `topics`：門目。
- `layers`：層次，包含 `敘事`、`事對`、`詩文`。
- `items`：條目。
- `notes`：注文。
- `raw_lines`：保留來源頁面的行級文本、行類型與頁碼標記，便於復核。

## 統計

- 分卷 JSON：200 份。
- 分卷 Markdown：200 份。
- 結構化條目：47,364。
- 原始行：208,102。
- 層次統計：`敘事` 23,706，`事對` 21,904，`詩文` 1,754。

## 已知問題

卷一百三十一的部類源行疑似 OCR 為「人邵十十」。由於缺少直接可驗證證據，腳本未將其強行改寫，該卷 `category` 暫保留為空；原始行已保留在 `raw_lines` 中，可供後續人工校訂。

## 復跑

在 Python 3 環境中可使用：

```powershell
python scripts\scrape_tang_leihan.py --skip-front-matter --delay 0.5 --output-dir data
```

復跑時請注意來源網站的訪問規則與數據使用權限。

