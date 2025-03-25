import request from '@/utils/request'

// 查询轮播图列表
export function listCarousel(query) {
  return request({
    url: '/h5/carousel/list',
    method: 'get',
    params: query
  })
}

// 查询轮播图详细
export function getCarousel(carouselId) {
  return request({
    url: '/h5/carousel/' + carouselId,
    method: 'get'
  })
}

// 新增轮播图
export function addCarousel(data) {
  return request({
    url: '/h5/carousel',
    method: 'post',
    data: data
  })
}

// 修改轮播图
export function updateCarousel(data) {
  return request({
    url: '/h5/carousel',
    method: 'put',
    data: data
  })
}

// 删除轮播图
export function delCarousel(carouselId) {
  return request({
    url: '/h5/carousel/' + carouselId,
    method: 'delete'
  })
}

// 修改轮播图状态
export function changeCarouselStatus(carouselId, status) {
  return request({
    url: '/h5/carousel/changeStatus',
    method: 'put',
    data: {
      carousel_id: carouselId,
      status: status
    }
  })
}

// 上传媒体文件
export function uploadMedia(file, overwrite = false) {
  const formData = new FormData();
  formData.append('file', file);
  
  return request({
    url: '/common/upload?overwrite=' + overwrite,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}
