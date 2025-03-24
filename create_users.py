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

async def create_users():
    # 生成密码哈希
    password_hash = PwdUtil.get_password_hash("123456")
    
    print(f"密码哈希: {password_hash}")
    
    # 创建用户数据
    users = [
        {
            "user_name": "test1",
            "nick_name": "测试用户1",
            "password": password_hash,
            "dept_id": 108,  # 测试部门
            "status": "0",
            "del_flag": "0",
            "create_by": "admin",
            "remark": "测试账号"
        },
        {
            "user_name": "test2",
            "nick_name": "测试用户2",
            "password": password_hash,
            "dept_id": 108,  # 测试部门
            "status": "0",
            "del_flag": "0",
            "create_by": "admin",
            "remark": "测试账号"
        },
        {
            "user_name": "dev1",
            "nick_name": "开发人员1",
            "password": password_hash,
            "dept_id": 105,  # 研发部门
            "status": "0",
            "del_flag": "0",
            "create_by": "admin",
            "remark": "开发账号"
        },
        {
            "user_name": "dev2",
            "nick_name": "开发人员2",
            "password": password_hash,
            "dept_id": 105,  # 研发部门
            "status": "0",
            "del_flag": "0",
            "create_by": "admin",
            "remark": "开发账号"
        }
    ]
    
    async with engine.begin() as conn:
        # 插入用户数据
        for user in users:
            await conn.execute(
                text("""
                INSERT INTO sys_user (user_name, nick_name, password, dept_id, 
                                     email, phonenumber, sex, avatar, status, del_flag, 
                                     login_ip, create_by, create_time, remark)
                VALUES (:user_name, :nick_name, :password, :dept_id, 
                        '', '', '0', '', :status, :del_flag, 
                        '127.0.0.1', :create_by, NOW(), :remark)
                """),
                user
            )
            print(f"已创建用户: {user['user_name']}")
        
        # 获取新创建的用户ID
        result = await conn.execute(text(
            "SELECT user_id, user_name FROM sys_user WHERE user_name IN ('test1', 'test2', 'dev1', 'dev2')"
        ))
        users = result.fetchall()
        
        # 为用户分配角色
        for user in users:
            user_id = user[0]
            user_name = user[1]
            
            # 根据用户名确定角色ID
            role_id = 3 if user_name.startswith('test') else 4  # test用户->测试角色(3), dev用户->开发角色(4)
            
            await conn.execute(
                text("INSERT INTO sys_user_role (user_id, role_id) VALUES (:user_id, :role_id)"),
                {"user_id": user_id, "role_id": role_id}
            )
            print(f"已为用户 {user_name} 分配角色ID: {role_id}")

if __name__ == "__main__":
    asyncio.run(create_users())
