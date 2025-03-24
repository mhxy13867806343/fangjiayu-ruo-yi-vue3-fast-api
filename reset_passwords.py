import sys
import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# 添加项目根目录到Python路径
sys.path.append('/Users/hooksvue/Desktop/RuoYi-Vue3-FastAP/ruoyi-fastapi-backend')

# 导入项目中的密码工具类
from utils.pwd_util import PwdUtil

# 数据库连接信息
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "ruoyi-fastapi"

# 创建数据库连接
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)

async def reset_passwords():
    # 生成密码哈希
    admin_password = PwdUtil.get_password_hash("admin123")
    user_password = PwdUtil.get_password_hash("123456")
    
    print(f"Admin密码哈希: {admin_password}")
    print(f"用户密码哈希: {user_password}")
    
    # 更新数据库中的密码
    async with engine.begin() as conn:
        # 更新admin用户密码
        await conn.execute(
            text("UPDATE sys_user SET password = :password WHERE user_name = 'admin'"),
            {"password": admin_password}
        )
        print("已更新admin用户密码")
        
        # 更新其他用户密码
        await conn.execute(
            text("UPDATE sys_user SET password = :password WHERE user_name IN ('test1', 'test2', 'dev1', 'dev2')"),
            {"password": user_password}
        )
        print("已更新其他用户密码")

if __name__ == "__main__":
    asyncio.run(reset_passwords())
