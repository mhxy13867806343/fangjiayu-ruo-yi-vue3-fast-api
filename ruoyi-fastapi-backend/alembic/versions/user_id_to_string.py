"""user_id to string

Revision ID: user_id_to_string
Revises: 
Create Date: 2025-03-26 19:55:35

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import random
import string


# revision identifiers, used by Alembic.
revision = 'user_id_to_string'
down_revision = None
branch_labels = None
depends_on = None


def generate_user_id() -> str:
    """
    生成字母加数字组成的30个字符的用户ID
    """
    letters = string.ascii_letters  # 包含大小写字母
    digits = string.digits  # 包含数字
    
    # 确保至少包含一个字母和一个数字
    first_char = random.choice(letters)
    second_char = random.choice(digits)
    
    # 剩余的28个字符从字母和数字中随机选择
    remaining_chars = ''.join(random.choices(letters + digits, k=28))
    
    # 组合并随机打乱顺序
    chars = first_char + second_char + remaining_chars
    chars_list = list(chars)
    random.shuffle(chars_list)
    
    return ''.join(chars_list)


def upgrade():
    # 创建临时表
    op.create_table(
        'h5_user_temp',
        sa.Column('user_id', sa.String(30), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('nickname', sa.String(50), nullable=False),
        sa.Column('password', sa.String(100), nullable=False),
        sa.Column('email', sa.String(50), server_default=''),
        sa.Column('phone', sa.String(11), server_default=''),
        sa.Column('avatar', sa.String(255), server_default=''),
        sa.Column('status', sa.String(1), server_default='0'),
        sa.Column('bind_type', sa.String(20), server_default=''),
        sa.Column('pay_type', sa.String(20), server_default=''),
        sa.Column('register_time', sa.DateTime),
        sa.Column('exp_points', sa.Integer, server_default='0'),
        sa.Column('level', sa.Integer, server_default='1'),
        sa.Column('level_name', sa.String(50), server_default='初级会员'),
        sa.Column('checkin_days', sa.Integer, server_default='0'),
        sa.Column('continuous_checkin_days', sa.Integer, server_default='0'),
        sa.Column('last_checkin_date', sa.DateTime),
        sa.Column('mood', sa.String(255)),
        sa.Column('remark', sa.String(500)),
        sa.Column('login_ip', sa.String(50)),
        sa.Column('login_date', sa.DateTime),
        sa.Column('create_time', sa.DateTime),
        sa.Column('update_time', sa.DateTime),
    )
    
    # 获取所有用户数据
    connection = op.get_bind()
    users = connection.execute('SELECT * FROM h5_user').fetchall()
    
    # 将数据插入临时表，并为每个用户生成新的字符串ID
    for user in users:
        user_dict = dict(user)
        old_user_id = user_dict['user_id']
        new_user_id = generate_user_id()
        
        # 更新用户ID
        user_dict['user_id'] = new_user_id
        
        # 构建插入语句
        columns = ', '.join(user_dict.keys())
        placeholders = ', '.join(['%s'] * len(user_dict))
        sql = f"INSERT INTO h5_user_temp ({columns}) VALUES ({placeholders})"
        
        # 执行插入
        connection.execute(sql, list(user_dict.values()))
        
        # 更新关联表中的user_id
        tables = ['h5_user_checkin', 'h5_user_mood', 'h5_user_mood_comment', 
                 'h5_user_third_party', 'h5_user_payment']
        
        for table in tables:
            connection.execute(
                f"UPDATE {table} SET user_id = '{new_user_id}' WHERE user_id = {old_user_id}"
            )
    
    # 删除原表
    op.drop_table('h5_user')
    
    # 重命名临时表为原表名
    op.rename_table('h5_user_temp', 'h5_user')
    
    # 修改关联表中的user_id列类型
    tables = ['h5_user_checkin', 'h5_user_mood', 'h5_user_mood_comment', 
             'h5_user_third_party', 'h5_user_payment']
    
    for table in tables:
        op.alter_column(
            table, 'user_id',
            existing_type=sa.Integer(),
            type_=sa.String(30),
            existing_nullable=False
        )


def downgrade():
    # 此迁移不支持回滚，因为字符串ID无法可靠地转换回整数ID
    pass
