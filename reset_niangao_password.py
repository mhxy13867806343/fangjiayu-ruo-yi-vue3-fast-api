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

async def reset_password():
    # 生成密码哈希
    password_hash = PwdUtil.get_password_hash("123456")
    
    print(f"密码哈希: {password_hash}")
    
    # 更新数据库中的密码
    async with engine.begin() as conn:
        # 更新niangao用户密码
        await conn.execute(
            text("UPDATE sys_user SET password = :password WHERE user_name = 'niangao'"),
            {"password": password_hash}
        )
        print("已更新niangao用户密码为123456")

if __name__ == "__main__":
    asyncio.run(reset_password())
