<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

// 查询参数
const queryParams = ref({
  title: '',
  type: '',
  position: '',
  dateRange: []
});

// 表格数据
const carouselList = ref([]);
const total = ref(0);
const loading = ref(false);
const pageNum = ref(1);
const pageSize = ref(10);

// 弹出层标题
const title = ref('');
const open = ref(false);

// 表单参数
const form = ref({
  id: null,
  title: '',
  type: '',
  category: '',
  isExternalLink: '0',
  position: '1', // 默认为首页
  startTime: '',
  endTime: '',
  mediaList: [
    { type: 'video', url: '', externalLink: '' }
  ],
  detail: '',
  status: '0'
});

// 表单校验规则
const rules = {
  title: [
    { required: true, message: '标题不能为空', trigger: 'blur' },
    { max: 50, message: '标题长度不能超过50个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择轮播类型', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  position: [
    { required: true, message: '请选择显示位置', trigger: 'change' }
  ],
  startTime: [
    { required: true, message: '请选择开始时间', trigger: 'blur' }
  ],
  endTime: [
    { required: true, message: '请选择结束时间', trigger: 'blur' }
  ]
};

// 轮播类型选项
const typeOptions = ref([
  { dictValue: '1', dictLabel: '普通轮播' },
  { dictValue: '2', dictLabel: '活动轮播' },
  { dictValue: '3', dictLabel: '推广轮播' }
]);

// 分类选项
const categoryOptions = ref([
  { value: '1', label: '活动' },
  { value: '2', label: '促销' },
  { value: '3', label: '新品' },
  { value: '4', label: '热门' },
  { value: '5', label: '推荐' }
]);

// 位置选项
const positionOptions = ref([
  { value: '1', label: '首页' },
  { value: '0', label: '其他页面' }
]);

// 是否外部链接选项
const externalLinkOptions = ref([
  { value: '0', label: '否' },
  { value: '1', label: '是' }
]);

// 状态选项
const statusOptions = ref([
  { value: '0', label: '正常' },
  { value: '1', label: '停用' }
]);

// 模拟获取数据
const getList = () => {
  loading.value = true;
  // 这里模拟异步请求
  setTimeout(() => {
    carouselList.value = [
      {
        id: 1,
        title: '新品上市活动',
        type: '2',
        typeName: '活动轮播',
        category: '1',
        categoryName: '活动',
        isExternalLink: '0',
        position: '1',
        positionName: '首页',
        startTime: '2025-03-20 00:00:00',
        endTime: '2025-04-20 23:59:59',
        createTime: '2025-03-24 10:00:00',
        status: '0'
      },
      {
        id: 2,
        title: '春季促销活动',
        type: '2',
        typeName: '活动轮播',
        category: '2',
        categoryName: '促销',
        isExternalLink: '0',
        position: '1',
        positionName: '首页',
        startTime: '2025-03-15 00:00:00',
        endTime: '2025-04-15 23:59:59',
        createTime: '2025-03-14 10:00:00',
        status: '0'
      }
    ];
    total.value = 2;
    loading.value = false;
  }, 300);
};

// 表单重置
const reset = () => {
  form.value = {
    id: null,
    title: '',
    type: '',
    category: '',
    isExternalLink: '0',
    position: '1',
    startTime: '',
    endTime: '',
    mediaList: [
      { type: 'video', url: '', externalLink: '' }
    ],
    detail: '',
    status: '0'
  };
};

// 搜索按钮操作
const handleQuery = () => {
  pageNum.value = 1;
  getList();
};

// 重置按钮操作
const resetQuery = () => {
  queryParams.value = {
    title: '',
    type: '',
    position: '',
    dateRange: []
  };
  handleQuery();
};

// 新增按钮操作
const handleAdd = () => {
  reset();
  open.value = true;
  title.value = '添加轮播图';
};

// 修改按钮操作
const handleUpdate = (row) => {
  reset();
  // 这里模拟获取详情数据
  form.value = {
    id: row.id,
    title: row.title,
    type: row.type,
    category: row.category,
    isExternalLink: row.isExternalLink,
    position: row.position,
    startTime: row.startTime,
    endTime: row.endTime,
    mediaList: [
      { type: 'video', url: 'https://example.com/video1.mp4', externalLink: '' }
    ],
    detail: '<p>这是一个活动详情的富文本内容</p>',
    status: row.status
  };
  open.value = true;
  title.value = '修改轮播图';
};

// 提交按钮
const submitForm = () => {
  ElMessage.success('操作成功');
  open.value = false;
  getList();
};

// 删除按钮操作
const handleDelete = (row) => {
  ElMessageBox.confirm('是否确认删除轮播图名称为"' + row.title + '"的数据项?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功');
    getList();
  }).catch(() => {});
};

// 添加媒体文件
const addMedia = () => {
  if (form.value.mediaList.length >= 9) {
    ElMessage.warning('最多只能上传9个媒体文件');
    return;
  }
  
  // 第一个必须是视频，后面的都是图片
  const mediaType = form.value.mediaList.length === 0 ? 'video' : 'image';
  form.value.mediaList.push({
    type: mediaType,
    url: '',
    externalLink: ''
  });
};

// 删除媒体文件
const removeMedia = (index) => {
  form.value.mediaList.splice(index, 1);
  
  // 如果删除了第一个（视频），则需要确保第一个仍然是视频
  if (index === 0 && form.value.mediaList.length > 0) {
    form.value.mediaList[0].type = 'video';
  }
};

