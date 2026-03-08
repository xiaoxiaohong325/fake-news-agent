import logging
import re
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi

from file_history_store import get_history
from vector_stores import VectorStoreService, DashScopeEmbeddings
import config_data as config

logger = logging.getLogger("RagService")

class RagService(object):
    def __init__(self):
        # 初始化组件
        self.embedding = DashScopeEmbeddings(model_name=config.embedding_model_name)
        self.vector_service = VectorStoreService(embedding=self.embedding)
        self.chat_model = ChatTongyi(model=config.chat_model_name, dashscope_api_key=config.API_KEY)

        # 1. 事实核查提示词 (用于判定模式)
        self.verify_prompt = ChatPromptTemplate.from_template("""你是一名资深的娱乐信息事实核查员。请根据提供的背景证据（Context）来核查用户输入的新闻（Question）。

### 判定逻辑：
1. **对比分析**：检查证据中提到的事件、人物、时间是否与新闻吻合。
2. **冲突检测**：如果背景证据中包含官方辟谣，或时间线上存在逻辑矛盾，请判定为“虚假”。
3. **解释性**：不仅给出结果，还要指出具体是哪条证据支撑了你的判定。
4. **诚实原则**：如果背景证据中没有任何相关信息，请回答“库中暂无相关证据，无法判定”，严禁编造。

### 背景证据 (Context):
{context}

### 待核查新闻 (Question):
{input}

---
### 鉴定报告输出格式：
- **鉴定结果**：[真实 / 虚假 / 存疑]
- **核心理由**：[一句话简述理由]
- **逻辑拆解**：[对比新闻与证据的相同与不同点]
- **参考证据**：[列出参考的证据来源和时间]
""")

        # 2. 对话助手提示词 (用于对话模式)
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个虚假新闻核查对话助手。你可以基于提供的知识库证据({context})来回答用户关于娱乐新闻的追问或日常对话。"),
            MessagesPlaceholder("history"),
            ("user", "{input}")
        ])

        # 初始化链
        self.verify_chain = self._build_verify_chain()
        self.chat_chain = self._build_chat_chain()

    def _format_docs(self, docs: List[Document]):
        if not docs:
            return "无相关参考资料"
        formatted = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "未知来源")
            content = doc.page_content.strip().replace("\n", " ")
            formatted.append(f"--- 证据碎片 {i + 1} [来源: {source}] ---\n内容: {content}")
        return "\n\n".join(formatted)

    def _build_verify_chain(self):
        """构建事实核查链（不含历史记录，专注当前事实）"""
        retriever = self.vector_service.get_retriever()
        
        chain = (
            {
                "context": (lambda x: x["input"]) | retriever | self._format_docs,
                "input": lambda x: x["input"]
            }
            | self.verify_prompt
            | self.chat_model
            | StrOutputParser()
        )
        return chain

    def _build_chat_chain(self):
        """构建对话链（含历史记录）"""
        retriever = self.vector_service.get_retriever()
        
        inner_chain = (
            {
                "context": (lambda x: x["input"]) | retriever | self._format_docs,
                "input": lambda x: x["input"],
                "history": lambda x: x["history"]
            }
            | self.chat_prompt
            | self.chat_model
            | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            inner_chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain

    def verify(self, query: str):
        """执行单次事实核查"""
        logger.info(f"🔎 启动事实核查: {query[:30]}...")
        return self.verify_chain.invoke({"input": query})

    def chat(self, query: str, session_id: str = "default_user"):
        """执行对话交互"""
        logger.info(f"💬 启动对话会话 ({session_id}): {query[:30]}...")
        session_config = {"configurable": {"session_id": session_id}}
        return self.chat_chain.invoke({"input": query}, session_config)

if __name__ == '__main__':
    service = RagService()
    
    # 测试核查
    print("--- 事实核查测试 ---")
    print(service.verify("听说蔡徐坤要开演唱会了是真的吗？"))
    
    # 测试对话
    print("\n--- 连续对话测试 ---")
    print(service.chat("你好，你是谁？"))
    print(service.chat("帮我查查周杰伦最近的消息"))
