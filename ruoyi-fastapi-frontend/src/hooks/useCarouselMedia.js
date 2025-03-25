import { ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

export default function useCarouselMedia(form) {
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

  // 重置媒体相关状态
  const resetMedia = () => {
    uploadProgress.value = {};
    pendingUploadFiles.value = [];
  };

  return {
    pendingUploadFiles,
    uploadProgress,
    beforeUpload,
    handleExceed,
    checkFileLimit,
    handleFileChange,
    processFile,
    removeMedia,
    uploadFiles,
    resetMedia
  };
}
