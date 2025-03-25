#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加 detail 字段到 sys_carousel 表
"""
import asyncio
import aiomysql
from config.env import DataBaseConfig

async def add_detail_column():
    """
    添加 detail 字段到 sys_carousel 表
    """
    # 创建数据库连接
    conn = await aiomysql.connect(
        host=DataBaseConfig.db_host,
        port=DataBaseConfig.db_port,
        user=DataBaseConfig.db_username,
        password=DataBaseConfig.db_password,
        db=DataBaseConfig.db_database
    )
    
    # 创建游标
    async with conn.cursor() as cursor:
        # 检查字段是否已存在
        check_sql = """
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'sys_carousel' 
        AND COLUMN_NAME = 'detail'
        """
        await cursor.execute(check_sql, (DataBaseConfig.db_database,))
        result = await cursor.fetchone()
        
        if result[0] == 0:
            # 添加字段
            alter_sql = """
            ALTER TABLE sys_carousel 
            ADD COLUMN detail TEXT NULL COMMENT '详情内容' 
            AFTER end_time
            """
            await cursor.execute(alter_sql)
            print("成功添加 detail 字段到 sys_carousel 表")
        else:
            print("detail 字段已存在于 sys_carousel 表中")
    
    # 提交事务
    await conn.commit()
    # 关闭连接
    conn.close()

if __name__ == "__main__":
    asyncio.run(add_detail_column())
