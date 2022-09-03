# 使用方式

## 1. 將資料夾 clone 到本機

`git clone https://github.com/andreashih/shinyapp-python.git`

## 2. `cd` 到該資料夾，建立虛擬環境

`python -m venv venv`（若失敗請試試 `python3 -m venv venv`）

## 3. 進入虛擬環境

`source venv/bin/activate`

## 4. 下載必備套件

`pip install -r requirements.txt`

## 5. 執行 Shiny App

`shiny run --reload`，再用瀏覽器開啟 `http://localhost:8000`（可能需要稍待片刻）
