# 模拟数据库存储用户余额（可以扩展为实际数据库存储）
user_balances = {}

def get_user_balance(user_id):
    """获取用户余额"""
    return user_balances.get(user_id, 1000)  # 默认给用户1000余额

def update_user_balance(user_id, new_balance):
    """更新用户余额"""
    user_balances[user_id] = new_balance
