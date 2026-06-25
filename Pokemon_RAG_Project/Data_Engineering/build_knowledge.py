import os
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= 配置信息 =================
DEEPSEEK_API_KEY = "****************************************"
BASE_DIR = "/home/pokemon_dataset"
TUNNEL_URL = "http://8.160.163.5"
OUTPUT_FILE = "/home/pokemon_knowledge_base_cn.md"

# 线程池并发数限制
MAX_WORKERS = 25
# ============================================


def translate_to_english(chinese_text, api_key):
    """
    调用 DeepSeek API 将中文名字与描述精准翻译为英文
    """
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": (
                    "你是一个专业的生物特征与外观描述翻译助手。你的任务是将输入的中文宝可梦名字与外貌特征描述精准翻译为英文。\n"
                    "要求：\n"
                    "1. 直接返回英文翻译结果，不要输出任何解释、不要有废话或引导词。\n"
                    "2. 严格根据中文文字翻译，保留原有的结构（例如：输入'暴雪王, 草属性...'，对应翻译为'Abomasnow, Grass-type...'）。"
                )
            },
            {"role": "user", "content": chinese_text}
        ],
        "temperature": 0.1,
        "max_tokens": 300
    }
    
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            elif response.status_code == 429:
                time.sleep(2)
            else:
                pass
        except Exception:
            time.sleep(1)
            
    return None

def process_file(txt_file):
    pokemon_id = os.path.splitext(txt_file)[0]
    txt_path = os.path.join(BASE_DIR, txt_file)
    
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            chinese_description = f.read().strip()
    except Exception as e:
        return pokemon_id, ("读取失败", f"Read failed: {e}"), f"读取失败: {e}"

    english_description = translate_to_english(chinese_description, DEEPSEEK_API_KEY)
    if not english_description:
        return pokemon_id, (chinese_description, "Translation Failed"), "翻译失败(保留原著兜底)"
    
    return pokemon_id, (chinese_description, english_description), "成功"

def build_markdown_db():
    if not os.path.exists(BASE_DIR):
        print(f"错误: 路径 {BASE_DIR} 不存在")
        return

    files = [f for f in os.listdir(BASE_DIR) if f.endswith('.txt')]
    total_files = len(files)
    print(f"开启多线程翻译，共 {total_files} 个文件...")

    translation_results = {}
    completed_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {executor.submit(process_file, f): f for f in files}
        for future in as_completed(future_to_file):
            pokemon_id, desc_tuple, status = future.result()
            translation_results[pokemon_id] = desc_tuple
            completed_count += 1
            print(f"[{completed_count}/{total_files}] 宝可梦 {pokemon_id} 翻译完毕 ({status})")

    sorted_ids = sorted(translation_results.keys())
    markdown_entries = []

    for p_id in sorted_ids:
        png_file = f"{p_id}.png"
        chinese_description, english_description = translation_results[p_id]
        
        entry = (
            f"{chinese_description}\n"
            f"{english_description}\n"
            f"对应图片: {TUNNEL_URL}/{png_file}"
        )
        markdown_entries.append(entry)

    full_content = "\n\n".join(markdown_entries)
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"转换成功,已保存至: {OUTPUT_FILE}")
    except Exception as e:
        print(f"写入 .md 文件失败: {e}")

if __name__ == "__main__":
    build_markdown_db()