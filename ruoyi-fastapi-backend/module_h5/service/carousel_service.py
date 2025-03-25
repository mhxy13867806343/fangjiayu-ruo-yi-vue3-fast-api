#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
轮播图服务
"""
from datetime import datetime
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Tuple

from module_h5.entity.do.carousel_do import SysCarousel, SysCarouselMedia
from module_h5.entity.vo.carousel_vo import CarouselModel, CarouselMediaModel, CarouselPageQueryModel
from utils.page_util import PageResponseModel


class CarouselService:
    """轮播图服务类"""
    
    @classmethod
    async def get_carousel_list_services(
        cls,
        db: AsyncSession,
        carousel_query: CarouselPageQueryModel,
        is_page: bool = True
    ) -> PageResponseModel:
        """
        获取轮播图列表
        """
        # 构建查询条件
        where_list = []
        
        # 根据状态查询，如果没有指定状态，则查询所有状态（包括正常和禁用）
        if hasattr(carousel_query, 'status') and carousel_query.status:
            where_list.append(SysCarousel.status == carousel_query.status)
        
        # 只查询未过期的数据（结束时间为空或结束时间大于当前时间）
        current_time = datetime.now()
        where_list.append(or_(
            SysCarousel.end_time == None,
            SysCarousel.end_time > current_time
        ))
        
        # 标题
        if hasattr(carousel_query, 'title') and carousel_query.title:
            where_list.append(SysCarousel.title.like(f"%{carousel_query.title}%"))
        
        # 轮播类型
        if hasattr(carousel_query, 'type') and carousel_query.type:
            where_list.append(SysCarousel.type == carousel_query.type)
        
        # 显示位置
        if hasattr(carousel_query, 'position') and carousel_query.position:
            where_list.append(SysCarousel.position == carousel_query.position)
        
        # 时间范围
        if hasattr(carousel_query, 'begin_time') and carousel_query.begin_time:
            where_list.append(SysCarousel.create_time >= carousel_query.begin_time)
        
        if hasattr(carousel_query, 'end_time') and carousel_query.end_time:
            where_list.append(SysCarousel.create_time <= carousel_query.end_time)
        
        # 计算总数
        count_stmt = select(func.count(SysCarousel.id))
        if where_list:
            count_stmt = count_stmt.where(and_(*where_list))
        
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()
        
        # 构建查询语句
        stmt = select(SysCarousel)
        if where_list:
            stmt = stmt.where(and_(*where_list))
        
        # 排序
        stmt = stmt.order_by(SysCarousel.sort.asc(), SysCarousel.id.desc())
        
        # 分页
        if is_page:
            page_num = getattr(carousel_query, 'page_num', 1)
            page_size = getattr(carousel_query, 'page_size', 10)
            stmt = stmt.offset((page_num - 1) * page_size).limit(page_size)
        
        # 执行查询
        result = await db.execute(stmt)
        carousel_list = result.scalars().all()
        
        # 查询媒体信息
        carousel_models = []
        for carousel in carousel_list:
            # 创建轮播图模型
            carousel_dict = {
                "id": carousel.id,
                "title": carousel.title,
                "type": carousel.type,
                "category": carousel.category,
                "position": carousel.position,
                "isExternalLink": carousel.is_external_link,
                "url": carousel.url,
                "sort": carousel.sort,
                "startTime": carousel.start_time,
                "endTime": carousel.end_time,
                "desc": carousel.desc,
                "remark": carousel.remark,
                "status": carousel.status,
                "mediaList": []
            }
            
            # 查询媒体列表
            media_stmt = select(SysCarouselMedia).where(SysCarouselMedia.carousel_id == carousel.id)
            media_result = await db.execute(media_stmt)
            media_list = media_result.scalars().all()
            
            # 转换为媒体模型列表
            media_models = []
            for media in media_list:
                media_dict = {
                    "id": media.id,
                    "carouselId": media.carousel_id,
                    "name": media.name,
                    "url": media.url,
                    "type": media.type,
                    "externalLink": media.external_link,
                    "sort": media.sort
                }
                media_models.append(media_dict)
            
            # 添加媒体列表
            carousel_dict["mediaList"] = media_models
            
            # 添加到轮播图模型列表
            carousel_models.append(carousel_dict)
        
        # 返回分页数据
        if is_page:
            page_num = getattr(carousel_query, 'page_num', 1)
            page_size = getattr(carousel_query, 'page_size', 10)
            return PageResponseModel(
                total=total,
                rows=carousel_models,
                page_num=page_num,
                page_size=page_size
            )
        else:
            return carousel_models
    
    @classmethod
    async def get_carousel_detail_services(
        cls,
        db: AsyncSession,
        carousel_id: int
    ) -> Optional[CarouselModel]:
        """
        获取轮播图详情
        """
        # 查询轮播图
        stmt = select(SysCarousel).where(SysCarousel.id == carousel_id)
        result = await db.execute(stmt)
        carousel = result.scalars().first()
        
        if not carousel:
            return None
        
        # 创建轮播图模型
        carousel_dict = {
            "id": carousel.id,
            "title": carousel.title,
            "type": carousel.type,
            "category": carousel.category,
            "position": carousel.position,
            "isExternalLink": carousel.is_external_link,
            "url": carousel.url,
            "sort": carousel.sort,
            "startTime": carousel.start_time,
            "endTime": carousel.end_time,
            "desc": carousel.desc,
            "remark": carousel.remark,
            "status": carousel.status,
            "mediaList": []
        }
        
        # 查询媒体列表
        media_stmt = select(SysCarouselMedia).where(SysCarouselMedia.carousel_id == carousel_id)
        media_result = await db.execute(media_stmt)
        media_list = media_result.scalars().all()
        
        # 转换为媒体模型列表
        media_models = []
        for media in media_list:
            media_dict = {
                "id": media.id,
                "carouselId": media.carousel_id,
                "name": media.name,
                "url": media.url,
                "type": media.type,
                "externalLink": media.external_link,
                "sort": media.sort
            }
            media_models.append(media_dict)
        
        # 添加媒体列表
        carousel_dict["mediaList"] = media_models
        
        # 创建并返回轮播图模型
        return CarouselModel(**carousel_dict)
    
    @classmethod
    async def add_carousel_services(
        cls,
        db: AsyncSession,
        carousel: CarouselModel,
        username: str
    ) -> SysCarousel:
        """
        添加轮播图
        """
        # 创建轮播图对象
        carousel_obj = SysCarousel(
            title=carousel.title,
            type=carousel.type,
            category=carousel.category,
            position=carousel.position,
            is_external_link=carousel.is_external_link,
            url=carousel.url,
            sort=carousel.sort,
            start_time=carousel.start_time,
            end_time=carousel.end_time,
            desc=carousel.desc,
            remark=carousel.remark,
            status=carousel.status,
            create_by=username,
            create_time=datetime.now(),
            update_by=username,
            update_time=datetime.now()
        )
        
        # 添加轮播图
        db.add(carousel_obj)
        await db.flush()
        
        # 添加媒体
        if carousel.media_list:
            for media in carousel.media_list:
                db_media = SysCarouselMedia(
                    carousel_id=carousel_obj.id,
                    name=media.name,
                    url=media.url,
                    type=media.type,
                    external_link=media.external_link,
                    sort=media.sort,
                    create_time=datetime.now()
                )
                db.add(db_media)
        
        await db.commit()
        return carousel_obj
    
    @classmethod
    async def update_carousel_services(
        cls,
        db: AsyncSession,
        carousel_id: int,
        carousel: CarouselModel,
        username: str
    ) -> Optional[SysCarousel]:
        """
        更新轮播图
        """
        # 查询轮播图是否存在
        carousel_stmt = select(SysCarousel).where(SysCarousel.id == carousel_id)
        carousel_result = await db.execute(carousel_stmt)
        carousel_obj = carousel_result.scalars().first()
        
        if not carousel_obj:
            return None
        
        # 检查轮播图状态，只有状态为正常(0)的轮播图才能被修改
        if carousel_obj.status != "0":
            return False
            
        # 检查轮播图是否已过期
        current_time = datetime.now()
        if carousel_obj.end_time and carousel_obj.end_time <= current_time:
            return False
        
        # 更新轮播图信息
        carousel_obj.title = carousel.title
        carousel_obj.type = carousel.type
        carousel_obj.category = carousel.category
        carousel_obj.position = carousel.position
        carousel_obj.is_external_link = carousel.is_external_link
        carousel_obj.url = carousel.url
        carousel_obj.sort = carousel.sort
        carousel_obj.start_time = carousel.start_time
        carousel_obj.end_time = carousel.end_time
        carousel_obj.desc = carousel.desc
        carousel_obj.remark = carousel.remark
        carousel_obj.status = carousel.status
        carousel_obj.update_by = username
        carousel_obj.update_time = datetime.now()
        
        # 删除原有媒体信息
        media_stmt = delete(SysCarouselMedia).where(SysCarouselMedia.carousel_id == carousel_id)
        await db.execute(media_stmt)
        
        # 添加新的媒体信息
        for media in carousel.media_list:
            media_obj = SysCarouselMedia(
                carousel_id=carousel_id,
                name=media.name,
                url=media.url,
                type=media.type,
                external_link=media.external_link,
                sort=media.sort,
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            db.add(media_obj)
        
        await db.commit()
        
        return carousel_obj
    
    @classmethod
    async def edit_carousel_services(
        cls,
        db: AsyncSession,
        carousel: CarouselModel,
        username: str
    ) -> Optional[SysCarousel]:
        """
        编辑轮播图
        """
        # 查询轮播图
        stmt = select(SysCarousel).where(SysCarousel.id == carousel.id)
        result = await db.execute(stmt)
        db_carousel = result.scalars().first()
        
        if not db_carousel:
            return None
        
        # 更新轮播图
        db_carousel.title = carousel.title
        db_carousel.type = carousel.type
        db_carousel.category = carousel.category
        db_carousel.position = carousel.position
        db_carousel.is_external_link = carousel.is_external_link
        db_carousel.url = carousel.url
        db_carousel.sort = carousel.sort
        db_carousel.start_time = carousel.start_time
        db_carousel.end_time = carousel.end_time
        db_carousel.desc = carousel.desc
        db_carousel.remark = carousel.remark
        db_carousel.status = carousel.status
        db_carousel.update_by = username
        db_carousel.update_time = datetime.now()
        
        # 删除原有媒体
        media_stmt = select(SysCarouselMedia).where(SysCarouselMedia.carousel_id == carousel.id)
        media_result = await db.execute(media_stmt)
        media_list = media_result.scalars().all()
        
        for media in media_list:
            await db.delete(media)
        
        # 添加新媒体
        if carousel.media_list:
            for media in carousel.media_list:
                db_media = SysCarouselMedia(
                    carousel_id=db_carousel.id,
                    name=media.name,
                    url=media.url,
                    type=media.type,
                    external_link=media.external_link,
                    sort=media.sort,
                    create_time=datetime.now()
                )
                db.add(db_media)
        
        await db.commit()
        return db_carousel
    
    @classmethod
    async def delete_carousel_services(
        cls,
        db: AsyncSession,
        carousel_ids: List[int]
    ) -> int:
        """
        删除轮播图
        """
        # 删除轮播图
        count = 0
        for carousel_id in carousel_ids:
            # 查询轮播图
            stmt = select(SysCarousel).where(SysCarousel.id == carousel_id)
            result = await db.execute(stmt)
            db_carousel = result.scalars().first()
            
            if db_carousel:
                await db.delete(db_carousel)
                count += 1
        
        await db.commit()
        return count
    
    @classmethod
    async def change_carousel_status_services(
        cls,
        db: AsyncSession,
        carousel_id: int,
        status: str,
        username: str
    ) -> Optional[SysCarousel]:
        """
        修改轮播图状态
        """
        # 查询轮播图
        stmt = select(SysCarousel).where(SysCarousel.id == carousel_id)
        result = await db.execute(stmt)
        db_carousel = result.scalars().first()
        
        if not db_carousel:
            return None
        
        # 更新状态
        db_carousel.status = status
        db_carousel.update_by = username
        db_carousel.update_time = datetime.now()
        
        await db.commit()
        return db_carousel
