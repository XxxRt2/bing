from bot.bot import start, bet, show_result, balance, cancel, handle_number, handle_amount
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

API_TOKEN = '7749410324:AAGYPwzvt2oPzTei3Ero_68jQb9NWZqk5eI'

def main():
    # 初始化数据库
    from bot.database import init_db
    init_db()

    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # 设置对话处理
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('bet', bet)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, handle_number)],
            2: [MessageHandler(Filters.text & ~Filters.command, handle_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('balance', balance))  # 余额查询命令
    dispatcher.add_handler(CommandHandler('result', show_result))  # 显示开奖结果命令

    # 启动机器人
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

