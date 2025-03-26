from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from config.database import Base


class H5User(Base):
    """
    H5用户信息表
    """

    __tablename__ = 'h5_user'

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(50), nullable=False, unique=True, comment='登录名')
    nickname = Column(String(50), nullable=False, comment='用户昵称')
    password = Column(String(100), nullable=False, comment='密码')
    email = Column(String(50), default='', comment='用户邮箱')
    phone = Column(String(11), default='', comment='手机号码')
    avatar = Column(String(255), default='', comment='头像地址')
    status = Column(String(1), default='0', comment='帐号状态（0正常 1停用）')
    bind_type = Column(String(20), default='', comment='绑定类型（如微信、github等）')
    pay_type = Column(String(20), default='', comment='支付类型')
    login_ip = Column(String(128), default='', comment='最后登录IP')
    login_date = Column(DateTime, comment='最后登录时间')
    register_time = Column(DateTime, comment='注册时间', default=datetime.now)
    exp_points = Column(Integer, default=0, comment='经验值')
    level = Column(Integer, default=1, comment='用户等级')
    level_name = Column(String(50), default='小鸡出壳', comment='等级名称')
    checkin_days = Column(Integer, default=0, comment='签到天数')
    continuous_checkin_days = Column(Integer, default=0, comment='连续签到天数')
    last_checkin_date = Column(DateTime, comment='最后签到日期')
    mood = Column(String(50), default='', comment='心情')
    del_flag = Column(String(1), default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now)
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, comment='更新时间', default=datetime.now)
    remark = Column(String(500), default=None, comment='备注')


class H5UserCheckin(Base):
    """
    H5用户签到记录表
    """

    __tablename__ = 'h5_user_checkin'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = Column(Integer, ForeignKey('h5_user.user_id'), nullable=False, comment='用户ID')
    checkin_date = Column(DateTime, nullable=False, comment='签到日期')
    exp_gained = Column(Integer, default=10, comment='获得的经验值')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now)


class H5UserMood(Base):
    """
    H5用户心情表
    """

    __tablename__ = 'h5_user_mood'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = Column(Integer, ForeignKey('h5_user.user_id'), nullable=False, comment='用户ID')
    content = Column(String(255), nullable=False, comment='心情内容')
    status = Column(String(1), default='0', comment='状态（0公开 1私有）')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now)
    update_time = Column(DateTime, comment='更新时间', default=datetime.now)


class H5UserMoodComment(Base):
    """
    H5用户心情评论表
    """

    __tablename__ = 'h5_user_mood_comment'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    mood_id = Column(Integer, ForeignKey('h5_user_mood.id'), nullable=False, comment='心情ID')
    user_id = Column(Integer, ForeignKey('h5_user.user_id'), nullable=False, comment='评论用户ID')
    content = Column(String(255), nullable=False, comment='评论内容')
    parent_id = Column(Integer, default=0, comment='父评论ID，0表示一级评论')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now)
    update_time = Column(DateTime, comment='更新时间', default=datetime.now)


class H5UserThirdParty(Base):
    """
    H5用户第三方绑定表
    """

    __tablename__ = 'h5_user_third_party'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = Column(Integer, ForeignKey('h5_user.user_id'), nullable=False, comment='用户ID')
    platform = Column(String(20), nullable=False, comment='平台（如微信、github等）')
    open_id = Column(String(100), nullable=False, comment='第三方平台用户唯一标识')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now)
    update_time = Column(DateTime, comment='更新时间', default=datetime.now)


class H5UserPayment(Base):
    """
    H5用户支付记录表
    """

    __tablename__ = 'h5_user_payment'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = Column(Integer, ForeignKey('h5_user.user_id'), nullable=False, comment='用户ID')
    order_no = Column(String(50), nullable=False, unique=True, comment='订单号')
    amount = Column(Integer, nullable=False, comment='支付金额（分）')
    pay_type = Column(String(20), nullable=False, comment='支付类型')
    status = Column(String(1), default='0', comment='状态（0未支付 1已支付 2已取消）')
    qrcode_url = Column(String(255), default='', comment='二维码URL')
    expire_time = Column(DateTime, comment='过期时间')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now)
    update_time = Column(DateTime, comment='更新时间', default=datetime.now)
