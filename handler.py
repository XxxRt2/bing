import re
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CallbackContext
from models import get_user_balance, update_user_balance

# 赔率设置
odds = {
    '特码': 47,
    '特肖': {'带龙': 9.5, '不带龙': 11.7},
    '波色': {'红波': 2.75, '蓝波': 2.98, '绿波': 2.98},
    '不中': {'五不中': 2, '六不中': 2.5, '七不中': 3, '八不中': 3.5, '九不中': 4, '十不中': 5},
    '平特肖': {'带龙': {'一肖': 1.8, '二连肖': 3.5, '三连肖': 8.5, '四连肖': 31, '五连肖': 90}, 
              '不带龙': {'一肖': 2.1, '二连肖': 4.5, '三连肖': 12.5, '四连肖': 36, '五连肖': 100}}
}

def get_draw_times():
    """返回封盘时间和开奖时间"""
    now = datetime.now()
    close_time = now + timedelta(minutes=5)  # 假设封盘时间在5分钟后
    draw_time = close_time + timedelta(minutes=5)  # 开奖时间在封盘后5分钟
    return close_time.strftime('%H:%M:%S'), draw_time.strftime('%H:%M:%S')

def get_current_period():
    """生成当前期号"""
    now = datetime.now()
    # 用日期和时间生成期号
    return now.strftime('%Y%m%d%H%M')  # 格式为：年-月-日-小时-分钟

def start(update: Update, context: CallbackContext):
    """处理 /start 命令"""
    update.message.reply_text('欢迎使用六合彩投注机器人！\n请输入您的投注信息')

def handle_bet(update: Update, context: CallbackContext):
    bet_message = update.message.text.strip()
    user_id = update.message.from_user.id
    
    # 获取用户余额
    balance = get_user_balance(user_id)
    
    # 使用正则表达式提取下注内容
    bet_pattern = re.compile(r'(\S+)\s*(.*?)\s*(押|@)\s*(\d+)', re.IGNORECASE)
    match = bet_pattern.match(bet_message)

    if not match:
        update.message.reply_text("下注格式错误，请使用以下格式：\n<玩法> <选项>押<金额>")
        return

    game_type = match.group(1).lower()
    bet_options = match.group(2).strip()
    bet_amount = int(match.group(4))

    # 检查余额
    if bet_amount > balance:
        update.message.reply_text(f"余额不足，当前余额: {balance}")
        return
    
    # 获取封盘时间和开奖时间
    close_time, draw_time = get_draw_times()

    # 获取当前期号
    current_period = get_current_period()

    # 下注内容提醒
    reminder_message = (
        f"第{current_period}期\n"
        f"封盘时间：{close_time}\n"
        f"开奖时间：{draw_time}\n"
        f"下注内容：\n"
        f"玩法：{game_type}，选项：{bet_options}，金额：{bet_amount}\n"
        "------------\n"
        f"余额：{balance - bet_amount}"
    )
    
    # 处理下注
    if game_type == '特码':
        # 处理特码玩法
        if bet_options and bet_amount > 0:
            update_message = reminder_message
            update.message.reply_text(update_message)
        else:
            update.message.reply_text("特码下注格式错误")
        
    elif game_type == '特肖':
        # 处理特肖玩法
        if bet_options and bet_amount > 0:
            update_message = reminder_message
            update.message.reply_text(update_message)
        else:
            update.message.reply_text("特肖下注格式错误")
        
    elif game_type == '波色':
        # 处理波色玩法
        if bet_options in odds['波色'] and bet_amount > 0:
            update_message = reminder_message
            update.message.reply_text(update_message)
        else:
            update.message.reply_text("波色下注格式错误")
        
    elif game_type == '不中':
        # 处理不中玩法
        if bet_options and bet_amount > 0:
            update_message = reminder_message
            update.message.reply_text(update_message)
        else:
            update.message.reply_text("不中下注格式错误")
        
    elif game_type == '平特肖':
        # 处理平特肖玩法
        if bet_options and bet_amount > 0:
            update_message = reminder_message
            update.message.reply_text(update_message)
        else:
            update.message.reply_text("平特肖下注格式错误")
        
    else:
        update.message.reply_text(f"无效玩法：{game_type}")

    # 更新用户余额
    update_user_balance(user_id, balance - bet_amount)
