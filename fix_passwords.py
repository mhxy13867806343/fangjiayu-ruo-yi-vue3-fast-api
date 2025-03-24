import sys
import os

# 添加项目根目录到Python路径
sys.path.append('/Users/hooksvue/Desktop/RuoYi-Vue3-FastAP/ruoyi-fastapi-backend')

# 导入项目中的密码工具类
from utils.pwd_util import PwdUtil

# 生成加密密码
admin_password = PwdUtil.get_password_hash('admin')
user_password = PwdUtil.get_password_hash('123456')

print(f"Admin密码加密结果: {admin_password}")
print(f"用户密码加密结果: {user_password}")