// 文件上传前的验证
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过 10MB!');
    return false;
  }
  return true;
};

// 状态修改
const handleStatusChange = (row) => {
  let text = row.status === "0" ? "启用" : "停用";
  ElMessageBox.confirm('确认要"' + text + '""' + row.title + '"轮播图吗?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = row.status === "0" ? "1" : "0";
    ElMessage.success(text + '成功');
  }).catch(() => {
    row.status = row.status === "0" ? "1" : "0";
  });
};

onMounted(() => {
  getList();
});
</script>

<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="true">
      <el-form-item label="标题" prop="title">
        <el-input
          v-model="queryParams.title"
          placeholder="请输入标题"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="轮播类型" prop="type">
        <el-select v-model="queryParams.type" placeholder="请选择轮播类型" clearable style="width: 200px">
          <el-option
            v-for="dict in typeOptions"
            :key="dict.dictValue"
            :label="dict.dictLabel"
            :value="dict.dictValue"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="显示位置" prop="position">
        <el-select v-model="queryParams.position" placeholder="请选择显示位置" clearable style="width: 200px">
          <el-option
            v-for="item in positionOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="创建时间">
        <el-date-picker
          v-model="queryParams.dateRange"
          style="width: 300px"
          value-format="YYYY-MM-DD"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
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
        >新增</el-button>
      </el-col>
    </el-row>

    <el-table v-loading="loading" :data="carouselList">
      <el-table-column label="ID" align="center" prop="id" />
      <el-table-column label="标题" align="center" prop="title" :show-overflow-tooltip="true" />
      <el-table-column label="轮播类型" align="center" prop="typeName" />
      <el-table-column label="分类" align="center" prop="categoryName" />
      <el-table-column label="显示位置" align="center" prop="positionName" />
      <el-table-column label="开始时间" align="center" prop="startTime" width="160" />
      <el-table-column label="结束时间" align="center" prop="endTime" width="160" />
      <el-table-column label="创建时间" align="center" prop="createTime" width="160" />
      <el-table-column label="状态" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            active-value="0"
            inactive-value="1"
            @change="handleStatusChange(scope.row)"
          ></el-switch>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="150" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-if="total > 0"
      :total="total"
      v-model:page="pageNum"
      v-model:limit="pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改轮播图对话框 -->
    <el-dialog :title="title" v-model="open" width="780px" append-to-body>
      <el-form ref="carouselRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="轮播类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择轮播类型">
            <el-option
              v-for="dict in typeOptions"
              :key="dict.dictValue"
              :label="dict.dictLabel"
              :value="dict.dictValue"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类">
            <el-option
              v-for="item in categoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="显示位置" prop="position">
          <el-select v-model="form.position" placeholder="请选择显示位置">
            <el-option
              v-for="item in positionOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="外部链接" prop="isExternalLink">
          <el-radio-group v-model="form.isExternalLink">
            <el-radio
              v-for="dict in externalLinkOptions"
              :key="dict.value"
              :label="dict.value"
            >{{dict.label}}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="有效时间" prop="time">
          <el-col :span="11">
            <el-date-picker
              v-model="form.startTime"
              type="datetime"
              placeholder="选择开始时间"
              style="width: 100%"
            />
          </el-col>
          <el-col :span="2" class="text-center">-</el-col>
          <el-col :span="11">
            <el-date-picker
              v-model="form.endTime"
              type="datetime"
              placeholder="选择结束时间"
              style="width: 100%"
            />
          </el-col>
        </el-form-item>
        
        <el-divider content-position="center">媒体文件（第一个必须是视频，最多9个）</el-divider>
        
        <div v-for="(media, index) in form.mediaList" :key="index" class="media-item">
          <el-row :gutter="10">
            <el-col :span="6">
              <el-form-item :label="index === 0 ? '视频' : '图片' + index">
                <el-tag v-if="index === 0" type="danger">视频(10MB内)</el-tag>
                <el-tag v-else type="success">图片(PNG,10MB内)</el-tag>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <el-upload
                  :action="'#'"
                  :before-upload="beforeUpload"
                  :auto-upload="false"
                  :limit="1"
                  :accept="index === 0 ? 'video/*' : 'image/png'"
                >
                  <el-button type="primary">选择文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      {{ index === 0 ? '请上传视频文件，且不超过10MB' : '请上传PNG图片，且不超过10MB' }}
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="6" v-if="form.isExternalLink === '1'">
              <el-form-item label="外链地址">
                <el-input v-model="media.externalLink" placeholder="请输入外链地址" />
              </el-form-item>
            </el-col>
            <el-col :span="6" class="text-right">
              <el-button type="danger" icon="Delete" @click="removeMedia(index)">删除</el-button>
            </el-col>
          </el-row>
        </div>
        
        <el-form-item>
          <el-button type="primary" icon="Plus" @click="addMedia">添加媒体</el-button>
          <el-text type="info">最多9个，第一个必须是视频</el-text>
        </el-form-item>
        
        <el-divider content-position="center">详情信息</el-divider>
        
        <el-form-item label="详情" prop="detail">
          <editor v-model="form.detail" :min-height="192" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="open = false">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.media-item {
  margin-bottom: 10px;
  padding: 10px;
  border: 1px dashed #ccc;
  border-radius: 4px;
}
.text-center {
  text-align: center;
}
.text-right {
  text-align: right;
}
</style>