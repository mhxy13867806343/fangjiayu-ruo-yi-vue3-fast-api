from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr, validator
from pydantic.alias_generators import to_camel
from module_admin.annotation.pydantic_annotation import as_query


class H5UserBaseModel(BaseModel):
    """H5用户基础模型"""
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)


class H5UserPageQueryModel(H5UserBaseModel):
    """H5用户分页查询模型"""
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数")
    username: Optional[str] = Field(None, description="登录名")
    status: Optional[str] = Field(None, description="账号状态（0正常 1停用）")
    bind_type: Optional[str] = Field(None, description="绑定类型")
    pay_type: Optional[str] = Field(None, description="支付类型")
    date_range: Optional[List[str]] = Field(None, description="日期范围")
    begin_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")

    @classmethod
    def as_query(cls):
        from fastapi import Depends
        return Depends(as_query(cls))


class H5UserModel(H5UserBaseModel):
    """H5用户模型"""
    id: Optional[int] = Field(None, description="用户ID")
    user_id: Optional[str] = Field(None, description="用户唯一标识符")
    username: str = Field(..., description="登录名")
    nickname: str = Field(..., description="用户昵称")
    password: Optional[str] = Field(None, description="密码")
    email: Optional[str] = Field(None, description="用户邮箱")
    phone: Optional[str] = Field(None, description="手机号码")
    avatar: Optional[str] = Field(None, description="头像地址")
    status: Optional[str] = Field("0", description="帐号状态（0正常 1停用）")
    bind_type: Optional[str] = Field(None, description="绑定类型")
    pay_type: Optional[str] = Field(None, description="支付类型")
    exp_points: Optional[int] = Field(0, description="经验值")
    level: Optional[int] = Field(1, description="用户等级")
    level_name: Optional[str] = Field("小鸡出壳", description="等级名称")
    checkin_days: Optional[int] = Field(0, description="签到天数")
    continuous_checkin_days: Optional[int] = Field(0, description="连续签到天数")
    last_checkin_date: Optional[datetime] = Field(None, description="最后签到日期")
    mood: Optional[str] = Field(None, description="心情")
    remark: Optional[str] = Field(None, description="备注")

    @validator('email', pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class H5UserDetailModel(BaseModel):
    """H5用户详情模型"""
    id: Optional[int] = None  # 用于存储数据库的整数ID
    user_id: Optional[str] = None  # 用于存储生成的字符串ID
    username: Optional[str] = Field(None, description="登录名")
    nickname: Optional[str] = Field(None, description="用户昵称")
    password: Optional[str] = Field(None, description="密码")
    email: Optional[str] = Field(None, description="用户邮箱")
    phone: Optional[str] = Field(None, description="手机号码")
    avatar: Optional[str] = Field(None, description="头像地址")
    status: Optional[str] = Field(None, description="帐号状态（0正常 1停用）")
    bind_type: Optional[str] = Field(None, description="绑定类型（如微信、github等）")
    pay_type: Optional[str] = Field(None, description="支付类型")
    exp_points: Optional[int] = Field(0, description="经验值")
    level: Optional[int] = Field(1, description="用户等级")
    level_name: Optional[str] = Field("小鸡出壳", description="等级名称")
    checkin_days: Optional[int] = Field(0, description="签到天数")
    continuous_checkin_days: Optional[int] = Field(0, description="连续签到天数")
    last_checkin_date: Optional[datetime] = Field(None, description="最后签到日期")
    mood: Optional[str] = Field(None, description="心情")
    remark: Optional[str] = Field(None, description="备注")
    register_time: Optional[datetime] = Field(None, description="注册时间")
    login_ip: Optional[str] = Field(None, description="最后登录IP")
    login_date: Optional[datetime] = Field(None, description="最后登录时间")
    register_days: Optional[int] = Field(0, description="注册天数")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    @validator('id', pre=True)
    def validate_id(cls, v):
        if v is not None:
            return int(v)
        return v

    @validator('user_id', pre=True)
    def validate_user_id(cls, v):
        if v is not None:
            return str(v)
        return v


class H5UserRegisterModel(BaseModel):
    """H5用户注册模型"""
    username: str = Field(..., description="登录名")
    nickname: Optional[str] = Field(None, description="用户昵称")
    password: str = Field(..., description="密码")
    email: Optional[str] = Field(None, description="用户邮箱")
    phone: Optional[str] = Field(None, description="手机号码")
    avatar: Optional[str] = Field(None, description="头像地址")
    status: Optional[str] = Field("0", description="帐号状态（0正常 1停用）")
    bind_type: Optional[str] = Field(None, description="绑定类型（如微信、github等）")
    pay_type: Optional[str] = Field(None, description="支付类型")
    
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)


class H5UserLoginModel(H5UserBaseModel):
    """H5用户登录模型"""
    username: str = Field(..., description="登录名")
    password: str = Field(..., description="密码")
    code: Optional[str] = Field(None, description="验证码")
    uuid: Optional[str] = Field(None, description="唯一标识")


class H5UserPasswordResetModel(H5UserBaseModel):
    """H5用户密码重置模型"""
    username: str = Field(..., description="登录名")
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    phone: Optional[str] = Field(None, description="手机号码")
    code: str = Field(..., description="验证码")
    password: str = Field(..., description="新密码")


class H5UserCheckinModel(H5UserBaseModel):
    """H5用户签到模型"""
    user_id: int = Field(..., description="用户ID")
    checkin_date: datetime = Field(..., description="签到日期")
    exp_gained: int = Field(10, description="获得的经验值")


class H5UserMoodModel(H5UserBaseModel):
    """H5用户心情模型"""
    id: Optional[int] = Field(None, description="记录ID")
    user_id: int = Field(..., description="用户ID")
    content: str = Field(..., description="心情内容")
    status: str = Field("0", description="状态（0公开 1私有）")


class H5UserMoodCommentModel(H5UserBaseModel):
    """H5用户心情评论模型"""
    id: Optional[int] = Field(None, description="记录ID")
    mood_id: int = Field(..., description="心情ID")
    user_id: int = Field(..., description="评论用户ID")
    content: str = Field(..., description="评论内容")
    parent_id: int = Field(0, description="父评论ID，0表示一级评论")


class H5UserThirdPartyModel(H5UserBaseModel):
    """H5用户第三方绑定模型"""
    id: Optional[int] = Field(None, description="记录ID")
    user_id: int = Field(..., description="用户ID")
    platform: str = Field(..., description="平台（如微信、github等）")
    open_id: str = Field(..., description="第三方平台用户唯一标识")


class H5UserPaymentModel(H5UserBaseModel):
    """H5用户支付记录模型"""
    id: Optional[int] = Field(None, description="记录ID")
    user_id: int = Field(..., description="用户ID")
    order_no: str = Field(..., description="订单号")
    amount: int = Field(..., description="支付金额（分）")
    pay_type: str = Field(..., description="支付类型")
    status: str = Field("0", description="状态（0未支付 1已支付 2已取消）")
    qrcode_url: Optional[str] = Field(None, description="二维码URL")
    expire_time: Optional[datetime] = Field(None, description="过期时间")


class DeleteH5UserModel(H5UserBaseModel):
    """删除H5用户模型"""
    user_ids: str = Field(..., description="用户ID字符串，多个以逗号分隔")


class ChangeH5UserStatusModel(BaseModel):
    """修改H5用户状态模型"""
    user_id: str = Field(..., description="用户ID")
    status: str = Field(..., description="账号状态（0正常 1停用）")

    model_config = ConfigDict(from_attributes=True)
