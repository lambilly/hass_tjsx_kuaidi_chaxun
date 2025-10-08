"""Constants for the TJSX Kuaidi Chaxun integration."""

DOMAIN = "tjsx_kuaidi_chaxun"
CONF_API_KEY = "api_key"
CONF_EXPRESS_NUMBER = "express_number"
CONF_EXPRESS_NAME = "express_name"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 12  # hours

# API Configuration
API_URL = "https://apis.tianapi.com/kuaidi/index"

# 更新状态码映射
STATUS_MAP = {
    0: '无记录',
    1: '揽件',
    2: '在途中',
    3: '派送中',
    4: '已签收',
    5: '用户拒签',
    6: '疑难件',
    7: '无效单',
    8: '超时单',
    9: '签收失败',
    10: '退回',
    11: '转投',
    12: '待签'
}