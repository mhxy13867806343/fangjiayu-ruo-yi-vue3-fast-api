#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
轮播图数据对象
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.get_db import Base


class SysCarousel(Base):
    """轮播图表"""
    __tablename__ = "sys_carousel"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="轮播图ID")
    title = Column(String(100), nullable=False, comment="标题")
    type = Column(String(20), nullable=False, comment="轮播类型")
    category = Column(String(20), nullable=True, comment="分类")
    position = Column(String(20), nullable=False, comment="显示位置")
    is_external_link = Column(String(1), default="0", comment="是否外链")
    url = Column(String(255), nullable=True, comment="链接地址")
    sort = Column(Integer, default=0, comment="排序")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    remark = Column(String(500), nullable=True, comment="备注")
    status = Column(String(1), default="0", comment="状态（0正常 1停用）")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment="更新时间")
    
    # 关联媒体
    media_list = relationship("SysCarouselMedia", back_populates="carousel", cascade="all, delete-orphan")


class SysCarouselMedia(Base):
    """轮播图媒体表"""
    __tablename__ = "sys_carousel_media"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="媒体ID")
    carousel_id = Column(Integer, ForeignKey("sys_carousel.id"), nullable=False, comment="轮播图ID")
    name = Column(String(100), nullable=True, comment="媒体名称")
    url = Column(String(255), nullable=False, comment="媒体地址")
    type = Column(String(20), nullable=False, comment="媒体类型")
    external_link = Column(String(255), nullable=True, comment="外部链接")
    sort = Column(Integer, default=0, comment="排序")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment="更新时间")
    
    # 关联轮播图
    carousel = relationship("SysCarousel", back_populates="media_list")
