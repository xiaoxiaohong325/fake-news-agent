import os
import streamlit as st
from knowledge_base import KnowledgeBaseService
import config_data as config

# 页面配置
st.set_page_config(page_title="知识库更新服务", layout="centered")

st.title("📚 知识库更新服务")
st.markdown("上传新的证据文件（PDF/DOCX/TXT），系统将自动向量化并存入 FAISS。")
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
    st.subheader(f"已选择 {len(uploaded_files)} 个文件")
    
    if st.button("🚀 开始索引"):
        saved_paths = []
        for uploaded_file in uploaded_files:
            # 1. 保存到本地临时目录
            file_path = os.path.join(config.UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(file_path)
            st.info(f"💾 已保存: {uploaded_file.name}")

        # 2. 调用知识库服务
        with st.spinner("🧠 正在生成向量并更新 FAISS 库..."):
            try:
                result = st.session_state["kb_service"].ingest_files(saved_paths)
                st.success(f"✅ 处理完成: {result}")
            except Exception as e:
                st.error(f"❌ 索引失败: {str(e)}")

# 显示当前向量库状态
with st.sidebar:
    st.header("📊 库状态")
    if os.path.exists(config.VECTOR_DB_PATH):
        st.write(f"向量库路径: `{config.VECTOR_DB_PATH}`")
        st.write("状态: ✅ 已就绪")
    else:
        st.write("状态: ❌ 未初始化")
