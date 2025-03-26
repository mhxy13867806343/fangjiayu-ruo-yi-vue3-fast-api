import request from '@/utils/request'

// 查询H5用户列表
export function listUser(query) {
  return request({
    url: '/h5/user/list',
    method: 'get',
    params: query
  })
}

// 查询H5用户详细
export function getUser(userId) {
  return request({
    url: `/h5/user/${userId}`,
    method: 'get'
  })
}

// 新增H5用户
export function addUser(data) {
  return request({
    url: '/h5/user',
    method: 'post',
    data: data
  })
}

// 修改H5用户
export function updateUser(data) {
  return request({
    url: `/h5/user/${data.userId}`,
    method: 'put',
    data: data
  })
}

// 删除H5用户
export function delUser(userId) {
  return request({
    url: `/h5/user/${userId}`,
    method: 'delete'
  })
}

// 修改用户状态
export function changeUserStatus(userId, status) {
  const data = {
    user_id: userId,
    status
  }
  return request({
    url: '/h5/user/status/change',
    method: 'put',
    data: data
  })
}

// 用户签到
export function userCheckin(userId) {
  return request({
    url: `/h5/user/checkin/${userId}`,
    method: 'post'
  })
}

// 发布心情
export function createMood(userId, content, status) {
  return request({
    url: `/h5/user/mood/${userId}`,
    method: 'post',
    params: {
      content,
      status
    }
  })
}

// 获取心情列表
export function listMood(query) {
  return request({
    url: '/h5/user/mood/list',
    method: 'get',
    params: query
  })
}

// 更新用户心情
export function updateUserMood(userId, mood) {
  return request({
    url: `/h5/user/mood/${userId}`,
    method: 'put',
    params: {
      mood
    }
  })
}

// 创建支付订单
export function createPayment(userId, amount, payType) {
  return request({
    url: `/h5/user/payment/${userId}`,
    method: 'post',
    params: {
      amount,
      payType
    }
  })
}

// 查询支付状态
export function checkPaymentStatus(orderNo) {
  return request({
    url: `/h5/user/payment/${orderNo}`,
    method: 'get'
  })
}

// 获取验证码
export function getVerifyCode(uuid) {
  return request({
    url: `/h5/user/code/${uuid}`,
    method: 'get'
  })
}

// 发送邮箱验证码
export function sendEmailCode(email) {
  return request({
    url: '/h5/user/email/code',
    method: 'post',
    params: {
      email
    }
  })
}
