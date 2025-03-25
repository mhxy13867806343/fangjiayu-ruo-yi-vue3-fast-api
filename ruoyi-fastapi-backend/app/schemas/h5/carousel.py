#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
轮播图相关的数据模型
"""
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class CarouselMediaBase(BaseModel):
    """轮播图媒体基础模型"""
    name: str = Field(..., description="媒体名称")
    type: str = Field(..., description="媒体类型（image图片 video视频）")
    url: str = Field(..., description="媒体URL")
    external_link: Optional[str] = Field(None, description="外链地址")
    sort: Optional[int] = Field(0, description="排序")


class CarouselMediaCreate(CarouselMediaBase):
    """创建轮播图媒体模型"""
    carousel_id: int = Field(..., description="轮播图ID")


class CarouselMediaUpdate(CarouselMediaBase):
    """更新轮播图媒体模型"""
    pass


class CarouselMediaInDB(CarouselMediaBase):
    """数据库中的轮播图媒体模型"""
    id: int = Field(..., description="媒体ID")
    carousel_id: int = Field(..., description="轮播图ID")
    create_by: str = Field("", description="创建者")
    create_time: datetime = Field(None, description="创建时间")
    update_by: str = Field("", description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        orm_mode = True


class CarouselBase(BaseModel):
    """轮播图基础模型"""
    title: str = Field(..., description="标题")
    type: str = Field(..., description="轮播类型（1普通轮播 2活动轮播 3推广轮播）")
    category: str = Field(..., description="分类（1活动 2促销 3新品 4热门 5推荐）")
    position: str = Field(..., description="显示位置（1首页 0其他页面）")
    url: Optional[str] = Field(None, description="URL地址")
    is_external_link: str = Field("0", description="是否外部链接（0否 1是）")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    detail: Optional[str] = Field(None, description="详情信息")
    status: str = Field("0", description="状态（0正常 1停用）")
    sort: Optional[int] = Field(0, description="排序")
    remark: Optional[str] = Field(None, description="备注")


class CarouselCreate(CarouselBase):
    """创建轮播图模型"""
    media_list: Optional[List[CarouselMediaBase]] = Field([], description="媒体列表")


class CarouselUpdate(CarouselBase):
    """更新轮播图模型"""
    media_list: Optional[List[CarouselMediaBase]] = Field([], description="媒体列表")


class CarouselInDB(CarouselBase):
    """数据库中的轮播图模型"""
    id: int = Field(..., description="轮播图ID")
    create_by: str = Field("", description="创建者")
    create_time: datetime = Field(None, description="创建时间")
    update_by: str = Field("", description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        orm_mode = True


class CarouselOut(CarouselInDB):
    """轮播图输出模型"""
    type_name: str = Field("", description="轮播类型名称")
    category_name: str = Field("", description="分类名称")
    position_name: str = Field("", description="位置名称")
    media_list: List[CarouselMediaInDB] = Field([], description="媒体列表")


class CarouselQuery(BaseModel):
    """轮播图查询模型"""
    title: Optional[str] = Field(None, description="标题")
    type: Optional[str] = Field(None, description="轮播类型")
    position: Optional[str] = Field(None, description="显示位置")
    status: Optional[str] = Field(None, description="状态")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
