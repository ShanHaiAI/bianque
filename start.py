from dotenv import load_dotenv

from core.basic_class import get_logger
from front.web import demo

logger = get_logger()
def main():
    load_dotenv()  # 加载 .env 文件环境变量
    logger.info("启动扁鹊 AI 医疗自诊服务……")
    demo.launch(share=True)

if __name__ == '__main__':
    main()
