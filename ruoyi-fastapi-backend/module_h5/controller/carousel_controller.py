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
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_h5.entity.vo.carousel_vo import CarouselModel, CarouselPageQueryModel, DeleteCarouselModel, ChangeStatusModel
from module_h5.service.carousel_service import CarouselService
from utils.response_util import ResponseUtil

# 添加认证依赖，使轮播图API需要登录访问
carouselController = APIRouter(prefix='/h5/carousel', dependencies=[Depends(LoginService.get_current_user)])

@carouselController.get("/list", dependencies=[Depends(CheckUserInterfaceAuth("h5:carousel:list"))])
async def get_carousel_list(
    request: Request,
    carousel_query: CarouselPageQueryModel = Depends(CarouselPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取轮播图列表
    """
    # 获取轮播图列表
    carousel_page_query_result = await CarouselService.get_carousel_list_services(
        query_db, carousel_query, is_page=True
    )
    
    return ResponseUtil.success(model_content=carousel_page_query_result)


@carouselController.get("/{carousel_id}", dependencies=[Depends(CheckUserInterfaceAuth("h5:carousel:query"))])
async def get_carousel_by_id(
    request: Request,
    carousel_id: int = Path(..., description="轮播图ID"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    根据ID获取轮播图详情
    """
    carousel = await CarouselService.get_carousel_detail_services(db=query_db, carousel_id=carousel_id)
    if not carousel:
        return ResponseUtil.error(msg="轮播图不存在")
    
    return ResponseUtil.success(data=carousel)


@carouselController.post("", dependencies=[Depends(CheckUserInterfaceAuth("h5:carousel:add"))])
async def create_carousel(
    request: Request,
    carousel_in: CarouselModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    创建轮播图
    """
    # 打印接收到的轮播图数据
    print("接收到的轮播图数据:", carousel_in.dict())
    
    # 创建轮播图
    result = await CarouselService.add_carousel_services(
        db=query_db,
        carousel=carousel_in,
        username=current_user.user.user_name
    )
    return ResponseUtil.success(msg="创建成功", data=result)


@carouselController.put("", dependencies=[Depends(CheckUserInterfaceAuth("h5:carousel:edit"))])
async def update_carousel(
    request: Request,
    carousel_in: CarouselModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    修改轮播图
    """
    # 打印更新轮播图数据
    print("更新轮播图数据:", carousel_in.dict())
    
    if not carousel_in.id:
        return ResponseUtil.error(msg="轮播图ID不能为空")
    
    result = await CarouselService.update_carousel_services(
        db=query_db,
        carousel_id=carousel_in.id,
        carousel=carousel_in,
        username=current_user.user.user_name
    )
    if result is None:
        return ResponseUtil.error(msg="轮播图不存在")
    elif result is False:
        return ResponseUtil.error(msg="只能修改状态为正常且未过期的轮播图")
    
    return ResponseUtil.success(msg="更新成功")


@carouselController.delete("", dependencies=[Depends(CheckUserInterfaceAuth("h5:carousel:remove"))])
async def delete_carousel(
    request: Request,
    delete_model: DeleteCarouselModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    删除轮播图
    """
    carousel_ids = [int(x) for x in delete_model.carousel_ids.split(",") if x]
    count = await CarouselService.delete_carousel_services(db=query_db, carousel_ids=carousel_ids)
    
    if count == 0:
        return ResponseUtil.error(msg="未删除任何数据")
    
    return ResponseUtil.success(msg=f"成功删除{count}条数据")


@carouselController.delete("/{carousel_id}", dependencies=[Depends(CheckUserInterfaceAuth("h5:carousel:remove"))])
async def delete_carousel_by_id(
    request: Request,
    carousel_id: int = Path(..., description="轮播图ID"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    删除轮播图（逻辑删除，修改状态为停用）
    """
    # 实际上是修改状态为停用（1）
    carousel = await CarouselService.change_carousel_status_services(
        db=query_db, 
        carousel_id=carousel_id, 
        status="1",  # 1表示停用
        username=current_user.user.user_name
    )
    
    if not carousel:
        return ResponseUtil.error(msg="轮播图不存在")
    
    return ResponseUtil.success(msg="删除成功")


@carouselController.put("/changeStatus", dependencies=[Depends(CheckUserInterfaceAuth("h5:carousel:status"))])
async def change_carousel_status(
    request: Request,
    status_model: ChangeStatusModel = Body(...),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    修改轮播图状态
    """
    carousel = await CarouselService.change_carousel_status_services(
        db=query_db, 
        carousel_id=status_model.carousel_id, 
        status=status_model.status, 
        username=current_user.user.user_name
    )
    
    if not carousel:
        return ResponseUtil.error(msg="轮播图不存在")
    
    return ResponseUtil.success(msg="状态修改成功")
