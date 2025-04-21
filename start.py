from dotenv import load_dotenv
from front.web import demo
from logger import logger

def main():
    load_dotenv()  # 加载 .env 文件环境变量
    logger.info("启动扁鹊 AI 医疗自诊服务……")
    demo.launch()

if __name__ == '__main__':
    main()
