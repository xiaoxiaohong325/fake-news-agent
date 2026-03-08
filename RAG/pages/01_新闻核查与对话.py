import streamlit as st
from rag import RagService
import config_data as config

# 设置页面
st.set_page_config(page_title="新闻核查与对话", layout="wide")

st.title("🛡️ 虚假娱乐信息核查与对话")
st.divider()

# 初始化 RagService
if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

# 侧边栏设置
with st.sidebar:
    st.header("⚙️ 设置")
    mode = st.radio("选择模式：", ["事实核查报告", "智能对话模式"])
    session_id = st.text_input("会话 ID", value="default_user")
    if st.button("清除历史记录"):
        st.session_state["messages"] = []
        st.rerun()

# 初始化消息
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "你好！我是核查助手。请输入你想要核实的新闻或问题。"}]

# 显示对话
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 用户输入
if prompt := st.chat_input("在此输入..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # AI 响应
    with st.chat_message("assistant"):
        with st.spinner("处理中..."):
            try:
                if mode == "事实核查报告":
                    response = st.session_state["rag"].verify(prompt)
                else:
                    response = st.session_state["rag"].chat(prompt, session_id=session_id)
                st.write(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
