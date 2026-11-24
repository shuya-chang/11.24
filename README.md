# Ollama-Groq 視覺分析助手

上傳 JPG 或 PNG，輸入提示詞，並使用 Groq、Ollama-Cloud 或本機 Ollama 分析圖片。預設提示詞會要求以繁體中文回答。

## 部署到 Streamlit Community Cloud

1. 在 Streamlit Community Cloud 選擇 **Create app**，選取 GitHub 儲存庫 `shuya-chang/11.24` 和包含本程式的分支。
2. 將 **Main file path** 設為 `ch16-4-3.py`。Streamlit 會從 `requirements.txt` 安裝依賴。
3. 在 **Advanced settings → Secrets** 貼上要使用的服務金鑰，再按 **Deploy**。只需保留要啟用的項目。

```toml
GROQ_API_KEY = "在此填入 Groq API 金鑰"
OLLAMA_API_KEY = "在此填入 Ollama Cloud API 金鑰"
```

- Groq 使用 `qwen/qwen3.8-27b`。[建立 Groq API 金鑰](https://console.groq.com/keys)
- Ollama-Cloud 使用 `gemma4:31b`，由 Ollama Cloud 執行。[建立 Ollama API 金鑰](https://ollama.com/settings/keys)

請將金鑰保存在 Streamlit Secrets。本機 Ollama 選項預設隱藏，雲端部署維持預設即可。未設定金鑰的服務會顯示提示，其他服務可以獨立使用。

## 在本機執行

建議使用 Python 3.12。在專案目錄執行以下指令。

```shell
python -m pip install -r requirements.txt
python -m streamlit run ch16-4-3.py
```

在本機使用雲端服務時，可將上方適用的設定存成 `.streamlit/secrets.toml`，或設定同名環境變數。此 Secrets 檔案已列入 `.gitignore`。

要使用本機 Ollama，請先啟動 Ollama，執行 `ollama pull gemma4:12b`，並在本機 Secrets 加入 `ENABLE_LOCAL_OLLAMA = "true"`。本機模式無需 API 金鑰。
