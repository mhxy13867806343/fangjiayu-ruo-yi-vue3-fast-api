<script setup name="Carousel">
import useCarouselForm from '@/hooks/useCarouselForm';
import useCarouselDate from '@/hooks/useCarouselDate';
import useCarouselMedia from '@/hooks/useCarouselMedia';
import useCarouselDrag from '@/hooks/useCarouselDrag';
import useCarouselList from '@/hooks/useCarouselList';
import useCarouselSubmit from '@/hooks/useCarouselSubmit';
import draggable from 'vuedraggable';
import Editor from '@/components/Editor';

// 引入各个 hooks
const { 
  title, open, loading, typeOptions, categoryOptions, positionOptions, 
  externalLinkOptions, statusOptions, form, rules, reset, cancel 
} = useCarouselForm();

const { disabledStartDate, disabledEndDate, handleStartTimeChange } = useCarouselDate(form);

const { 
  pendingUploadFiles, uploadProgress, beforeUpload, handleExceed, 
  checkFileLimit, handleFileChange, processFile, removeMedia, uploadFiles, resetMedia 
} = useCarouselMedia(form);

const { onDragStart, onDragEnd } = useCarouselDrag();

const { 
  carouselList, total, queryParams, pageNum, pageSize, 
  getList, handleQuery, resetQuery, handleDelete, handleStatusChange 
} = useCarouselList();

const { submitForm } = useCarouselSubmit(form, open, loading, getList);

// 新增按钮操作
const handleAdd = () => {
  reset();
  resetMedia();
  open.value = true;
  title.value = '添加轮播图';
};

// 修改按钮操作
const handleUpdate = (row) => {
  reset();
  resetMedia();
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

// 表单提交
const handleSubmit = () => {
  submitForm(uploadFiles);
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
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
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
              <draggable
                v-model="form.mediaList"
                item-key="uid"
                :component-data="{
                  tag: 'div',
                  class: 'media-grid'
                }"
                handle=".drag-handle"
                ghost-class="ghost-item"
                animation="300"
                @start="onDragStart"
                @end="onDragEnd"
              >
                <template #item="{element, index}">
                  <div class="media-item">
                    <div class="media-preview">
                      <video v-if="element.type === 'video'" :src="element.url" controls class="media-preview-content"></video>
                      <img v-else :src="element.url" class="media-preview-content" />
                    </div>
                    <div class="media-info">
                      <div class="media-name">{{ element.name }}</div>
                      <div class="media-type-tag">
                        <el-tag :type="element.type === 'video' ? 'danger' : 'success'">
                          {{ element.type === 'video' ? '视频' : '图片' }}
                        </el-tag>
                      </div>
                      <el-input v-model="element.externalLink" placeholder="外链地址（可选）" size="small" class="mt10" />
                    </div>
                    <div class="media-actions">
                      <el-button type="primary" icon="Rank" circle class="drag-handle" title="拖动调整顺序"></el-button>
                      <el-button type="danger" icon="Delete" circle @click="removeMedia(index)"></el-button>
                    </div>
                  </div>
                </template>
              </draggable>
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
          <el-button type="primary" @click="handleSubmit">确 定</el-button>
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
  display: block;
  width: 100%;
  margin-bottom: 20px;
}

.media-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  width: 100%;
}

.media-item {
  width: calc(33.33% - 10px);
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: #fff;
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

.ghost-item {
  opacity: 0.5;
  background: #c8ebfb;
  border: 1px dashed #409eff;
}

.drag-handle {
  cursor: move;
  margin-right: 8px;
}
</style>