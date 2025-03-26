<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { listUser, getUser, delUser, addUser, updateUser, changeUserStatus, userCheckin } from '@/api/h5/user';
import { useDict } from '@/utils/dict';
import dayjs from "dayjs";

const { proxy } = getCurrentInstance();

// 获取字典数据
const { sys_user_status:statusOptions, sys_bind_gitub:bindTypeOptions, sys_play:payTypeOptions, sys_pub_user:levelNameOptions } = useDict('sys_user_status',
                                                                                                     'sys_bind_gitub',
                                                                                                     'sys_play',
                                                                                                     'sys_pub_user');
// 格式化时间的函数
const formatTime = (time) => {
  if (!time) return '--';
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};
const isEdit=ref(false)
// 遮罩层
const loading = ref(false);
// 选中数组
const ids = ref([]);
// 非单个禁用
const single = ref(true);
// 非多个禁用
const multiple = ref(true);
// 显示搜索条件
const showSearch = ref(true);
// 总条数
const total = ref(0);
// 用户表格数据
const userList = ref([]);
// 弹出层标题
const title = ref("");
// 是否显示弹出层
const open = ref(false);
// 查询参数
const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  username: undefined,
  status: undefined,
  bindType: undefined,
  payType: undefined,
  beginTime: undefined,
  endTime: undefined,
});

// 表单参数
const form = reactive({
  userId: undefined,
  username: undefined,
  phone: undefined,
  password: "123456",
  status: "0",
  remark: undefined,
  email: undefined
});

// 表单校验
const rules = ref({
  username: [
    { required: true, message: "登录名不能为空", trigger: "blur" }
  ],
  phone: [
    { required: true, message: "手机号码不能为空", trigger: "blur" },
    { pattern: /^1[3-9]\d{9}$/, message: "请输入正确的手机号码", trigger: "blur" }
  ]
});

// 查询用户列表
const getList = async () => {
  loading.value = true;
  try {
    const response = await listUser(queryParams);
    console.log('API返回的数据结构:', response);
    userList.value = response.data.rows;
    total.value = response.data.total;
  } finally {
    loading.value = false;
  }
};

// 取消按钮
const cancel = () => {
  open.value = false;
  reset();
};

// 表单重置
const reset = () => {
  form.userId = undefined;
  form.username = undefined;
  form.phone = undefined;
  form.password = "123456";
  form.status = "0";
  form.remark = undefined;
  form.email = undefined;
  proxy.resetForm("userForm");
  console.log('重置表单',form);
};

// 搜索按钮操作
const handleQuery = () => {
  queryParams.pageNum = 1;
  getList();
};

// 重置按钮操作
const resetQuery = () => {
  proxy.resetForm("queryForm");
  handleQuery();
};

// 多选框选中数据
const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.userId);
  single.value = selection.length !== 1;
  multiple.value = !selection.length;
};

// 状态修改
const handleStatusChange = async (row) => {
  const userId = row?.userId || ids.value;
  // 切换状态：如果当前是启用(0)，则改为禁用(1)，反之亦然
  const newStatus = row.status === '0' ? '1' : '0';
  const statusText = newStatus === '1' ? '禁用' : '启用';
  
  await ElMessageBox.confirm(`是否确认${statusText}用户编号为${userId}的用户?`);
  await changeUserStatus(userId, newStatus);
  ElMessage.success(`${statusText}成功`);
  getList();
};

// 新增按钮操作
const handleAdd = () => {
  reset();
  open.value = true;
  title.value = "添加用户";
  isEdit.value=false
};

// 修改按钮操作
const handleUpdate = async (row) => {
  reset();
  const userId = row?.userId;
  const response = await getUser(userId);
  Object.assign(form, response.data);
  open.value = true;
  title.value = "修改用户";
  isEdit.value=true
};

// 提交按钮
const submitForm = () => {
  proxy.$refs["userForm"].validate(async valid => {
    if (valid) {
      try {
        // 转换数据格式，确保与后端模型匹配
        const userData = {
          ...form
        };

        // 如果没有昵称，使用用户名作为昵称
        userData.nickname = userData.username;
        
        // 处理email字段，确保不发送空字符串
        if (!userData.email || userData.email === '') {
          delete userData.email; // 完全删除email字段，而不是设置为null
        }
        
        if (form.userId) {
          // 修改用户时，不传递用户名
          delete userData.username;
          await updateUser(userData);
          ElMessage.success("修改成功");
        } else {
          await addUser(userData);
          ElMessage.success("新增成功");
        }
        open.value = false;
        getList();
        // 操作完成后重置表单
        reset();
      } catch (error) {
        console.error("提交表单失败:", error);
        ElMessage.error(error.message || "操作失败");
      }
    }
  });
};

