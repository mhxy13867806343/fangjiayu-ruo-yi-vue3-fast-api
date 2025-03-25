#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
轮播图CRUD操作
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.models.h5.carousel import Carousel, CarouselMedia
from app.schemas.h5.carousel import CarouselCreate, CarouselUpdate, CarouselMediaCreate
from app.core.security import get_current_username


class CRUDCarousel:
    """轮播图CRUD操作类"""

    @staticmethod
    def get_carousel(db: Session, carousel_id: int) -> Optional[Carousel]:
        """
        根据ID获取轮播图
        """
        return db.query(Carousel).filter(Carousel.id == carousel_id).first()

    @staticmethod
    def get_carousels(
        db: Session, 
        title: Optional[str] = None,
        type: Optional[str] = None,
        position: Optional[str] = None,
        status: Optional[str] = None,
        begin_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Carousel]:
        """
        获取轮播图列表
        """
        query = db.query(Carousel)
        
        # 添加查询条件
        if title:
            query = query.filter(Carousel.title.like(f"%{title}%"))
        if type:
            query = query.filter(Carousel.type == type)
        if position:
            query = query.filter(Carousel.position == position)
        if status:
            query = query.filter(Carousel.status == status)
        if begin_time and end_time:
            query = query.filter(and_(
                Carousel.create_time >= begin_time,
                Carousel.create_time <= end_time
            ))
            
        # 按创建时间降序排序
        query = query.order_by(desc(Carousel.create_time))
        
        # 分页
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_carousels_count(
        db: Session, 
        title: Optional[str] = None,
        type: Optional[str] = None,
        position: Optional[str] = None,
        status: Optional[str] = None,
        begin_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        """
        获取轮播图总数
        """
        query = db.query(Carousel)
        
        # 添加查询条件
        if title:
            query = query.filter(Carousel.title.like(f"%{title}%"))
        if type:
            query = query.filter(Carousel.type == type)
        if position:
            query = query.filter(Carousel.position == position)
        if status:
            query = query.filter(Carousel.status == status)
        if begin_time and end_time:
            query = query.filter(and_(
                Carousel.create_time >= begin_time,
                Carousel.create_time <= end_time
            ))
            
        return query.count()

    @staticmethod
    def create_carousel(
        db: Session, 
        carousel_in: CarouselCreate, 
        current_user: str
    ) -> Carousel:
        """
        创建轮播图
        """
        # 创建轮播图对象
        db_carousel = Carousel(
            title=carousel_in.title,
            type=carousel_in.type,
            category=carousel_in.category,
            position=carousel_in.position,
            url=carousel_in.url,
            is_external_link=carousel_in.is_external_link,
            start_time=carousel_in.start_time,
            end_time=carousel_in.end_time,
            detail=carousel_in.detail,
            status=carousel_in.status,
            sort=carousel_in.sort,
            remark=carousel_in.remark,
            create_by=current_user,
            create_time=datetime.now()
        )
        
        # 保存轮播图
        db.add(db_carousel)
        db.commit()
        db.refresh(db_carousel)
        
        # 创建媒体文件
        if carousel_in.media_list:
            for i, media in enumerate(carousel_in.media_list):
                db_media = CarouselMedia(
                    carousel_id=db_carousel.id,
                    name=media.name,
                    type=media.type,
                    url=media.url,
                    external_link=media.external_link,
                    sort=i,
                    create_by=current_user,
                    create_time=datetime.now()
                )
                db.add(db_media)
        
        db.commit()
        db.refresh(db_carousel)
        
        return db_carousel

    @staticmethod
    def update_carousel(
        db: Session, 
        db_carousel: Carousel, 
        carousel_in: CarouselUpdate, 
        current_user: str
    ) -> Carousel:
        """
        更新轮播图
        """
        # 更新轮播图基本信息
        update_data = carousel_in.dict(exclude_unset=True, exclude={"media_list"})
        update_data["update_by"] = current_user
        update_data["update_time"] = datetime.now()
        
        for key, value in update_data.items():
            setattr(db_carousel, key, value)
        
        # 删除原有媒体文件
        db.query(CarouselMedia).filter(CarouselMedia.carousel_id == db_carousel.id).delete()
        
        # 创建新的媒体文件
        if carousel_in.media_list:
            for i, media in enumerate(carousel_in.media_list):
                db_media = CarouselMedia(
                    carousel_id=db_carousel.id,
                    name=media.name,
                    type=media.type,
                    url=media.url,
                    external_link=media.external_link,
                    sort=i,
                    create_by=current_user,
                    create_time=datetime.now()
                )
                db.add(db_media)
        
        db.commit()
        db.refresh(db_carousel)
        
        return db_carousel

    @staticmethod
    def delete_carousel(db: Session, db_carousel: Carousel) -> Carousel:
        """
        删除轮播图
        """
        db.delete(db_carousel)
        db.commit()
        return db_carousel

    @staticmethod
    def update_carousel_status(
        db: Session, 
        db_carousel: Carousel, 
        status: str, 
        current_user: str
    ) -> Carousel:
        """
        更新轮播图状态
        """
        db_carousel.status = status
        db_carousel.update_by = current_user
        db_carousel.update_time = datetime.now()
        
        db.commit()
        db.refresh(db_carousel)
        
        return db_carousel


carousel = CRUDCarousel()
