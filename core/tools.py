import os
import pytesseract
from PIL import Image
from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection, list_collections
)
from sentence_transformers import SentenceTransformer


def ocr_extract_text(image_path: str) -> str:
    """
    使用 pytesseract 对上传的图片进行 OCR 解析，
    请确保 Tesseract 已安装且配置中文语言包（chi_sim）
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='chi_sim')
        return text
    except Exception as e:
        raise Exception("OCR 解析失败：" + str(e))


class MilvusVectorKnowledgeBase:
    def __init__(self, host=None, port=None, collection_name="medical_docs"):
        self.host = host or os.getenv("MILVUS_HOST", "localhost")
        self.port = port or os.getenv("MILVUS_PORT", "19530")
        self.collection_name = collection_name
        connections.connect("default", host=self.host, port=self.port)
        if self.collection_name not in list_collections():
            self.create_collection()
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def create_collection(self):
        id_field = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
        embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
        schema = CollectionSchema(fields=[id_field, embedding_field], description="专业文档集合")
        Collection(name=self.collection_name, schema=schema)

    def insert_documents(self, docs: list) -> str:
        embeddings = self.model.encode(docs)
        collection = Collection(self.collection_name)
        data = [embeddings.tolist()]
        collection.insert(data)
        collection.flush()
        return "文档上传成功！"

    def search(self, query: str, top_k: int = 5):
        query_embedding = self.model.encode([query])
        collection = Collection(self.collection_name)
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(query_embedding.tolist(), "embedding", search_params, limit=top_k)
        return results


def vector_knowledge_query(query: str) -> str:
    kb = MilvusVectorKnowledgeBase()
    results = kb.search(query)
    output = "相关文档摘要：\n"
    for result in results[0]:
        output += f"文档ID: {result.id}, 距离: {result.distance}\n"
    return output


if __name__ == "__main__":
    print(vector_knowledge_query("发热"))
    sample_path = "sample_report.jpg"
    print("OCR 解析结果：", ocr_extract_text(sample_path))