// 用户签到
const handleCheckin = async (row) => {
  try {
    const response = await userCheckin(row.userId);
    ElMessage.success(`签到成功，获得${response.data.expGained}点经验值`);
    getList();
  } catch (error) {
    ElMessage.error(error.message || "签到失败");
  }
};

// 格式化手机号（脱敏）
const formatPhone = (phone) => {
  if (!phone || phone.length !== 11) return phone;
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
};

// 格式化注册天数
const formatRegisterDays = (days) => {
  if (!days) return '0天';
  if (days >= 365) return Math.floor(days / 365) + '年';
  if (days >= 180) return '半年';
  if (days >= 30) return Math.floor(days / 30) + '月';
  return days + '天';
};

// 查看完整手机号
const viewFullPhone = async (row) => {
  try {
    const response = await getUser(row.userId);
    ElMessageBox.alert(response.data.phone, '完整手机号', {
      confirmButtonText: '确定'
    });
  } catch (error) {
    ElMessage.error("获取信息失败");
  }
};


onMounted(() => {
  getList();
});
</script>

<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="登录名" prop="username">
        <el-input
          v-model="queryParams.username"
          placeholder="请输入登录名"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
            <el-form-item label="状态" prop="bindType">
        <el-select v-model="queryParams.status" placeholder="状态" clearable style="width: 240px">
          <el-option
            v-for="dict in statusOptions"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="绑定类型" prop="bindType">
        <el-select v-model="queryParams.bindType" placeholder="绑定类型" clearable style="width: 240px">
          <el-option
            v-for="dict in bindTypeOptions"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="支付类型" prop="payType">
        <el-select v-model="queryParams.payType" placeholder="支付类型" clearable style="width: 240px">
          <el-option
            v-for="dict in payTypeOptions"
             :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="注册时间">
        <el-date-picker
          v-model="dateRange"
          style="width: 240px"
          value-format="YYYY-MM-DD"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery" v-hasPermi="['h5:user:list']">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['h5:user:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['h5:user:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleStatusChange"
          v-hasPermi="['h5:user:remove']"
        >禁用/启用</el-button>
      </el-col>
    </el-row>

    <el-table v-loading="loading" :data="userList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="50" align="center" />
      <el-table-column label="序号" type="index" width="50" align="center" />
      <el-table-column label="登录名" align="center" prop="nickname" />
      <el-table-column label="用户昵称" align="center" prop="nickname" />
      <el-table-column label="邮箱" align="center" prop="email" />
      <el-table-column label="手机号码" align="center" width="120">
        <template #default="scope">
          <el-button link type="primary" @click="viewFullPhone(scope.row)">
            {{ formatPhone(scope.row.phone) }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="注册时间" align="center" width="160">
        <template #default="scope">
          {{ formatTime(scope.row.registerTime) }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" width="160">
        <template #default="scope">
          {{ formatTime(scope.row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column label="等级" align="center" width="100">
        <template #default="scope">
          LV{{ scope.row.level }}
        </template>
      </el-table-column>
      <el-table-column label="签到天数" align="center" width="100">
        <template #default="scope">
          {{ scope.row.checkinDays }} 天
          <el-tag v-if="scope.row.continuousCheckinDays > 0" size="small" type="success">
            连续{{ scope.row.continuousCheckinDays }}天
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="当前IP" align="center" prop="loginIp" />
      <el-table-column label="当前状态" align="center" prop="status" >
        <template #default="scope">
          {{  scope.row.status==="0"?'正常':'禁用'}}
        </template>
      </el-table-column>
      <el-table-column label="注册天数" align="center" width="100">
        <template #default="scope">
          {{ formatRegisterDays(scope.row.registerDays) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200" class-name="small-padding fixed-width">
        <template #default="scope">
           <el-button link type="primary"
                      v-if="scope.row.status==='0'"
                      icon="edit" @click="handleUpdate(scope.row)" v-hasPermi="['h5:user:edit']">
            编辑
          </el-button>
          <el-button link type="primary" icon="Delete" @click="handleStatusChange(scope.row)" v-hasPermi="['h5:user:remove']">
            {{  scope.row.status === '0' ? '正常' : '禁用'}}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改用户对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="userForm" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="登录名" prop="username">
          <el-input v-model="form.username" placeholder="请输入登录名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号码" maxlength="11" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.el-tag + .el-tag {
  margin-left: 10px;
}
</style>