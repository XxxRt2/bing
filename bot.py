import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handler import handle_bet, start

# 启用日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # 用您的 token 替换
    TOKEN = '7749410324:AAGYPwzvt2oPzTei3Ero_68jQb9NWZqk5eI'
    
    updater = Updater(TOKEN, use_context=True)
    
    dp = updater.dispatcher
    
    # 处理 /start 命令
    dp.add_handler(CommandHandler("start", start))
    
    # 处理下注消息
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_bet))
    
    # 启动 Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
