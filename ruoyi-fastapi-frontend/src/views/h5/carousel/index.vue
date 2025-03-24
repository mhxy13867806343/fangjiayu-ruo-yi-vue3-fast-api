<script setup name="Carousel">
import { ref, reactive, toRefs, onMounted, watch, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import Editor from '@/components/Editor';

// 对话框标题
const title = ref('');
// 是否显示对话框
const open = ref(false);
// 表格数据
const carouselList = ref([]);
// 总条数
const total = ref(0);
// 加载状态
const loading = ref(false);
// 查询参数
const queryParams = ref({
  title: '',
  type: '',
  position: '',
  dateRange: []
});

// 页码参数
const pageNum = ref(1);
const pageSize = ref(10);

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

// 表单参数
const form = ref({
  id: null,
  title: '',
  type: '',
  category: '',
  isExternalLink: '0',
  position: '1', // 默认为首页
  url: '', 
  startTime: '',
  endTime: '',
  mediaList: [],
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
  url: [
    { required: true, message: '请输入URL', trigger: 'blur' },
    { 
      pattern: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w.-]*)*\/?$/, 
      message: '请输入有效的URL地址', 
      trigger: 'blur' 
    }
  ],
  startTime: [
    { required: true, message: '请选择开始时间', trigger: 'blur' }
  ],
  endTime: [
    { required: true, message: '请选择结束时间', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value && form.value.startTime) {
          const startTime = new Date(form.value.startTime).getTime();
          const endTime = new Date(value).getTime();
          if (endTime <= startTime) {
            callback(new Error('结束时间必须大于开始时间'));
          } else {
            callback();
          }
        } else {
          callback();
        }
      }, 
      trigger: 'blur' 
    }
  ],
  mediaList: [
    { 
      validator: (rule, value, callback) => {
        if (value.length === 0) {
          callback(new Error('请至少上传一个媒体文件'));
        } else {
          callback();
        }
      }, 
      trigger: 'change' 
    }
  ]
};

// 禁用开始日期（不允许选择过期的时间）
const disabledStartDate = (time) => {
  // 获取当前时间
  const now = new Date();
  // 设置时间为当天的00:00:00
  now.setHours(0, 0, 0, 0);
  // 禁用当前日期之前的日期
  return time.getTime() < now.getTime();
};

// 禁用结束日期（不允许选择比开始时间小的时间）
const disabledEndDate = (time) => {
  if (!form.value.startTime) {
    return true; // 如果没有选择开始时间，则禁用所有日期
  }
  // 获取开始时间
  const startTime = new Date(form.value.startTime);
  // 禁用比开始时间小的日期
  return time.getTime() <= startTime.getTime();
};

// 处理开始时间变化
const handleStartTimeChange = (val) => {
  // 如果开始时间大于结束时间，则清空结束时间
  if (form.value.endTime && new Date(val) >= new Date(form.value.endTime)) {
    form.value.endTime = '';
  }
};

// 待上传的文件列表（只在提交表单时才真正上传）
const pendingUploadFiles = ref([]);

// 上传进度
const uploadProgress = ref({});

// 模拟上传进度
const simulateUploadProgress = (fileId) => {
  uploadProgress.value[fileId] = 0;
  const interval = setInterval(() => {
    if (uploadProgress.value[fileId] < 100) {
      uploadProgress.value[fileId] += 10;
    } else {
      clearInterval(interval);
    }
  }, 300);
};

// 文件上传前的校验
const beforeUpload = (file) => {
  // 检查文件大小
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!');
    return false;
  }
  
  // 检查文件类型
  const isImage = file.type.indexOf('image/') !== -1;
  const isVideo = file.type.indexOf('video/') !== -1;
  if (!isImage && !isVideo) {
    ElMessage.error('只能上传图片或视频文件!');
    return false;
  }
  
  return true;
};

