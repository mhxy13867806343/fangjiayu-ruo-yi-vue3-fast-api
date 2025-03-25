#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
轮播图API接口
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.h5.carousel import (
    CarouselCreate, CarouselUpdate, CarouselOut, CarouselQuery
)
from app.crud.h5.carousel import carousel as carousel_crud
from app.core.security import get_current_username
from app.utils.dict_data import get_dict_label
from app.utils.response import success, fail, ResponseModel

router = APIRouter()


@router.get("/list", response_model=ResponseModel)
def get_carousel_list(
    *,
    db: Session = Depends(deps.get_db),
    title: Optional[str] = Query(None, description="标题"),
    type: Optional[str] = Query(None, description="轮播类型"),
    position: Optional[str] = Query(None, description="显示位置"),
    status: Optional[str] = Query(None, description="状态"),
    date_range: Optional[List[str]] = Query(None, description="创建时间范围"),
    page_num: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100),
) -> Any:
    """
    获取轮播图列表
    """
    # 处理时间范围
    begin_time = None
    end_time = None
    if date_range and len(date_range) == 2:
        begin_time = date_range[0]
        end_time = date_range[1]
    
    # 获取轮播图列表
    carousels = carousel_crud.get_carousels(
        db=db,
        title=title,
        type=type,
        position=position,
        status=status,
        begin_time=begin_time,
        end_time=end_time,
        skip=(page_num - 1) * page_size,
        limit=page_size
    )
    
    # 获取轮播图总数
    total = carousel_crud.get_carousels_count(
        db=db,
        title=title,
        type=type,
        position=position,
        status=status,
        begin_time=begin_time,
        end_time=end_time
    )
    
    # 转换为输出模型
    carousel_list = []
    for c in carousels:
        carousel_out = CarouselOut.from_orm(c)
        # 获取字典标签
        carousel_out.type_name = get_dict_label("sys_carousel_type", c.type)
        carousel_out.category_name = get_dict_label("sys_category", c.category)
        carousel_out.position_name = "首页" if c.position == "1" else "其他页面"
        carousel_list.append(carousel_out)
    
    return success(data={"rows": carousel_list, "total": total})


@router.get("/{carousel_id}", response_model=ResponseModel)
def get_carousel_by_id(
    *,
    db: Session = Depends(deps.get_db),
    carousel_id: int = Path(..., description="轮播图ID"),
) -> Any:
    """
    根据ID获取轮播图详情
    """
    carousel = carousel_crud.get_carousel(db=db, carousel_id=carousel_id)
    if not carousel:
        return fail(msg="轮播图不存在")
    
    # 转换为输出模型
    carousel_out = CarouselOut.from_orm(carousel)
    # 获取字典标签
    carousel_out.type_name = get_dict_label("sys_carousel_type", carousel.type)
    carousel_out.category_name = get_dict_label("sys_category", carousel.category)
    carousel_out.position_name = "首页" if carousel.position == "1" else "其他页面"
    
    return success(data=carousel_out)


@router.post("", response_model=ResponseModel)
def create_carousel(
    *,
    db: Session = Depends(deps.get_db),
    carousel_in: CarouselCreate = Body(...),
    current_user: str = Depends(get_current_username),
) -> Any:
    """
    创建轮播图
    """
    carousel = carousel_crud.create_carousel(
        db=db, 
        carousel_in=carousel_in, 
        current_user=current_user
    )
    
    return success(msg="创建成功")


@router.put("", response_model=ResponseModel)
def update_carousel(
    *,
    db: Session = Depends(deps.get_db),
    carousel_in: CarouselUpdate = Body(...),
    current_user: str = Depends(get_current_username),
) -> Any:
    """
    更新轮播图
    """
    carousel = carousel_crud.get_carousel(db=db, carousel_id=carousel_in.id)
    if not carousel:
        return fail(msg="轮播图不存在")
    
    carousel = carousel_crud.update_carousel(
        db=db, 
        db_carousel=carousel, 
        carousel_in=carousel_in, 
        current_user=current_user
    )
    
    return success(msg="更新成功")


@router.delete("/{carousel_id}", response_model=ResponseModel)
def delete_carousel(
    *,
    db: Session = Depends(deps.get_db),
    carousel_id: int = Path(..., description="轮播图ID"),
) -> Any:
    """
    删除轮播图
    """
    carousel = carousel_crud.get_carousel(db=db, carousel_id=carousel_id)
    if not carousel:
        return fail(msg="轮播图不存在")
    
    carousel_crud.delete_carousel(db=db, db_carousel=carousel)
    
    return success(msg="删除成功")


@router.put("/changeStatus", response_model=ResponseModel)
def change_carousel_status(
    *,
    db: Session = Depends(deps.get_db),
    carousel_id: int = Body(..., embed=True),
    status: str = Body(..., embed=True),
    current_user: str = Depends(get_current_username),
) -> Any:
    """
    更新轮播图状态
    """
    carousel = carousel_crud.get_carousel(db=db, carousel_id=carousel_id)
    if not carousel:
        return fail(msg="轮播图不存在")
    
    carousel = carousel_crud.update_carousel_status(
        db=db, 
        db_carousel=carousel, 
        status=status, 
        current_user=current_user
    )
    
    return success(msg="状态更新成功")
