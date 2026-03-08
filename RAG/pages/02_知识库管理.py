import os
import streamlit as st
from knowledge_base import KnowledgeBaseService
import config_data as config

# 页面配置
st.set_page_config(page_title="知识库管理", layout="centered")

st.title("📚 证据库管理服务")
st.markdown("上传新的证据文件（PDF/DOCX/TXT），系统将自动更新向量数据库。")
st.divider()

# 初始化服务
if "kb_service" not in st.session_state:
    st.session_state["kb_service"] = KnowledgeBaseService()

# 文件上传
uploaded_files = st.file_uploader(
    "选择文件上传",
    type=['pdf', 'docx', 'txt', 'md'],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 开始索引"):
        saved_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(config.UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(file_path)
            st.info(f"已暂存: {uploaded_file.name}")

        with st.spinner("🧠 正在生成向量索引并更新 FAISS 库..."):
            try:
                result = st.session_state["kb_service"].ingest_files(saved_paths)
                st.success(f"处理完成: {result}")
            except Exception as e:
                st.error(f"索引失败: {str(e)}")
