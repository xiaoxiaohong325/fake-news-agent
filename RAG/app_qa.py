import streamlit as st
from rag import RagService
import config_data as config

# 页面配置
st.set_page_config(page_title="虚假娱乐信息核查系统", layout="wide")

st.title("🛡️ 虚假娱乐信息核查系统")
st.markdown("基于 RAG 技术的智能事实核对与对话助手")
st.divider()

# 初始化 RagService
if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 设置")
    mode = st.radio("选择运行模式：", ["事实核查报告", "智能对话模式"])
    session_id = st.text_input("会话 ID", value="user_001")
    if st.button("清除历史记录"):
        st.session_state["messages"] = []
        st.rerun()

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "你好！我是虚假信息核查助手。请输入你想要核实的新闻内容。"}]

# 显示历史消息
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 用户输入
if prompt := st.chat_input("输入新闻内容或问题..."):
    # 显示用户输入
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # AI 响应
    with st.chat_message("assistant"):
        with st.spinner("正在检索并分析..."):
            try:
                if mode == "事实核查报告":
                    # 模式 A: 专注事实核对
                    response = st.session_state["rag"].verify(prompt)
                else:
                    # 模式 B: 连续对话
                    response = st.session_state["rag"].chat(prompt, session_id=session_id)
                
                st.write(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"发生错误: {str(e)}"
                st.error(error_msg)
                st.session_state["messages"].append({"role": "assistant", "content": error_msg})
