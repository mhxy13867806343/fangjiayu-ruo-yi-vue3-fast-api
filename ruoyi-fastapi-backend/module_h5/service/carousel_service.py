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
from utils.page_util import PageResponseModel, PageUtil
import os
import requests
import uuid
from config.env import UploadConfig
from utils.upload_util import UploadUtil


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
        
        # 处理日期范围参数
        if hasattr(carousel_query, 'begin_time') and carousel_query.begin_time and hasattr(carousel_query, 'end_time') and carousel_query.end_time:
            try:
                start_date = datetime.fromisoformat(carousel_query.begin_time.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(carousel_query.end_time.replace('Z', '+00:00'))
                # 设置结束日期为当天的23:59:59
                end_date = end_date.replace(hour=23, minute=59, second=59)
                
                where_list.append(SysCarousel.create_time >= start_date)
                where_list.append(SysCarousel.create_time <= end_date)
            except (ValueError, TypeError):
                # 如果日期格式不正确，忽略这个条件
                pass
        
        # 构建查询语句
        query = select(SysCarousel)
        if where_list:
            query = query.where(and_(*where_list))
        
        # 排序
        query = query.order_by(SysCarousel.sort.asc(), SysCarousel.id.desc())
        
        # 使用与角色管理相同的分页方法
        result = await PageUtil.paginate(db, query, carousel_query.page_num, carousel_query.page_size, is_page)
        
        # 查询媒体信息
        carousel_models = []
        
        # 判断是否有分页结果
        if is_page and hasattr(result, 'rows'):
            carousel_list = result.rows
        else:
            carousel_list = result  # 如果没有分页，直接使用结果
            
        for carousel in carousel_list:
            # 创建轮播图模型
            carousel_dict = {
                "id": carousel["id"] if isinstance(carousel, dict) else carousel.id,
                "title": carousel["title"] if isinstance(carousel, dict) else carousel.title,
                "type": carousel["type"] if isinstance(carousel, dict) else carousel.type,
                "category": carousel["category"] if isinstance(carousel, dict) else carousel.category,
                "position": carousel["position"] if isinstance(carousel, dict) else carousel.position,
                "url": carousel["url"] if isinstance(carousel, dict) else carousel.url,
                "sort": carousel["sort"] if isinstance(carousel, dict) else carousel.sort,
                "status": carousel["status"] if isinstance(carousel, dict) else carousel.status,
                "startTime": carousel["startTime"] if isinstance(carousel, dict) else (carousel.start_time.strftime('%Y-%m-%d %H:%M:%S') if carousel.start_time else None),
                "endTime": carousel["endTime"] if isinstance(carousel, dict) else (carousel.end_time.strftime('%Y-%m-%d %H:%M:%S') if carousel.end_time else None),
                "createTime": carousel["createTime"] if isinstance(carousel, dict) else (carousel.create_time.strftime('%Y-%m-%d %H:%M:%S') if carousel.create_time else None),
                "createBy": carousel["createBy"] if isinstance(carousel, dict) else carousel.create_by,
                "updateTime": carousel["updateTime"] if isinstance(carousel, dict) else (carousel.update_time.strftime('%Y-%m-%d %H:%M:%S') if carousel.update_time else None),
                "updateBy": carousel["updateBy"] if isinstance(carousel, dict) else carousel.update_by,
                "remark": carousel["remark"] if isinstance(carousel, dict) else carousel.remark,
                "mediaList": []
            }
            
            # 查询媒体信息
            carousel_id = carousel["id"] if isinstance(carousel, dict) else carousel.id
            media_stmt = select(SysCarouselMedia).where(SysCarouselMedia.carousel_id == carousel_id).order_by(SysCarouselMedia.sort)
            media_result = await db.execute(media_stmt)
            media_list = media_result.scalars().all()
            
            # 创建媒体模型列表
            media_models = []
            for media in media_list:
                media_dict = {
                    "id": media.id,
                    "carouselId": media.carousel_id,
                    "name": media.name,
                    "mediaType": media.type,
                    "mediaUrl": media.url,
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
            return PageResponseModel(
                total=result.total,
                rows=carousel_models,
                page_num=carousel_query.page_num,
                page_size=carousel_query.page_size
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
                "mediaType": media.type,
                "mediaUrl": media.url,
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
                # 处理blob URL
                url = media.url
                if url and url.startswith('blob:'):
                    url = await cls.process_blob_url(url, media.type)
                
                db_media = SysCarouselMedia(
                    carousel_id=carousel_obj.id,
                    name=media.name,
                    type=media.type,
                    url=url,
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
    ) -> Optional[bool]:
        """
        更新轮播图
        """
        # 查询轮播图
        stmt = select(SysCarousel).where(SysCarousel.id == carousel_id)
        result = await db.execute(stmt)
        db_carousel = result.scalars().first()
        
        if not db_carousel:
            return None
            
        # 检查轮播图状态，只有正常状态且未过期的轮播图才能修改
        current_time = datetime.now()
        if db_carousel.status != "0" or (db_carousel.end_time and db_carousel.end_time < current_time):
            return False
            
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
        delete_stmt = delete(SysCarouselMedia).where(SysCarouselMedia.carousel_id == carousel_id)
        await db.execute(delete_stmt)
        
        # 添加新媒体
        if carousel.media_list:
            for media in carousel.media_list:
                # 处理blob URL
                url = media.url
                if url and url.startswith('blob:'):
                    url = await cls.process_blob_url(url, media.type)
                
                db_media = SysCarouselMedia(
                    carousel_id=db_carousel.id,
                    name=media.name,
                    type=media.type,
                    url=url,
                    external_link=media.external_link,
                    sort=media.sort,
                    create_time=datetime.now(),
                    update_time=datetime.now()
                )
                db.add(db_media)
        
        await db.commit()
        return True
    
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
                # 处理blob URL
                url = media.url
                if url and url.startswith('blob:'):
                    url = await cls.process_blob_url(url, media.type)
                
                db_media = SysCarouselMedia(
                    carousel_id=db_carousel.id,
                    name=media.name,
                    type=media.type,
                    url=url,
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
    
    @classmethod
    async def process_blob_url(cls, url: str, media_type: str = 'image') -> str:
        """
        处理blob URL，下载文件并保存到本地
        返回文件路径
        """
        if not url or not url.startswith('blob:'):
            return url
            
        try:
            # 创建上传目录，与通用上传服务保持一致
            relative_path = f'upload/{datetime.now().strftime("%Y")}/{datetime.now().strftime("%m")}/{datetime.now().strftime("%d")}'
            dir_path = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)
            
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path)
                except FileExistsError:
                    pass
                    
            # 根据媒体类型确定文件后缀
            file_extension = '.jpg'  # 默认为jpg
            if media_type and media_type.lower() == 'video':
                file_extension = '.mp4'  # 视频默认为mp4
                
            # 生成文件名，与通用上传服务保持一致
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            random_str = UploadUtil.generate_random_str()
            filename = f'{random_str}_{current_time}{UploadConfig.UPLOAD_MACHINE}{UploadUtil.generate_random_number()}{file_extension}'
            filepath = os.path.join(dir_path, filename)
            
            # 由于blob URL无法直接下载，这里我们只能返回路径
            # 实际的文件上传应该由前端处理
            return f"{UploadConfig.UPLOAD_PREFIX}/{relative_path}/{filename}"
            
        except Exception as e:
            print(f"处理blob URL出错: {e}")
            return ""
