import random
import string
import time
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.get_db import get_db
from config.get_redis import RedisUtil
from module_h5.entity.do.user_do import H5User, H5UserCheckin, H5UserMood, H5UserMoodComment, H5UserThirdParty, H5UserPayment
from module_h5.entity.vo.user_vo import H5UserModel, H5UserPageQueryModel, H5UserDetailModel, H5UserRegisterModel
from utils.page_util import PageResponseModel, PageUtil

class H5UserService:
    """H5用户服务"""

    # 用户等级配置
    LEVEL_CONFIG = {
        1: {"name": "小鸡出壳", "exp": 0},
        2: {"name": "江湖小虾", "exp": 100},
        3: {"name": "练气弟子", "exp": 300},
        4: {"name": "筑基修士", "exp": 600},
        5: {"name": "金丹真人", "exp": 1000},
        6: {"name": "元婴大能", "exp": 1500},
        7: {"name": "化神宗师", "exp": 2100}
    }
    
    # Redis键前缀
    REDIS_CHECKIN_KEY = "h5:user:checkin:"
    REDIS_VERIFY_CODE_KEY = "h5:user:verify_code:"
    REDIS_EMAIL_CODE_KEY = "h5:user:email_code:"
    REDIS_PAYMENT_KEY = "h5:user:payment:"
    
    @staticmethod
    def generate_string_id() -> str:
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
    
    @staticmethod
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
    
    @classmethod
    async def get_user_list(
        cls, 
        query: H5UserPageQueryModel, 
        db: AsyncSession = Depends(get_db)
    ) -> Tuple[List[H5UserDetailModel], int]:
        """
        获取用户列表
        """
        # 构建查询条件
        conditions = []
        if query.username:
            conditions.append(H5User.username.like(f"%{query.username}%"))
        if query.status:
            conditions.append(H5User.status == query.status)
        if query.bind_type:
            conditions.append(H5User.bind_type == query.bind_type)
        if query.pay_type:
            conditions.append(H5User.pay_type == query.pay_type)
        if query.begin_time and query.end_time:
            conditions.append(
                and_(
                    H5User.register_time >= datetime.strptime(query.begin_time, "%Y-%m-%d"),
                    H5User.register_time <= datetime.strptime(query.end_time, "%Y-%m-%d") + timedelta(days=1)
                )
            )
        
        # 查询总数
        count_stmt = select(func.count(H5User.user_id)).where(and_(*conditions))
        total = await db.scalar(count_stmt)
        
        # 分页查询
        stmt = (
            select(H5User)
            .where(and_(*conditions))
            .order_by(desc(H5User.create_time))
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        # 转换为DTO
        user_list = []
        for user in users:
            user_dto = H5UserDetailModel.model_validate(user)
            
            # 设置id字段为数据库的user_id值
            user_dto.id = user.user_id
            
            # 生成字符串格式的用户ID
            string_id = cls.generate_string_id_from_int(user.user_id)
            user_dto.user_id = string_id
            
            # 计算注册天数
            if user.register_time:
                delta = datetime.now() - user.register_time
                user_dto.register_days = delta.days
                # 确保register_time字段被赋值
                user_dto.register_time = user.register_time
            # 确保create_time字段被赋值
            if user.create_time:
                user_dto.create_time = user.create_time
            # 手机号脱敏
            if user.phone and len(user.phone) == 11:
                user_dto.phone = user.phone[:3] + "****" + user.phone[-4:]
            # 在应用层处理身份证号
            user_dto.id_card = ""  # 默认为空字符串
            user_list.append(user_dto)
        
        return user_list, total
    
    @classmethod
    async def get_user_by_id(
        cls, 
        user_id: int, 
        db: AsyncSession = Depends(get_db)
    ) -> Optional[H5UserDetailModel]:
        """
        根据ID获取用户
        """
        stmt = select(H5User).where(H5User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return None
        
        # 转换为DTO
        user_dto = H5UserDetailModel.model_validate(user)
        
        # 设置id字段为数据库的user_id值
        user_dto.id = user.user_id
        
        # 生成字符串格式的用户ID
        string_id = cls.generate_string_id_from_int(user.user_id)
        user_dto.user_id = string_id
        
        # 计算注册天数
        if user.register_time:
            delta = datetime.now() - user.register_time
            user_dto.register_days = delta.days
            # 确保register_time字段被赋值
            user_dto.register_time = user.register_time
        # 确保create_time字段被赋值
        if user.create_time:
            user_dto.create_time = user.create_time
        
        # 手机号脱敏
        if user.phone and len(user.phone) == 11:
            user_dto.phone = user.phone[:3] + "****" + user.phone[-4:]
        # 在应用层处理身份证号
        user_dto.id_card = ""  # 默认为空字符串
        
        return user_dto
    
    @classmethod
    async def get_user_detail(
        cls, 
        user_id: str, 
        db: AsyncSession = Depends(get_db),
            request: Request = None
    ) -> Optional[H5UserDetailModel]:
        """
        根据ID获取用户详情，支持整数ID和字符串ID
        """
        user = None
        # 尝试将用户ID转换为整数
        try:
            user_id_int = int(user_id)
            # 如果成功转换为整数，则使用整数ID查询
            user = await cls.get_user_by_id(user_id_int, db)
        except ValueError:
            # 如果无法转换为整数，则使用字符串ID查询
            user = await cls.find_user_by_string_id(user_id, db)
            
        return user
    
    @classmethod
    async def create_user(
        cls,
        user: H5UserModel,
        request: Request = None,
        db: AsyncSession = Depends(get_db)
    ) -> H5UserDetailModel:
        """
        创建用户
        """
        print(f"service层创建用户，用户数据: {user.dict()}")
        
        # 检查用户名是否存在
        stmt = select(H5User).where(H5User.username == user.username)
        result = await db.execute(stmt)
        if result.scalars().first():
            print(f"用户名已存在: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 生成随机昵称
        if not user.nickname:
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.nickname = f"{user.username}_{random_suffix}"
            print(f"生成随机昵称: {user.nickname}")
        
        # 获取用户IP地址
        client_ip = cls.get_client_ip(request)
        
        # 创建用户（不指定user_id，让数据库自动生成）
        new_user = H5User(
            username=user.username,
            nickname=user.nickname,
            password=user.password,  # 实际应用中需要加密
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            status=user.status,
            bind_type=user.bind_type,
            pay_type=user.pay_type,
            login_ip=client_ip,  # 设置登录IP
            login_date=datetime.now(),  # 设置登录时间
            register_time=datetime.now(),
            exp_points=0,
            level=1,
            level_name=cls.LEVEL_CONFIG[1]["name"],
            checkin_days=0,
            continuous_checkin_days=0,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # 创建用户详情模型并返回
        user_detail = H5UserDetailModel.model_validate(new_user)
        
        # 确保user_id字段为字符串格式
        user_detail.user_id = str(new_user.user_id)
        # 确保register_time字段被赋值
        user_detail.register_time = new_user.register_time
        # 确保create_time字段被赋值
        user_detail.create_time = new_user.create_time
        
        return user_detail
    
    @classmethod
    async def update_user(
        cls,
        user_id: str,
        user: H5UserModel,
        request: Request = None,
        db: AsyncSession = Depends(get_db)
    ) -> Optional[H5UserDetailModel]:
        """
        更新用户
        """
        print(f"service层更新用户，用户ID: {user_id}, 数据: {user.dict() if user else None}")
        
        # 确保不会处理用户名
        if hasattr(user, 'username'):
            print(f"service层删除用户名属性: {user.username}")
            delattr(user, 'username')
        
        # 尝试将用户ID转换为整数
        try:
            user_id_int = int(user_id)
            # 如果成功转换为整数，则使用整数ID查询
            stmt = select(H5User).where(H5User.user_id == user_id_int)
        except ValueError:
            # 如果无法转换为整数，则使用字符串ID查询
            db_user = await cls.find_user_by_string_id(user_id, db)
            if db_user:
                stmt = select(H5User).where(H5User.user_id == db_user.user_id)
            else:
                return None
        
        result = await db.execute(stmt)
        db_user = result.scalars().first()
        
        if not db_user:
            return None
        
        # 更新用户信息
        # 注意：不更新用户名，因为前端在修改用户时不会传递用户名
        if user.nickname:
            db_user.nickname = user.nickname
        if user.email:
            db_user.email = user.email
        if user.phone:
            db_user.phone = user.phone
        if user.avatar:
            db_user.avatar = user.avatar
        if user.status:
            db_user.status = user.status
        if user.bind_type:
            db_user.bind_type = user.bind_type
        if user.pay_type:
            db_user.pay_type = user.pay_type
        
        # 获取用户IP地址
        client_ip = cls.get_client_ip(request)
        db_user.login_ip = client_ip  # 设置登录IP
        
        db_user.update_time = datetime.now()
        
        await db.commit()
        await db.refresh(db_user)
        
        # 转换为DTO
        user_dto = H5UserDetailModel.model_validate(db_user)
        
        # 设置id字段为数据库的user_id值
        user_dto.id = db_user.user_id
        
        # 生成字符串格式的用户ID
        string_id = cls.generate_string_id_from_int(db_user.user_id)
        user_dto.user_id = string_id
        
        # 计算注册天数
        if db_user.register_time:
            delta = datetime.now() - db_user.register_time
            user_dto.register_days = delta.days
            # 确保register_time字段被赋值
            user_dto.register_time = db_user.register_time
        # 确保create_time字段被赋值
        if db_user.create_time:
            user_dto.create_time = db_user.create_time
        
        return user_dto
    
    @classmethod
    async def delete_user(
        cls,
        user_id: str,
        db: AsyncSession = Depends(get_db)
    ) -> bool:
        """
        删除用户
        """
        # 尝试将用户ID转换为整数
        try:
            user_id_int = int(user_id)
            # 如果成功转换为整数，则使用整数ID查询
            stmt = select(H5User).where(H5User.user_id == user_id_int)
        except ValueError:
            # 如果无法转换为整数，则使用字符串ID查询
            db_user = await cls.find_user_by_string_id(user_id, db)
            if db_user:
                stmt = select(H5User).where(H5User.user_id == db_user.user_id)
            else:
                return False
        
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return False
        
        # 软删除
        user.del_flag = "2"
        user.update_time = datetime.now()
        
        await db.commit()
        return True
    
    @classmethod
    async def find_user_by_string_id(
        cls,
        string_id: str,
        db: AsyncSession = Depends(get_db)
    ) -> Optional[H5User]:
        """
        根据字符串ID查找用户
        
        由于我们在应用层使用字符串ID，但在数据库中使用整数ID，
        这个方法会查询所有用户并在内存中匹配字符串ID。
        
        注意：这不是一个高效的方法，仅作为临时解决方案。
        长期解决方案应该是在数据库中添加字符串ID字段。
        """
        # 查询所有用户
        stmt = select(H5User)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        # 在内存中匹配字符串ID
        for user in users:
            # 生成该用户的字符串ID
            user_string_id = cls.generate_string_id_from_int(user.user_id)
            if user_string_id == string_id:
                return user
        
        return None
    
    @classmethod
    def generate_string_id_from_int(cls, user_id: int) -> str:
        """
        从整数ID生成字符串ID
        
        注意：这个方法应该与 generate_string_id 方法生成的ID格式一致
        """
        # 使用固定的种子值，确保每次为同一个整数ID生成相同的字符串ID
        random.seed(user_id)
        string_id = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
        # 重置随机数生成器
        random.seed()
        return string_id
    
    @classmethod
    async def change_user_status(
        cls,
        user_id: str,
        status: str,
        db: AsyncSession = Depends(get_db)
    ) -> bool:
        """
        修改用户状态
        """
        # 尝试将字符串ID转换为整数
        try:
            user_id_int = int(user_id)
            # 如果成功转换为整数，则直接查询数据库
            stmt = select(H5User).where(H5User.user_id == user_id_int)
            result = await db.execute(stmt)
            user = result.scalars().first()
        except (ValueError, TypeError):
            # 如果无法转换为整数，则尝试使用字符串ID查找用户
            user = await cls.find_user_by_string_id(user_id, db)
        
        if not user:
            return False
        
        user.status = status
        user.update_time = datetime.now()
        
        await db.commit()
        return True
    
    @classmethod
    async def user_checkin(
        cls,
        user_id: str,
        db: AsyncSession = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        用户签到
        """
        # 尝试将用户ID转换为整数
        try:
            user_id_int = int(user_id)
            # 如果成功转换为整数，则使用整数ID查询
            stmt = select(H5User).where(H5User.user_id == user_id_int)
        except ValueError:
            # 如果无法转换为整数，则使用字符串ID查询
            db_user = await cls.find_user_by_string_id(user_id, db)
            if db_user:
                user_id_int = db_user.user_id
                stmt = select(H5User).where(H5User.user_id == user_id_int)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
        
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查今天是否已签到
        today = datetime.now().date()
        redis_key = f"{cls.REDIS_CHECKIN_KEY}{user_id_int}:{today}"
        
        # 检查Redis中是否已签到
        if await RedisUtil.exists(redis_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="今天已经签到过了"
            )
        
        # 检查是否需要重置连续签到天数
        reset_continuous = False
        if user.last_checkin_date:
            yesterday = today - timedelta(days=1)
            if user.last_checkin_date.date() < yesterday:
                reset_continuous = True
        
        # 更新签到信息
        exp_gained = 10  # 每次签到获得10点经验值
        
        if reset_continuous:
            user.continuous_checkin_days = 1
        else:
            user.continuous_checkin_days += 1
        
        user.checkin_days += 1
        user.last_checkin_date = datetime.now()
        user.exp_points += exp_gained
        
        # 更新用户等级
        new_level = cls.calculate_level(user.exp_points)
        if new_level > user.level:
            user.level = new_level
            user.level_name = cls.LEVEL_CONFIG[new_level]["name"]
        
        # 记录签到信息到Redis
        await RedisUtil.set(redis_key, "1", 86400)  # 24小时过期
        
        # 记录签到信息到数据库
        checkin_record = H5UserCheckin(
            user_id=user_id_int,
            checkin_date=datetime.now(),
            exp_gained=exp_gained,
            create_time=datetime.now()
        )
        db.add(checkin_record)
        
        await db.commit()
        await db.refresh(user)
        
        # 返回签到结果
        return {
            "checkin_days": user.checkin_days,
            "continuous_checkin_days": user.continuous_checkin_days,
            "exp_gained": exp_gained,
            "total_exp": user.exp_points,
            "level": user.level,
            "level_name": user.level_name
        }
    
    @classmethod
    def calculate_level(cls, exp_points: int) -> int:
        """
        根据经验值计算等级
        """
        level = 1
        for lv, config in cls.LEVEL_CONFIG.items():
            if exp_points >= config["exp"]:
                level = lv
            else:
                break
        return min(level, 7)  # 最高7级
    
    @classmethod
    async def update_user_mood(
        cls,
        user_id: int,
        mood: str,
        db: AsyncSession = Depends(get_db)
    ) -> bool:
        """
        更新用户心情
        """
        if len(mood) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="心情内容不能超过50个字符"
            )
        
        stmt = select(H5User).where(H5User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return False
        
        user.mood = mood
        user.update_time = datetime.now()
        
        await db.commit()
        return True
    
    @classmethod
    async def create_user_mood(
        cls,
        user_id: int,
        content: str,
        status: str,
        db: AsyncSession = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        创建用户心情
        """
        if len(content) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="心情内容不能超过255个字符"
            )
        
        # 检查用户是否存在
        stmt = select(H5User).where(H5User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 创建心情记录
        mood = H5UserMood(
            user_id=user_id,
            content=content,
            status=status,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        
        db.add(mood)
        await db.commit()
        await db.refresh(mood)
        
        return {
            "id": mood.id,
            "user_id": mood.user_id,
            "content": mood.content,
            "status": mood.status,
            "create_time": mood.create_time
        }
    
    @classmethod
    async def get_user_moods(
        cls,
        user_id: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取用户心情列表
        """
        conditions = []
        if user_id:
            conditions.append(H5UserMood.user_id == user_id)
        if status:
            conditions.append(H5UserMood.status == status)
        else:
            # 默认只查询公开的心情
            conditions.append(H5UserMood.status == "0")
        
        # 查询总数
        count_stmt = select(func.count(H5UserMood.id)).where(and_(*conditions))
        total = await db.scalar(count_stmt)
        
        # 分页查询
        stmt = (
            select(H5UserMood, H5User.nickname, H5User.avatar)
            .join(H5User, H5UserMood.user_id == H5User.user_id)
            .where(and_(*conditions))
            .order_by(desc(H5UserMood.create_time))
            .offset((page_num - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        
        mood_list = []
        for mood, nickname, avatar in result:
            mood_dict = {
                "id": mood.id,
                "user_id": mood.user_id,
                "content": mood.content,
                "status": mood.status,
                "create_time": mood.create_time,
                "nickname": nickname,
                "avatar": avatar
            }
            mood_list.append(mood_dict)
        
        return mood_list, total
    
    @classmethod
    async def create_payment_order(
        cls,
        user_id: int,
        amount: int,
        pay_type: str,
        db: AsyncSession = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        创建支付订单
        """
        # 检查用户是否存在
        stmt = select(H5User).where(H5User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 生成订单号
        order_no = f"PAY{int(time.time())}{user_id}{random.randint(1000, 9999)}"
        
        # 设置过期时间（10分钟）
        expire_time = datetime.now() + timedelta(minutes=10)
        
        # 生成二维码URL（实际应用中需要调用支付API生成）
        qrcode_url = f"https://example.com/pay?order_no={order_no}"
        
        # 创建支付记录
        payment = H5UserPayment(
            user_id=user_id,
            order_no=order_no,
            amount=amount,
            pay_type=pay_type,
            status="0",  # 未支付
            qrcode_url=qrcode_url,
            expire_time=expire_time,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        
        # 将订单信息存入Redis，设置10分钟过期
        redis_key = f"{cls.REDIS_PAYMENT_KEY}{order_no}"
        payment_info = {
            "id": payment.id,
            "user_id": payment.user_id,
            "order_no": payment.order_no,
            "amount": payment.amount,
            "pay_type": payment.pay_type,
            "status": payment.status,
            "qrcode_url": payment.qrcode_url,
            "expire_time": payment.expire_time.isoformat()
        }
        await RedisUtil.set(redis_key, payment_info, 600)  # 10分钟过期
        
        return payment_info
    
    @classmethod
    async def check_payment_status(
        cls,
        order_no: str,
        db: AsyncSession = Depends(get_db)
    ) -> Dict[str, Any]:
        """
        检查支付状态
        """
        # 先从Redis中获取
        redis_key = f"{cls.REDIS_PAYMENT_KEY}{order_no}"
        payment_info = await RedisUtil.get(redis_key)
        
        if payment_info:
            # 如果Redis中存在，直接返回
            return payment_info
        
        # 如果Redis中不存在，从数据库中查询
        stmt = select(H5UserPayment).where(H5UserPayment.order_no == order_no)
        result = await db.execute(stmt)
        payment = result.scalars().first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 检查是否过期
        if payment.expire_time and payment.expire_time < datetime.now():
            payment.status = "2"  # 已取消
            await db.commit()
        
        return {
            "id": payment.id,
            "user_id": payment.user_id,
            "order_no": payment.order_no,
            "amount": payment.amount,
            "pay_type": payment.pay_type,
            "status": payment.status,
            "qrcode_url": payment.qrcode_url,
            "expire_time": payment.expire_time.isoformat() if payment.expire_time else None
        }
    
    @classmethod
    async def generate_verify_code(cls, uuid: str) -> Dict[str, Any]:
        """
        生成验证码
        """
        # 生成6位数字验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 存入Redis，设置10分钟过期
        redis_key = f"{cls.REDIS_VERIFY_CODE_KEY}{uuid}"
        await RedisUtil.set(redis_key, code, 600)  # 10分钟过期
        
        return {
            "uuid": uuid,
            "code": code  # 实际应用中应该返回图片
        }
    
    @classmethod
    async def send_email_code(cls, email: str) -> bool:
        """
        发送邮箱验证码
        """
        # 生成6位数字验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 存入Redis，设置10分钟过期
        redis_key = f"{cls.REDIS_EMAIL_CODE_KEY}{email}"
        await RedisUtil.set(redis_key, code, 600)  # 10分钟过期
        
        # 实际应用中需要发送邮件
        # 这里只是模拟
        print(f"Send email code to {email}: {code}")
        
        return True
    
    @classmethod
    async def verify_email_code(cls, email: str, code: str) -> bool:
        """
        验证邮箱验证码
        """
        redis_key = f"{cls.REDIS_EMAIL_CODE_KEY}{email}"
        stored_code = await RedisUtil.get(redis_key)
        
        if not stored_code or stored_code != code:
            return False
        
        # 验证成功后删除Redis中的验证码
        await RedisUtil.delete(redis_key)
        
        return True

    @classmethod
    async def register(
        cls,
        user: H5UserRegisterModel,
        request: Request = None,
        db: AsyncSession = Depends(get_db)
    ) -> H5UserDetailModel:
        """
        用户注册
        """
        # 检查用户名是否已存在
        stmt = select(H5User).where(H5User.username == user.username)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 生成随机昵称
        if not user.nickname:
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.nickname = f"{user.username}_{random_suffix}"
        
        # 获取用户IP地址
        client_ip = cls.get_client_ip(request)
        
        # 创建用户，注意不要指定 user_id，让数据库自动生成
        new_user = H5User(
            username=user.username,
            nickname=user.nickname,
            password=user.password,  # 实际应用中需要加密
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            status=user.status,
            bind_type=user.bind_type,
            pay_type=user.pay_type,
            login_ip=client_ip,  # 设置登录IP
            login_date=datetime.now(),  # 设置登录时间
            register_time=datetime.now(),
            exp_points=0,
            level=1,
            level_name=cls.LEVEL_CONFIG[1]["name"],
            checkin_days=0,
            continuous_checkin_days=0,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # 转换为DTO
        user_detail = H5UserDetailModel.model_validate(new_user)
        
        # 设置id字段为数据库的user_id值
        user_detail.id = new_user.user_id
        
        # 生成字符串格式的用户ID
        string_id = cls.generate_string_id_from_int(new_user.user_id)
        user_detail.user_id = string_id
        
        # 确保register_time字段被赋值
        user_detail.register_time = new_user.register_time
        # 确保create_time字段被赋值
        user_detail.create_time = new_user.create_time
        
        return user_detail

    @staticmethod
    def get_client_ip(request: Request = None) -> str:
        """
        获取客户端IP地址
        """
        if not request:
            print("警告: request对象为None，使用默认IP地址")
            return "127.0.0.1"
        
        try:
            x_forwarded_for = request.headers.get("X-Forwarded-For")
            client_host = request.client.host if hasattr(request.client, 'host') else None
            client_ip = x_forwarded_for or client_host or "127.0.0.1"
            print(f"获取到的用户IP地址: {client_ip}")
            print(f"X-Forwarded-For: {x_forwarded_for}")
            print(f"Client Host: {client_host}")
            return client_ip
        except Exception as e:
            print(f"获取客户端IP地址时发生错误: {str(e)}")
            return "127.0.0.1"