// 处理超出文件数量限制
const handleExceed = (files) => {
  console.log('handleExceed', files);
  // 当选择的文件超过限制时，我们仍然处理它们，但只取前面的部分
  const remainingSlots = 9 - form.value.mediaList.length;
  if (remainingSlots <= 0) {
    ElMessage.warning('已达到最大上传数量9个，无法继续添加');
    return;
  }
  
  // 只处理能够添加的文件数量
  const filesToProcess = Array.from(files).slice(0, remainingSlots);
  // 处理每个文件
  filesToProcess.forEach(file => {
    // 创建一个类似el-upload组件生成的file对象
    const uploadFile = {
      raw: file,
      name: file.name,
      size: file.size,
      status: 'ready',
      uid: Date.now() + '_' + Math.random().toString(36).substr(2, 10)
    };
    processFile(uploadFile);
  });
};

// 检查文件数量限制
const checkFileLimit = () => {
  if (form.value.mediaList.length >= 9) {
    ElMessage.warning('已达到最大上传数量9个，无法继续添加');
    return false;
  }
  return true;
};

// 处理文件变更
const handleFileChange = (file, fileList) => {
  console.log('handleFileChange', file, fileList);
  
  // 如果已经有9个或以上的文件，则不再添加
  if (form.value.mediaList.length >= 9) {
    ElMessage.warning('已达到最大上传数量9个，无法继续添加');
    return;
  }
  
  // 计算还可以添加多少个文件
  const remainingSlots = 9 - form.value.mediaList.length;
  
  // 如果用户一次性选择了多个文件
  if (fileList.length > 1) {
    // 只处理剩余槽位数量的文件
    const filesToProcess = fileList.slice(0, remainingSlots).filter(f => f.status === 'ready');
    
    if (filesToProcess.length > 0) {
      if (fileList.length > remainingSlots) {
        ElMessage.info(`您选择了${fileList.length}个文件，但只能再添加${remainingSlots}个，将自动取前${remainingSlots}个文件`);
      }
      
      // 处理每个文件
      filesToProcess.forEach(f => {
        processFile(f);
      });
    }
    return;
  }
  
  // 处理单个文件的情况
  if (file.status === 'ready') {
    processFile(file);
  }
};

// 处理单个文件的上传和预览
const processFile = (file) => {
  if (beforeUpload(file.raw)) {
    // 模拟上传进度
    simulateUploadProgress(file.uid);
    
    // 本地预览
    setTimeout(() => {
      // 再次检查是否已经达到上限（可能在延迟期间已经添加了其他文件）
      if (form.value.mediaList.length >= 9) {
        delete uploadProgress.value[file.uid];
        return;
      }
      
      const fileUrl = URL.createObjectURL(file.raw);
      const isVideo = file.raw.type.indexOf('video/') !== -1;
      
      // 添加到媒体列表用于预览
      form.value.mediaList.push({
        uid: file.uid,
        name: file.name,
        url: fileUrl,
        type: isVideo ? 'video' : 'image',
        externalLink: '',
        file: file.raw // 保存原始文件对象，用于后续上传
      });
      
      // 添加到待上传文件列表
      pendingUploadFiles.value.push({
        uid: file.uid,
        file: file.raw
      });
      
      // 清除进度
      setTimeout(() => {
        delete uploadProgress.value[file.uid];
      }, 1000);
    }, 1000); // 缩短延迟时间，提高响应速度
  }
};

// 移除媒体文件
const removeMedia = (index) => {
  ElMessageBox.confirm('确定要删除这个媒体文件吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 从待上传列表中移除
    const uid = form.value.mediaList[index].uid;
    if (uid) {
      const fileIndex = pendingUploadFiles.value.findIndex(item => item.uid === uid);
      if (fileIndex !== -1) {
        pendingUploadFiles.value.splice(fileIndex, 1);
      }
    }
    
    // 从预览列表中移除
    form.value.mediaList.splice(index, 1);
    ElMessage.success('删除成功');
  }).catch(() => {
    // 取消删除
  });
};

