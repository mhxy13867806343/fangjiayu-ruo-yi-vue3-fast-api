#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
轮播图视图对象
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CarouselMediaModel(BaseModel):
    """轮播图媒体模型"""
    id: Optional[int] = Field(None, description="媒体ID")
    carousel_id: Optional[int] = Field(None, description="轮播图ID")
    name: Optional[str] = Field(None, description="媒体名称")
    url: str = Field(..., description="媒体地址")
    type: str = Field(..., description="媒体类型")
    external_link: Optional[str] = Field(None, description="外部链接")
    sort: Optional[int] = Field(0, description="排序")
    
    class Config:
        from_attributes = True


class CarouselModel(BaseModel):
    """轮播图模型"""
    id: Optional[int] = Field(None, description="轮播图ID")
    title: str = Field(..., description="标题")
    type: str = Field(..., description="轮播类型")
    category: Optional[str] = Field(None, description="分类")
    position: str = Field(..., description="显示位置")
    is_external_link: Optional[str] = Field("0", description="是否外链")
    url: Optional[str] = Field(None, description="链接地址")
    sort: Optional[int] = Field(0, description="排序")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    remark: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field("0", description="状态（0正常 1停用）")
    media_list: List[CarouselMediaModel] = Field([], description="媒体列表")
    
    class Config:
        from_attributes = True


class CarouselPageQueryModel(BaseModel):
    """轮播图分页查询模型"""
    page_num: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
    title: Optional[str] = Field(None, description="标题")
    type: Optional[str] = Field(None, description="轮播类型")
    position: Optional[str] = Field(None, description="显示位置")
    status: Optional[str] = Field(None, description="状态")
    begin_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    
    @classmethod
    def as_query(cls):
        return cls
    
    class Config:
        from_attributes = True


class DeleteCarouselModel(BaseModel):
    """删除轮播图模型"""
    carousel_ids: str = Field(..., description="轮播图ID，多个以逗号分隔")
    
    class Config:
        from_attributes = True


class ChangeStatusModel(BaseModel):
    """修改状态模型"""
    carousel_id: int = Field(..., description="轮播图ID")
    status: str = Field(..., description="状态（0正常 1停用）")
    
    class Config:
        from_attributes = True
