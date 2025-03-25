#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
轮播图控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_h5.entity.vo.carousel_vo import CarouselModel, CarouselPageQueryModel, DeleteCarouselModel, ChangeStatusModel
from module_h5.service.carousel_service import CarouselService
from utils.response_util import ResponseUtil

# 移除认证依赖，使轮播图API可以无需登录访问
carouselController = APIRouter(prefix='/h5/carousel')

@carouselController.get("/list")
async def get_carousel_list(
    request: Request,
    carousel_query: CarouselPageQueryModel = Depends(CarouselPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取轮播图列表
    """
    # 获取轮播图列表
    carousel_page_query_result = await CarouselService.get_carousel_list_services(
        query_db, carousel_query, is_page=True
    )
    
    return ResponseUtil.success(model_content=carousel_page_query_result)


@carouselController.get("/{carousel_id}")
async def get_carousel_by_id(
    request: Request,
    carousel_id: int = Path(..., description="轮播图ID"),
    query_db: AsyncSession = Depends(get_db),
):
    """
    根据ID获取轮播图详情
    """
    carousel = await CarouselService.get_carousel_detail_services(db=query_db, carousel_id=carousel_id)
    if not carousel:
        return ResponseUtil.error(msg="轮播图不存在")
    
    return ResponseUtil.success(data=carousel)


@carouselController.post("")
async def create_carousel(
    request: Request,
    carousel_in: CarouselModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
):
    """
    创建轮播图
    """
    carousel = await CarouselService.add_carousel_services(
        db=query_db, 
        carousel=carousel_in, 
        username="admin"  # 使用默认用户名
    )
    
    return ResponseUtil.success(msg="创建成功")


@carouselController.put("")
async def update_carousel(
    request: Request,
    carousel_in: CarouselModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
):
    """
    更新轮播图
    """
    if not carousel_in.id:
        return ResponseUtil.error(msg="轮播图ID不能为空")
    
    carousel = await CarouselService.update_carousel_services(
        db=query_db, 
        carousel_id=carousel_in.id, 
        carousel=carousel_in, 
        username="admin"  # 使用默认用户名
    )
    
    if carousel is None:
        return ResponseUtil.error(msg="轮播图不存在")
    elif carousel is False:
        return ResponseUtil.error(msg="只能修改状态为正常且未过期的轮播图")
    
    return ResponseUtil.success(msg="更新成功")


@carouselController.delete("")
async def delete_carousel(
    request: Request,
    delete_model: DeleteCarouselModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
):
    """
    删除轮播图
    """
    carousel_ids = [int(x) for x in delete_model.carousel_ids.split(",") if x]
    count = await CarouselService.delete_carousel_services(db=query_db, carousel_ids=carousel_ids)
    
    if count == 0:
        return ResponseUtil.error(msg="未删除任何数据")
    
    return ResponseUtil.success(msg=f"成功删除{count}条数据")


@carouselController.delete("/{carousel_id}")
async def delete_carousel_by_id(
    request: Request,
    carousel_id: int = Path(..., description="轮播图ID"),
    query_db: AsyncSession = Depends(get_db),
):
    """
    删除轮播图（逻辑删除，修改状态为停用）
    """
    # 实际上是修改状态为停用（1）
    carousel = await CarouselService.change_carousel_status_services(
        db=query_db, 
        carousel_id=carousel_id, 
        status="1",  # 1表示停用
        username="admin"
    )
    
    if not carousel:
        return ResponseUtil.error(msg="轮播图不存在")
    
    return ResponseUtil.success(msg="删除成功")


@carouselController.put("/changeStatus")
async def change_carousel_status(
    request: Request,
    status_model: ChangeStatusModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
):
    """
    修改轮播图状态
    """
    carousel = await CarouselService.change_carousel_status_services(
        db=query_db, 
        carousel_id=status_model.carousel_id, 
        status=status_model.status, 
        username="admin"  # 使用默认用户名
    )
    
    if not carousel:
        return ResponseUtil.error(msg="轮播图不存在")
    
    return ResponseUtil.success(msg="状态修改成功")
