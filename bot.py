import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from random import randint
import logging
from config import API_KEY, ADMINS, LOTTERY_API_URL

# 设置日志记录
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# 用户管理类
class User:
    def __init__(self, user_id, balance=1000):
        """ 初始化用户，默认余额为1000 """
        self.user_id = user_id
        self.balance = balance

    def bet(self, amount):
        """ 用户投注，减少余额 """
        if amount <= self.balance:
            self.balance -= amount
            return True  # 下注成功
        else:
            return False  # 余额不足，下注失败

    def add_balance(self, amount):
        """ 用户充值，增加余额 """
        self.balance += amount

    def get_balance(self):
        """ 获取当前余额 """
        return self.balance


# 彩票机器人类
class LotteryBot:
    def __init__(self, updater):
        self.updater = updater
        self.dispatcher = updater.dispatcher
        self.users = {}  # 存储所有用户
        self.add_handlers()

    def add_user(self, user_id, balance=1000):
        """ 添加新用户 """
        if user_id not in self.users:
            self.users[user_id] = User(user_id, balance)

    def check_balance(self, user_id):
        """ 查询用户余额 """
        if user_id not in self.users:
            self.add_user(user_id)
        return self.users[user_id].get_balance()

    def bet_特码(self, user_id, amount):
        """ 处理特码下注 """
        if user_id in self.users and self.users[user_id].bet(amount):
            return amount * 47  # 假设 47 是特码的赔率
        return 0

    def admin_modify_balance(self, admin_id, user_id, amount):
        """ 管理员修改用户余额 """
        if admin_id in ADMINS:
            if user_id in self.users:
                self.users[user_id].add_balance(amount)
                return f"管理员 {admin_id} 修改了用户 {user_id} 的余额，增加了 {amount}，新余额为 {self.users[user_id].get_balance()}"
            else:
                return f"用户 {user_id} 不存在。"
        else:
            return f"管理员权限不足，{admin_id} 不是管理员。"

    def add_handlers(self):
        """ 添加所有处理器 """
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("balance", self.check_balance_command))
        self.dispatcher.add_handler(CommandHandler("bet", self.handle_bet))
        self.dispatcher.add_handler(CommandHandler("admin", self.admin_commands))
        self.dispatcher.add_handler(CommandHandler("draw", self.draw))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.message_handler))

    def start(self, update: Update, context: CallbackContext):
        """ 发送欢迎信息 """
        update.message.reply_text("欢迎使用六和彩机器人！输入 /bet 开始投注，输入 /balance 查看余额。")

    def check_balance_command(self, update: Update, context: CallbackContext):
        """ 查看余额 """
        user_id = update.message.from_user.id
        balance = self.check_balance(user_id)
        update.message.reply_text(f"你的余额是: {balance} 元")

    def handle_bet(self, update: Update, context: CallbackContext):
        """ 处理下注 """
        user_id = update.message.from_user.id
        bet_info = update.message.text.split(" ", 2)
        if len(bet_info) < 3:
            update.message.reply_text("格式错误！请按如下格式下注：/bet 特码 50")
            return
        bet_type, amount = bet_info[1], int(bet_info[2])

        if bet_type == "特码":
            result = self.bet_特码(user_id, amount)
            if result > 0:
                update.message.reply_text(f"你下注成功，可能获得: {result} 元")
            else:
                update.message.reply_text("下注失败，余额不足。")

    def admin_commands(self, update: Update, context: CallbackContext):
        """ 管理员命令处理 """
        admin_id = update.message.from_user.id
        if admin_id not in ADMINS:
            update.message.reply_text("你没有管理员权限！")
            return

        args = update.message.text.split(" ")
        if len(args) < 3:
            update.message.reply_text("格式错误！请按如下格式使用管理员命令：/admin 修改余额 <用户ID> <金额>")
            return

        action, user_id, amount = args[1], args[2], int(args[3])
        if action == "修改余额":
            response = self.admin_modify_balance(admin_id, user_id, amount)
            update.message.reply_text(response)

    def message_handler(self, update: Update, context: CallbackContext):
        """ 捕获未识别的消息 """
        update.message.reply_text("不支持的命令，请使用 /start 获取帮助。")

    def draw(self, update: Update, context: CallbackContext):
        """ 获取并发送最新的开奖信息 """
        try:
            response = requests.get(LOTTERY_API_URL)
            data = response.json()
            draw_result = data.get("result", "无法获取开奖数据")
            update.message.reply_text(f"最新开奖信息：{draw_result}")
        except requests.exceptions.RequestException as e:
            update.message.reply_text(f"获取开奖信息失败: {str(e)}")


def main():
    """ 机器人入口函数 """
    updater = Updater(API_KEY, use_context=True)
    bot = LotteryBot(updater)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