// 实际上传文件（在表单提交时调用）
const uploadFiles = async () => {
  if (pendingUploadFiles.value.length === 0) {
    return Promise.resolve([]);
  }
  
  // 这里是模拟上传，实际项目中应该调用真实的上传API
  return new Promise((resolve) => {
    const uploadResults = [];
    
    // 模拟异步上传
    setTimeout(() => {
      pendingUploadFiles.value.forEach(item => {
        // 模拟服务器返回的文件URL
        uploadResults.push({
          uid: item.uid,
          url: URL.createObjectURL(item.file),
          name: item.file.name,
          type: item.file.type.indexOf('video/') !== -1 ? 'video' : 'image'
        });
      });
      
      // 清空待上传列表
      pendingUploadFiles.value = [];
      
      resolve(uploadResults);
    }, 1000);
  });
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
    url: '',
    startTime: '',
    endTime: '',
    mediaList: [],
    detail: '',
    status: '0'
  };
  uploadProgress.value = {};
  pendingUploadFiles.value = [];
};

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
        url: 'https://example.com/page1',
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
        url: 'https://example.com/page2',
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
    url: row.url || 'https://example.com/page',
    startTime: row.startTime,
    endTime: row.endTime,
    mediaList: [
      { name: '示例视频', type: 'video', url: 'https://example.com/video1.mp4', externalLink: '' }
    ],
    detail: '<p>这是一个活动详情的富文本内容</p>',
    status: row.status
  };
  open.value = true;
  title.value = '修改轮播图';
};

