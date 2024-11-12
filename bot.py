from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from .database import init_db, get_balance, update_balance, place_bet
from .lhc_api import get_lhc_result

# 启动命令
def start(update: Update, context: CallbackContext):
    update.message.reply_text("欢迎使用六和彩机器人！输入 /bet 来下注，输入 /balance 查询余额。")

# 查询余额
def balance(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    balance = get_balance(user_id)
    update.message.reply_text(f"你的余额是：{balance}元")

# 开始下注
BETTING, WAITING_FOR_NUMBER, WAITING_FOR_AMOUNT = range(3)

def bet(update: Update, context: CallbackContext):
    update.message.reply_text("请输入你要下注的号码（例如：01, 12, 23）:")
    return WAITING_FOR_NUMBER

def handle_number(update: Update, context: CallbackContext):
    context.user_data['bet_number'] = update.message.text
    update.message.reply_text(f"你选择了号码 {update.message.text}，请输入下注金额:")
    return WAITING_FOR_AMOUNT

def handle_amount(update: Update, context: CallbackContext):
    bet_amount = update.message.text
    if bet_amount.isdigit() and int(bet_amount) > 0:
        bet_amount = int(bet_amount)
        user_id = update.message.from_user.id
        bet_number = context.user_data['bet_number']

        # 检查余额并进行下注
        if place_bet(user_id, bet_number, bet_amount):
            update.message.reply_text(f"你已经成功下注！号码：{bet_number}，金额：{bet_amount}元。")
            return ConversationHandler.END
        else:
            update.message.reply_text("余额不足，无法下注。")
            return ConversationHandler.END
    else:
        update.message.reply_text("请输入一个有效的金额！")
        return WAITING_FOR_AMOUNT

# 显示开奖结果
def show_result(update: Update, context: CallbackContext):
    result = get_lhc_result()
    update.message.reply_text(f"六和彩开奖结果是：{result}")

    # 检查是否有用户中奖
    conn = sqlite3.connect('bets.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, bet_number, bet_amount FROM bets')
    bets = cursor.fetchall()

    winners = []
    for bet in bets:
        user_id, bet_number, bet_amount = bet
        if bet_number == result:
            winners.append((user_id, bet_amount))

    if winners:
        for winner in winners:
            user_id, amount = winner
            # 假设奖金为下注金额的10倍
            bonus = amount * 10
            current_balance = get_balance(user_id)
            update_balance(user_id, current_balance + bonus)
            context.bot.send_message(user_id, f"恭喜你！你中奖了！奖金：{bonus}元")
    else:
        update.message.reply_text("没有人中奖。")

    conn.close()

# 取消下注
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("你已经取消下注。")
    return ConversationHandler.END

