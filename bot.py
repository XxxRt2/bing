import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import ADMIN_USER_ID, odds, zodiac_map

# 初始化用户余额和下注记录
user_balances = {}
user_bets = {}

# 更新用户余额
def update_balance(user_id, amount):
    if user_id not in user_balances:
        user_balances[user_id] = 0
    user_balances[user_id] += amount

# 获取用户余额
def get_balance(user_id):
    return user_balances.get(user_id, 0)

# 下注处理函数
def bet(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = update.message.text

    # 检查下注格式
    parts = message.split()
    if len(parts) < 2:
        update.message.reply_text("请输入有效的下注格式！例如：'特码01押100'")
        return

    bet_type = parts[0]
    amount = int(parts[1])

    # 下注处理
    if bet_type.startswith("特码"):
        numbers = list(map(int, parts[0][2:].split()))  # 解析特码下注号码
        add_bet(user_id, '特码', numbers, amount)
        update.message.reply_text(f"下注成功！下注类型：特码，号码：{numbers}，金额：{amount}")
    elif bet_type.startswith("特肖"):
        zodiac = parts[0][2:]
        add_bet(user_id, '特肖', zodiac, amount)
        update.message.reply_text(f"下注成功！下注类型：特肖，生肖：{zodiac}，金额：{amount}")
    elif bet_type.startswith("波色"):
        wave_color = parts[0]
        add_bet(user_id, '波色', wave_color, amount)
        update.message.reply_text(f"下注成功！下注类型：波色，颜色：{wave_color}，金额：{amount}")
    else:
        update.message.reply_text("未识别的下注类型！")

# 添加下注记录
def add_bet(user_id, bet_type, selection, amount):
    if user_id not in user_bets:
        user_bets[user_id] = []
    user_bets[user_id].append({'玩法': bet_type, '号码': selection, '金额': amount})

# 结算函数
def settle_bets(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    draw_result = random.sample(range(1, 50), 7)  # 模拟开奖结果
    winning_amount = 0

    # 检查用户下注并计算获奖金额
    winnings_special_code = check_special_code_winning(draw_result, user_id)
    winnings_zodiac = check_zodiac_winning(draw_result, user_id)
    winnings_wave = check_wave_winning(draw_result, user_id)

    winning_amount += winnings_special_code + winnings_zodiac + winnings_wave

    # 更新余额
    update_balance(user_id, winning_amount)

    # 返回结算信息
    update.message.reply_text(f"开奖结果：{draw_result}\n您总共赢得：{winning_amount} 元！")
    user_bets[user_id] = []  # 清空下注记录

# 检查特码中奖
def check_special_code_winning(draw_result, user_id):
    winnings = 0
    for bet in user_bets.get(user_id, []):
        if bet['玩法'] == '特码':
            if any(num in draw_result for num in bet['号码']):
                winnings += bet['金额'] * odds['特码']
    return winnings

# 检查特肖中奖
def check_zodiac_winning(draw_result, user_id):
    winnings = 0
    for bet in user_bets.get(user_id, []):
        if bet['玩法'] == '特肖':
            if bet['生肖'] in draw_result:
                winnings += bet['金额'] * odds['特肖不带龙']
    return winnings

# 检查波色中奖
def check_wave_winning(draw_result, user_id):
    winnings = 0
    for bet in user_bets.get(user_id, []):
        if bet['玩法'] == '波色':
            wave = bet['号码']
            if wave in draw_result:
                winnings += bet['金额'] * odds['波色'][wave]
    return winnings

# 查看余额
def balance(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    update.message.reply_text(f"您的当前余额为：{get_balance(user_id)} 元")

# 设置用户余额（管理员命令）
def set_balance(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != ADMIN_USER_ID:
        update.message.reply_text("您没有权限执行此操作！")
        return

    if len(context.args) != 2:
        update.message.reply_text("命令格式错误！正确格式：/set_balance <user_id> <amount>")
        return

    target_user_id = int(context.args[0])
    amount = int(context.args[1])

    update_balance(target_user_id, amount)
    update.message.reply_text(f"管理员已成功调整用户 {target_user_id} 的余额：{amount}")
    context.bot.send_message(target_user_id, f"您的余额已被管理员修改，当前余额为：{get_balance(target_user_id)} 元。")

# 启动命令
def start(update: Update, context: CallbackContext):
    update.message.reply_text("欢迎来到六合彩！使用以下命令进行下注和结算:\n"
                              "/settle - 结算开奖并结算下注\n"
                              "/balance - 查看余额\n"
                              "/set_balance <user_id> <amount> - 管理员修改用户余额")

# 主函数
def main():
    # 用自己的 API Token 替换 'YOUR_TOKEN'
    updater = Updater("YOUR_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # 添加命令处理程序
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("settle", settle_bets))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("set_balance", set_balance, pass_args=True))

    # 添加消息处理程序
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, bet))

    # 启动 Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

