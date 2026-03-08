import os

# 阿里云配置
API_KEY = "sk-9e45f3a144844b7dbfd691dc69852ef7"
embedding_model_name = "text-embedding-v3"
chat_model_name = "qwen-max"

# FAISS 向量库配置
VECTOR_DB_PATH = "faiss_index_qwen"
collection_name = "fake_news_rag"

# 文本分割配置
chunk_size = 500
chunk_overlap = 50
separators = ["\n\n", "\n", "。", "！", "？", " ", ""]
max_split_char_number = 1000

# 检索配置
similarity_threshold = 4  # TOP_K

# 会话配置
session_config = {
    "configurable": {
        "session_id": "default_user",
    }
}

# 上传文件存储
UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
