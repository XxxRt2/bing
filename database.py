import sqlite3

# 初始化数据库并创建用户和下注表
def init_db():
    conn = sqlite3.connect('bets.db')
    cursor = conn.cursor()

    # 创建用户余额表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 1000  -- 每个用户初始化1000元余额
    )''')

    # 创建下注表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bets (
        user_id INTEGER,
        bet_number TEXT,
        bet_amount INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )''')

    conn.commit()
    conn.close()

# 获取用户余额
def get_balance(user_id):
    conn = sqlite3.connect('bets.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return 0  # 如果没有找到余额，则返回0

# 更新用户余额
def update_balance(user_id, new_balance):
    conn = sqlite3.connect('bets.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()

# 用户下注，扣除余额
def place_bet(user_id, bet_number, bet_amount):
    current_balance = get_balance(user_id)
    if current_balance >= bet_amount:
        # 扣除下注金额
        new_balance = current_balance - bet_amount
        update_balance(user_id, new_balance)

        # 将下注记录保存到数据库
        conn = sqlite3.connect('bets.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO bets (user_id, bet_number, bet_amount)
        VALUES (?, ?, ?)''', (user_id, bet_number, bet_amount))
        conn.commit()
        conn.close()
        return True
    else:
        return False  # 余额不足，下注失败
