from telegram import Update
from telegram.ext import CallbackContext
from .database import get_balance, place_bet, update_balance
from .lhc_api import get_lhc_result

def start(update, context):
    update.message.reply_text("欢迎使用六和彩机器人！输入 /bet 来下注，输入 /balance 查询余额。")

def balance(update, context):
    user_id = update.message.from_user.id
    balance = get_balance(user_id)
    update.message.reply_text(f"你的余额是：{balance}元")

BETTING, WAITING_FOR_NUMBER, WAITING_FOR_AMOUNT = range(3)

def bet(update, context):
    update.message.reply_text("请输入你要下注的号码（例如：01, 12, 23）:")
    return WAITING_FOR_NUMBER

def handle_number(update, context):
    context.user_data['bet_number'] = update.message.text
    update.message.reply_text(f"你选择了号码 {update.message.text}，请输入下注金额:")
    return WAITING_FOR_AMOUNT

def handle_amount(update, context):
    bet_amount = update.message.text
    if bet_amount.isdigit() and int(bet_amount) > 0:
        bet_amount = int(bet_amount)
        user_id = update.message.from_user.id
        bet_number = context.user_data['bet_number']

        if place_bet(user_id, bet_number, bet_amount):
            update.message.reply_text(f"你已经成功下注！号码：{bet_number}，金额：{bet_amount}元。")
            return ConversationHandler.END
        else:
            update.message.reply_text("余额不足，无法下注。")
            return ConversationHandler.END
    else:
        update.message.reply_text("请输入一个有效的金额！")
        return WAITING_FOR_AMOUNT

def show_result(update, context):
    result = get_lhc_result()
    update.message.reply_text(f"六和彩开奖结果是：{result}")

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
            bonus = amount * 10
            current_balance = get_balance(user_id)
            update_balance(user_id, current_balance + bonus)
            context.bot.send_message(user_id, f"恭喜你！你中奖了！奖金：{bonus}元")
    else:
        update.message.reply_text("没有人中奖。")

    conn.close()

def cancel(update, context):
    update.message.reply_text("你已经取消下注。")
    return ConversationHandler.END

