import os
import logging
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from dashscope import TextEmbedding
import config_data as config

logger = logging.getLogger("VectorStore")

class DashScopeEmbeddings(Embeddings):
    """
    Qwen Embedding 封装
    """
    def __init__(self, model_name):
        self.model_name = model_name

    def embed_documents(self, texts):
        try:
            resp = TextEmbedding.call(
                model=self.model_name,
                input=[str(t) for t in texts],
                api_key=config.API_KEY
            )
            if resp.status_code == 200:
                return [item['embedding'] for item in resp.output['embeddings']]
            else:
                logger.error(f"Embedding API 错误: {resp.message}")
                return [[0.0] * 1536 for _ in texts]
        except Exception as e:
            logger.error(f"Embedding 异常: {e}")
            return [[0.0] * 1536 for _ in texts]

    def embed_query(self, text):
        return self.embed_documents([str(text)])[0]

class VectorStoreService(object):
    def __init__(self, embedding=None):
        self.embedding = embedding or DashScopeEmbeddings(model_name=config.embedding_model_name)
        self.vector_store_path = config.VECTOR_DB_PATH

        if Path(self.vector_store_path).exists():
            logger.info(f"✅ 加载本地向量库: {self.vector_store_path}")
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embedding,
                allow_dangerous_deserialization=True
            )
        else:
            logger.warning(f"⚠️ 知识库 {self.vector_store_path} 不存在，初始化新库。")
            # 临时占位，防止初始化失败
            from langchain_core.documents import Document
            self.vector_store = FAISS.from_documents(
                [Document(page_content="初始占位符", metadata={"source": "system"})],
                self.embedding
            )

    def get_retriever(self, k=None):
        """返回向量检索器"""
        top_k = k or config.similarity_threshold
        return self.vector_store.as_retriever(search_kwargs={"k": top_k})

    def save_local(self):
        """保存到本地"""
        self.vector_store.save_local(self.vector_store_path)

if __name__ == '__main__':
    service = VectorStoreService()
    retriever = service.get_retriever()
    res = retriever.invoke("测试检索")
    print(res)
