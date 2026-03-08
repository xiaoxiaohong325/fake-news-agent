import streamlit as st

st.set_page_config(
    page_title="虚假娱乐信息核查专家系统",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ 虚假娱乐信息核查专家系统")
st.markdown("""
### 欢迎使用本系统！
这是一个基于 RAG (检索增强生成) 技术的专业事实核查平台。

#### 👈 请在左侧菜单选择功能：

1. **🛡️ 新闻核查与对话**：
   - 输入一段新闻进行“事实核查报告”生成。
   - 进行“多轮对话”，追问更多细节。
   
2. **📚 知识库管理**：
   - 上传 PDF/Word/TXT 证据文件。
   - 更新 FAISS 向量索引库。

---
**当前状态：**
- 嵌入模型：`text-embedding-v3` (阿里云)
- 推理模型：`qwen-max` (通义千问)
""")