// 表单提交前验证
const submitForm = () => {
  const carouselRef = ref(null);
  
  nextTick(() => {
    carouselRef.value?.validate(async (valid) => {
      if (valid) {
        if (form.value.mediaList.length === 0) {
          ElMessage.error('请至少上传一个媒体文件');
          return;
        }
        
        // 显示提交中
        loading.value = true;
        
        try {
          // 上传文件
          const uploadResults = await uploadFiles();
          
          // 更新媒体列表中的URL为服务器返回的URL
          if (uploadResults.length > 0) {
            uploadResults.forEach(result => {
              const mediaItem = form.value.mediaList.find(item => item.uid === result.uid);
              if (mediaItem) {
                mediaItem.url = result.url;
                // 移除临时的file属性
                delete mediaItem.file;
              }
            });
          }
          
          // 提交表单
          if (form.value.id != null) {
            // 更新
            ElMessage.success('修改成功');
          } else {
            // 新增
            ElMessage.success('新增成功');
          }
          open.value = false;
          getList();
        } catch (error) {
          ElMessage.error('提交失败：' + error.message);
        } finally {
          loading.value = false;
        }
      }
    });
  });
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

// 取消按钮
const cancel = () => {
  open.value = false;
  reset();
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
      <el-table-column label="URL" align="center" prop="url" />
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
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="carouselRef" :model="form" :rules="rules" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入标题" maxlength="50" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="轮播类型" prop="type">
              <el-select v-model="form.type" placeholder="请选择轮播类型" style="width: 100%">
                <el-option
                  v-for="item in typeOptions"
                  :key="item.dictValue"
                  :label="item.dictLabel"
                  :value="item.dictValue"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row>
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
                <el-option
                  v-for="item in categoryOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示位置" prop="position">
              <el-select v-model="form.position" placeholder="请选择显示位置" style="width: 100%">
                <el-option
                  v-for="item in positionOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row>
          <el-col :span="12">
            <el-form-item label="URL" prop="url">
              <el-input v-model="form.url" placeholder="请输入URL地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="外部链接" prop="isExternalLink">
              <el-radio-group v-model="form.isExternalLink">
                <el-radio
                  v-for="dict in externalLinkOptions"
                  :key="dict.value"
                  :label="dict.value"
                >{{dict.label}}</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row>
          <el-col :span="24">
            <el-form-item label="有效时间" prop="startTime">
              <el-col :span="11">
                <el-date-picker
                  v-model="form.startTime"
                  type="datetime"
                  placeholder="选择开始时间"
                  style="width: 100%"
                  :disabled-date="disabledStartDate"
                  @change="handleStartTimeChange"
                />
              </el-col>
              <el-col :span="2" class="text-center">-</el-col>
              <el-col :span="11">
                <el-date-picker
                  v-model="form.endTime"
                  type="datetime"
                  placeholder="选择结束时间"
                  style="width: 100%"
                  :disabled="!form.startTime"
                  :disabled-date="disabledEndDate"
                />
              </el-col>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="center">媒体文件（最多9个，图片或视频）</el-divider>
        
        <el-form-item prop="mediaList">
          <div class="media-upload-container">
            <!-- 已上传的媒体文件列表 -->
            <div class="media-list">
              <div v-for="(item, index) in form.mediaList" :key="index" class="media-item">
                <div class="media-preview">
                  <video v-if="item.type === 'video'" :src="item.url" controls class="media-preview-content"></video>
                  <img v-else :src="item.url" class="media-preview-content" />
                </div>
                <div class="media-info">
                  <div class="media-name">{{ item.name }}</div>
                  <div class="media-type-tag">
                    <el-tag :type="item.type === 'video' ? 'danger' : 'success'">
                      {{ item.type === 'video' ? '视频' : '图片' }}
                    </el-tag>
                  </div>
                  <el-input v-model="item.externalLink" placeholder="外链地址（可选）" size="small" class="mt10" />
                </div>
                <div class="media-actions">
                  <el-button type="danger" icon="Delete" circle @click="removeMedia(index)"></el-button>
                </div>
              </div>
            </div>
            
            <!-- 上传进度显示 -->
            <div v-for="(progress, fileId) in uploadProgress" :key="fileId" class="upload-progress-item">
              <div class="progress-info">
                <span>上传中...</span>
                <span>{{ progress }}%</span>
              </div>
              <el-progress :percentage="progress" :show-text="false"></el-progress>
            </div>
            
            <!-- 上传按钮 -->
            <div class="upload-button-container" v-if="form.mediaList.length < 9">
              <el-upload
                class="media-uploader"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleFileChange"
                :on-exceed="handleExceed"
                multiple
              >
                <el-button 
                  type="primary" 
                  icon="Plus" 
                  :disabled="form.mediaList.length >= 9"
                >
                  添加媒体文件
                </el-button>
                <template #tip>
                  <div class="el-upload__tip" v-if="form.mediaList.length">
                    已上传 {{ form.mediaList.length }} 个文件，还可上传 {{ 9 - form.mediaList.length }} 个
                  </div>
                  <div class="el-upload__tip">
                    支持视频和图片，单个文件不超过10MB，最多9个文件
                  </div>
                </template>
              </el-upload>
            </div>
          </div>
        </el-form-item>
        
        <!-- 仅当不是首页时显示富文本编辑器 -->
        <div v-if="form.position !== '1'">
          <el-divider content-position="center">详情信息</el-divider>
          <Editor v-model="form.detail" :min-height="192" />
        </div>
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
.media-upload-container {
  margin-bottom: 20px;
}
.media-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}
.media-item {
  width: calc(33.33% - 10px);
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  position: relative;
  transition: all 0.3s;
}
.media-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
.media-preview {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}
.media-preview-content {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.media-info {
  margin-bottom: 10px;
}
.media-name {
  font-size: 14px;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.media-type-tag {
  margin-bottom: 10px;
}
.media-actions {
  position: absolute;
  top: 5px;
  right: 5px;
}
.upload-progress-item {
  margin-bottom: 10px;
  padding: 10px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
  color: #606266;
}
.upload-button-container {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}
.media-uploader {
  width: 100%;
  text-align: center;
}
.text-center {
  text-align: center;
}
.mt10 {
  margin-top: 10px;
}
</style>