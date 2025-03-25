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
          return false;
        }
        
        // 创建一个新的媒体列表，避免重复
        const newMediaList = [];
        
        // 首先添加所有已有的媒体（不是blob URL的）
        formData.mediaList.forEach(item => {
          if (item.url && !item.url.startsWith('blob:')) {
            newMediaList.push(item);
          }
        });
        
        // 然后添加所有新上传的媒体
        formData.mediaList.forEach(item => {
          if (item.url && item.url.startsWith('blob:')) {
            const uploadedItem = uploadedMediaList.find(m => m.uid === item.uid);
            if (uploadedItem) {
              newMediaList.push({
                ...item,
                url: uploadedItem.url // 使用上传后的URL
              });
            }
          }
        });
        
        // 更新媒体列表
        formData.mediaList = newMediaList;
      }
      
      // 确保媒体列表中的每个项目都有正确的类型
      formData.mediaList = formData.mediaList.map(item => {
        // 移除临时的file属性
        if (item.file) delete item.file;
        
        // 确保类型字段正确
        if (item.type !== 'video' && item.type !== 'image') {
          // 根据URL判断类型，确保URL存在
          if (item.url) {
            item.type = item.url.match(/\.(mp4|webm|ogg)$/i) ? 'video' : 'image';
          } else {
            item.type = 'image'; // 默认为图片类型
          }
        }
        
        // 确保有name字段
        if (!item.name && item.url) {
          const urlParts = item.url.split('/');
          item.name = urlParts[urlParts.length - 1];
        } else if (!item.name) {
          item.name = '未命名文件_' + Date.now(); // 提供默认文件名
        }
        
        // 确保有url字段
        if (!item.url) {
          item.url = ''; // 提供默认空URL
        }
        
        // 使用驼峰命名法
        return {
          id: item.id,
          carouselId: item.carouselId || formData.id,
          name: item.name,
          url: item.url,
          type: item.type,
          externalLink: item.externalLink || '',
          sort: item.sort || 0
        };
      });
      
      // 直接使用驼峰命名法，不需要转换
      const submitData = {
        ...formData,
        // 确保desc字段被包含
        desc: formData.desc || ''
      };
      
      console.log('提交数据:', submitData);
      console.log('desc字段值:', submitData.desc);
      
      // 提交表单
      try {
        if (submitData.id != null) {
          // 更新
          await updateCarousel(submitData);
          ElMessage.success('修改成功');
        } else {
          // 新增
          await addCarousel(submitData);
          ElMessage.success('新增成功');
        }
        open.value = false;
        loading.value = false;
        getList();
        return true;
      } catch (error) {
        console.error('提交表单失败:', error);
        ElMessage.error('操作失败: ' + (error.message || '未知错误'));
        loading.value = false;
        return false;
      }
    } catch (error) {
      console.error('提交失败:', error);
      ElMessage.error('提交失败：' + (error.message || '未知错误'));
    } finally {
      loading.value = false;
    }
  };

  return {
    submitForm
  };
}
