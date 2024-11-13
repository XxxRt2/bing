# config.py
import logging

# 设置 Telegram Bot 的日志记录级别
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# 这里可以设置您自己的配置，例如：
TOKEN = "7749410324:AAGYPwzvt2oPzTei3Ero_68jQb9NWZqk5eI"  # 替换为您自己的 Telegram Bot Token

