import { ElMessage } from 'element-plus';
import { addCarousel, updateCarousel } from '@/api/h5/carousel';

export default function useCarouselSubmit(form, open, loading, getList, uploadFiles) {
  // 表单提交前验证
  const submitForm = async () => {
    try {
      // 表单基本验证
      if (!form.value.title || form.value.title.trim() === '') {
        ElMessage.error('请输入标题');
        return;
      }
      
      if (!form.value.mediaList || form.value.mediaList.length === 0) {
        ElMessage.error('请至少上传一个媒体文件');
        return;
      }

      // 显示提交中
      loading.value = true;

      // 上传媒体文件，获取真实URL
      const uploadedMediaList = await uploadFiles();
      
      // 清理表单数据中的临时属性
      const formData = JSON.parse(JSON.stringify(form.value));
      
      // 使用上传后的媒体列表（如果有上传文件）
      if (uploadedMediaList && uploadedMediaList.length > 0) {
        // 检查是否有上传失败的文件
        const failedUploads = uploadedMediaList.filter(item => item.uploadFailed);
        if (failedUploads.length > 0) {
          ElMessage.warning(`有 ${failedUploads.length} 个文件上传失败，请重试`);
          loading.value = false;
          return false;
        }
        
        // 确保每个媒体项都有URL
        formData.mediaList = formData.mediaList.map(media => {
          // 如果URL为空，但有文件名，则构建一个基于文件名的URL
          if (!media.url && media.name) {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            
            // 构建相对路径URL
            media.url = `/profile/upload/${year}/${month}/${day}/${media.name}`;
          }
          return media;
        });
      }
      
      // 提交表单数据
      let result;
      if (formData.id) {
        // 更新轮播图
        result = await updateCarousel(formData);
      } else {
        // 新增轮播图
        result = await addCarousel(formData);
      }
      
      if (result.code === 200) {
        ElMessage.success(result.msg || '操作成功');
        open.value = false;
        getList();
      } else {
        ElMessage.error(result.msg || '操作失败');
      }
    } catch (error) {
      console.error('提交表单出错:', error);
      ElMessage.error('提交表单出错，请重试');
    } finally {
      loading.value = false;
    }
  };

  return {
    submitForm
  };
}
