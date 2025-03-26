<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户详情</span>
          <el-button type="primary" @click="goBack">返回</el-button>
        </div>
      </template>
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="用户ID">{{ userInfo.userId }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ userInfo.nickname }}</el-descriptions-item>
        <el-descriptions-item label="手机号">
          <span v-if="checkPermission(['admin'])">{{ userInfo.phone }}</span>
          <span v-else>{{ desensitizePhone(userInfo.phone) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userInfo.email }}</el-descriptions-item>
        <el-descriptions-item label="性别">
          {{ userInfo.sex === '0' ? '男' : userInfo.sex === '1' ? '女' : '未知' }}
        </el-descriptions-item>
        <el-descriptions-item label="头像">
          <el-avatar :size="50" :src="userInfo.avatar || defaultAvatar"></el-avatar>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="userInfo.status === '0' ? 'success' : 'danger'">
            {{ userInfo.status === '0' ? '正常' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userInfo.createTime }}</el-descriptions-item>
        <el-descriptions-item label="注册IP">{{ userInfo.registerIp }}</el-descriptions-item>
        <el-descriptions-item label="最后登录时间">{{ userInfo.loginTime }}</el-descriptions-item>
        <el-descriptions-item label="最后登录IP">{{ userInfo.loginIp }}</el-descriptions-item>
      </el-descriptions>

      <el-divider></el-divider>

      <el-descriptions title="等级信息" :column="2" border>
        <el-descriptions-item label="当前等级">
          <el-tag :type="getLevelTagType(userInfo.level)">
            {{ getLevelName(userInfo.level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="经验值">{{ userInfo.experience }}</el-descriptions-item>
        <el-descriptions-item label="签到天数">{{ userInfo.checkinDays }}</el-descriptions-item>
        <el-descriptions-item label="注册天数">{{ userInfo.registerDays }}</el-descriptions-item>
        <el-descriptions-item label="今日是否签到">
          <el-tag :type="userInfo.todayCheckin ? 'success' : 'info'">
            {{ userInfo.todayCheckin ? '已签到' : '未签到' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作">
          <el-button 
            v-if="!userInfo.todayCheckin" 
            type="primary" 
            size="small" 
            @click="handleCheckin"
            :disabled="userInfo.status === '1'"
          >
            签到
          </el-button>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider></el-divider>

      <el-descriptions title="绑定信息" :column="2" border>
        <el-descriptions-item label="绑定类型">
          <el-tag v-if="userInfo.bindType === '0'">未绑定</el-tag>
          <el-tag v-else-if="userInfo.bindType === '1'" type="success">微信</el-tag>
          <el-tag v-else-if="userInfo.bindType === '2'" type="warning">QQ</el-tag>
          <el-tag v-else-if="userInfo.bindType === '3'" type="info">微博</el-tag>
          <el-tag v-else type="danger">其他</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="绑定时间">{{ userInfo.bindTime || '未绑定' }}</el-descriptions-item>
        <el-descriptions-item label="第三方ID">{{ userInfo.thirdPartyId || '未绑定' }}</el-descriptions-item>
        <el-descriptions-item label="第三方昵称">{{ userInfo.thirdPartyName || '未绑定' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider></el-divider>

      <el-descriptions title="支付信息" :column="2" border>
        <el-descriptions-item label="支付类型">
          <el-tag v-if="userInfo.payType === '0'">未支付</el-tag>
          <el-tag v-else-if="userInfo.payType === '1'" type="success">微信支付</el-tag>
          <el-tag v-else-if="userInfo.payType === '2'" type="warning">支付宝</el-tag>
          <el-tag v-else-if="userInfo.payType === '3'" type="info">银联</el-tag>
          <el-tag v-else type="danger">其他</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="支付时间">{{ userInfo.payTime || '未支付' }}</el-descriptions-item>
        <el-descriptions-item label="支付金额">{{ userInfo.payAmount ? `¥${userInfo.payAmount}` : '未支付' }}</el-descriptions-item>
        <el-descriptions-item label="订单号">{{ userInfo.orderNo || '未支付' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider></el-divider>

      <div class="mood-section">
        <div class="section-header">
          <h3>用户心情</h3>
          <el-button type="primary" size="small" @click="openMoodDialog">发布心情</el-button>
        </div>
        <div class="mood-content" v-if="userInfo.mood">
          <el-card shadow="hover">
            <div class="mood-item">
              <div class="mood-text">{{ userInfo.mood }}</div>
              <div class="mood-time">{{ userInfo.moodTime }}</div>
            </div>
          </el-card>
        </div>
        <div class="no-mood" v-else>
          <el-empty description="暂无心情记录"></el-empty>
        </div>
      </div>
    </el-card>

    <!-- 心情发布对话框 -->
    <el-dialog v-model="moodDialogVisible" title="发布心情" width="500px">
      <el-form :model="moodForm" ref="moodFormRef" :rules="moodRules" label-width="80px">
        <el-form-item label="心情内容" prop="content">
          <el-input v-model="moodForm.content" type="textarea" :rows="4" placeholder="请输入心情内容"></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="moodForm.status">
            <el-radio label="0">公开</el-radio>
            <el-radio label="1">私密</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="moodDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitMood">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUser, userCheckin, createMood } from '@/api/h5/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import useUserStore from '@/store/modules/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const userInfo = ref({})
const moodDialogVisible = ref(false)
const moodFormRef = ref(null)

const moodForm = reactive({
  content: '',
  status: '0'
})

const moodRules = {
  content: [
    { required: true, message: '请输入心情内容', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 检查权限
const checkPermission = (permissions) => {
  const roles = userStore.roles
  return roles.some(role => permissions.includes(role))
}

// 获取用户详情
const getUserDetail = async () => {
  try {
    const userId = route.params.id
    const response = await getUser(userId)
    userInfo.value = response.data
  } catch (error) {
    console.error('获取用户详情失败:', error)
    ElMessage.error('获取用户详情失败')
  }
}

// 手机号脱敏
const desensitizePhone = (phone) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 获取等级名称
const getLevelName = (level) => {
  const levelMap = {
    '1': '青铜',
    '2': '白银',
    '3': '黄金',
    '4': '铂金',
    '5': '钻石',
    '6': '星耀',
    '7': '王者'
  }
  return levelMap[level] || '未知'
}

// 获取等级标签类型
const getLevelTagType = (level) => {
  const typeMap = {
    '1': 'info',
    '2': '',
    '3': 'warning',
    '4': 'success',
    '5': 'danger',
    '6': 'warning',
    '7': 'danger'
  }
  return typeMap[level] || ''
}

// 处理签到
const handleCheckin = async () => {
  try {
    await ElMessageBox.confirm('确认为该用户进行签到操作?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await userCheckin(userInfo.value.userId)
    ElMessage.success('签到成功')
    getUserDetail() // 刷新用户信息
  } catch (error) {
    if (error !== 'cancel') {
      console.error('签到失败:', error)
      ElMessage.error('签到失败')
    }
  }
}

// 打开心情对话框
const openMoodDialog = () => {
  moodForm.content = ''
  moodForm.status = '0'
  moodDialogVisible.value = true
}

// 提交心情
const submitMood = async () => {
  if (!moodFormRef.value) return
  
  try {
    await moodFormRef.value.validate()
    
    await createMood(
      userInfo.value.userId,
      moodForm.content,
      moodForm.status
    )
    
    ElMessage.success('心情发布成功')
    moodDialogVisible.value = false
    getUserDetail() // 刷新用户信息
  } catch (error) {
    console.error('心情发布失败:', error)
    if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('心情发布失败')
    }
  }
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}

onMounted(() => {
  getUserDetail()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mood-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.mood-content {
  margin-top: 10px;
}

.mood-item {
  display: flex;
  flex-direction: column;
}

.mood-text {
  font-size: 16px;
  margin-bottom: 8px;
}

.mood-time {
  font-size: 12px;
  color: #999;
  text-align: right;
}

.no-mood {
  padding: 20px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
