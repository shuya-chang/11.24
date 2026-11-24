import base64
import io
import os

import streamlit as st
from groq import Groq
from ollama import Client
from PIL import Image, ImageOps, UnidentifiedImageError


def encode_image(image: Image.Image) -> str:
    """將圖片轉為 RGB JPEG Base64。"""
    buffered = io.BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("ascii")


def analyze_with_ollama(client, model, encoded_image, prompt):
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt, "images": [encoded_image]}],
    )
    return response.message.content


def analyze_with_groq(api_key, encoded_image, prompt):
    client = Groq(api_key=api_key, timeout=60)
    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}",
                }},
            ],
        }],
        temperature=0,
        max_completion_tokens=1024,
        top_p=0.5,
    )
    return completion.choices[0].message.content


def main():
    st.title("Ollama-Groq 視覺分析助手")
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    ollama_key = os.getenv("OLLAMA_API_KEY", "").strip()
    local_enabled = os.getenv("ENABLE_LOCAL_OLLAMA", "").lower() == "true"

    providers = ["Groq", "Ollama-Cloud"]
    if local_enabled:
        providers.append("Ollama（本機）")
    default_provider = 1 if ollama_key and not groq_key else 0
    provider = st.radio("選擇 API", providers, index=default_provider, horizontal=True)

    available = True
    if provider == "Groq" and not groq_key:
        st.info("請在 Secrets 設定 GROQ_API_KEY 後使用 Groq。")
        available = False
    elif provider == "Ollama-Cloud" and not ollama_key:
        st.info("請在 Secrets 設定 OLLAMA_API_KEY 後使用 Ollama-Cloud。")
        available = False

    uploaded_file = st.file_uploader("上傳圖檔", type=["jpg", "jpeg", "png"])
    prompt = st.text_area(
        "請輸入提示詞",
        value="請針對此圖片，使用繁體中文說明你看到了什麼？如果你是一位觀光客，請說明你看到的特點。",
        height=100,
    )
    if not st.button("分析影像", disabled=not available):
        return
    if uploaded_file is None:
        st.warning("請先上傳圖檔。")
        return
    if not prompt.strip():
        st.warning("請輸入提示詞。")
        return

    try:
        with Image.open(uploaded_file) as source:
            image = ImageOps.exif_transpose(source)
            encoded_image = encode_image(image)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        st.error("無法讀取圖檔，請重新上傳有效的 JPG 或 PNG。")
        return

    preview, output = st.columns(2)
    preview.image(image, caption="已上傳的圖檔")

    try:
        with st.spinner(f"使用 {provider} 分析中…"):
            if provider == "Groq":
                result = analyze_with_groq(groq_key, encoded_image, prompt.strip())
            elif provider == "Ollama-Cloud":
                client = Client(
                    host="https://ollama.com",
                    headers={"Authorization": f"Bearer {ollama_key}"},
                    timeout=60,
                )
                result = analyze_with_ollama(client, "gemma4:31b", encoded_image, prompt.strip())
            else:
                client = Client(timeout=60)
                result = analyze_with_ollama(client, "gemma4:12b", encoded_image, prompt.strip())
    except Exception as error:
        status = getattr(error, "status_code", None)
        status_text = f"（HTTP {status}）" if isinstance(status, int) else ""
        if provider == "Ollama（本機）":
            output.error(f"本機 Ollama 分析失敗{status_text}。請確認服務已啟動且模型已安裝。")
        else:
            output.error(f"{provider} 分析失敗{status_text}。請確認金鑰、模型存取權限及服務狀態。")
        return

    if not result or not result.strip():
        output.warning("模型沒有回傳文字，請調整提示詞後重試。")
        return
    output.success("影像分析完成")
    output.write(result.strip())


if __name__ == "__main__":
    main()
