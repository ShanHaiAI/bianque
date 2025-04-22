import hashlib
import json
import os

from pymilvus import MilvusClient

from core.llm_calling import OpenAIEmbeddingModel



class MilvusVectorKnowledgeBase:
    def __init__(self, collection_name="medical_docs", hash_file_path="data/inserted_hashes.json"):
        self.client = MilvusClient(uri='./data/data.db')
        self.collection_name = collection_name
        if self.collection_name not in self.client.list_collections():
            self.client.create_collection(self.collection_name, dimension=1024)
        self.model = OpenAIEmbeddingModel()

        self.hash_file_path = hash_file_path

    def _text_hash(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _load_inserted_hashes(self) -> set:
        if os.path.exists(self.hash_file_path):
            with open(self.hash_file_path, "r") as f:
                return set(json.load(f))
        return set()

    def _save_inserted_hashes(self, hashes: set):
        os.makedirs(os.path.dirname(self.hash_file_path), exist_ok=True)
        with open(self.hash_file_path, "w") as f:
            json.dump(list(hashes), f)

    def insert_documents(self, docs: list, batch_size: int = 1000, deduplicate: bool = True) -> str:
        """

        Args:
            docs:
            batch_size:
            deduplicate:

        Returns:

        """
        hashes = [self._text_hash(text) for text in docs]

        inserted_hashes = self._load_inserted_hashes() if deduplicate else set()

        embeddings = self.model.encode(docs)
        chunk_with_embeddings = []
        new_hashes = set()

        for i in range(len(docs)):
            h = hashes[i]

            if deduplicate and h in inserted_hashes:
                continue

            chunk_dict = {
                "id": i,
                "vector": embeddings[i],
                "text": docs[i],
                "hash": h,
                "subject": "history"
            }
            chunk_with_embeddings.append(chunk_dict)
            new_hashes.add(h)

        for i in range(0, len(chunk_with_embeddings), batch_size):
            batch = chunk_with_embeddings[i:i + batch_size]
            self.client.insert(collection_name=self.collection_name, data=batch)
            print("Inserted {} documents".format(len(batch)))

        if deduplicate:
            inserted_hashes.update(new_hashes)
            self._save_inserted_hashes(inserted_hashes)

        return f"Inserted {len(chunk_with_embeddings)} new documents."

    def search(self, user_query: str, top_k: int = 5):
        query_embedding = self.model.encode([user_query])
        search_results = self.client.search(
            collection_name=self.collection_name,
            data=query_embedding,
            limit=top_k,
            output_fields=["text", "subject"],
        )
        return search_results


def vector_knowledge_query(query: str, kb: MilvusVectorKnowledgeBase) -> str:
    results = kb.search(query)
    output = "相关文档摘要：\n"
    for result in results[0]:
        output += f"文档内容: {result['entity']['text']}\n"
    return output


def read_documents_from_file(file_path: str) -> list:
    """
    从指定 JSON 文件中读取文档内容，
    处理逻辑：
      - 读取 JSON 后，将其转换为纯字符串形式
      - 如果数据为 dict，则按每个 key-value 对切割，
        构造 "key: value" 字符串，并去掉字符串中的大括号
      - 如果数据为 list，则对每个元素转换为字符串并去掉大括号
    最终返回一个仅包含纯字符串的列表
    """
    docs = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for k, v in data.items():
                        doc = f"{k}: {v}"
                        doc = doc.replace("{", "").replace("}", "")
                        docs.append(doc.strip())
                elif isinstance(data, list):
                    for item in data:
                        doc = str(item)
                        doc = doc.replace("{", "").replace("}", "")
                        docs.append(doc.strip())
                else:
                    pass
        except Exception as e:
            print(f"读取 {file_path} 失败: {e}")
    else:
        print(f"文件 {file_path} 不存在。")

    return docs



def initialize_knowledge_bases():
    """
    从 ./data 下指定三个 JSON 文件读取文档，
    分别生成三个知识库：
      - 诊断知识库（文件：./data/diagnosis_knowledge.json）
      - 体检报告数据知识库（文件：./data/physical_examination_reports.json）
      - 患者安抚知识库（文件：./data/patient_support.json）
    """
    file_mapping = {
        "diagnosis_knowledge": "../data/diagnosis_knowledge.json",
        "physical_examination_reports": "../data/physical_examination_reports.json",
        "patient_support": "../data/patient_support.json",
    }

    diagnosis_kb = MilvusVectorKnowledgeBase(collection_name="diagnosis_knowledge")
    physical_examination_kb = MilvusVectorKnowledgeBase(collection_name="physical_examination_reports")
    patient_support_kb = MilvusVectorKnowledgeBase(collection_name="patient_support")

    kb_instances = {
        "diagnosis_knowledge": diagnosis_kb,
        "physical_examination_reports": physical_examination_kb,
        "patient_support": patient_support_kb,
    }

    for kb_name, file_path in file_mapping.items():
        docs = read_documents_from_file(file_path)
        if docs:
            print(f"向 {kb_name} 上传 {len(docs)} 个文档...")
            kb_instances[kb_name].insert_documents(docs)
        else:
            print(f"{kb_name} 未能读取到文档。")

    return patient_support_kb, diagnosis_kb, physical_examination_kb,


# -----------------------------
# 7. 示例主程序
# -----------------------------
if __name__ == "__main__":
    diagnosis_kb, physical_examination_kb, patient_support_kb = initialize_knowledge_bases()

    query = "发热"
    print("诊断知识库查询结果：")
    print(vector_knowledge_query(query, diagnosis_kb))
    print("体检报告查询结果：")
    print(vector_knowledge_query(query, physical_examination_kb))
    print("患者安抚查询结果：")
    print(vector_knowledge_query(query, patient_support_kb))


