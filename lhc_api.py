import requests

# 获取六和彩开奖结果
def get_lhc_result():
    try:
        # 假设API URL为
        LHC_API_URL = "https://api.example.com/lottery/6hc"  # 替换为实际API URL
        response = requests.get(LHC_API_URL)
        data = response.json()
        return data["result"]
    except Exception as e:
        return "获取开奖结果失败，请稍后再试。"
