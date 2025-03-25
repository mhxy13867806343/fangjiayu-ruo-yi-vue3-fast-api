import { ref, nextTick } from 'vue';
import { ElMessage } from 'element-plus';

export default function useCarouselSubmit(form, open, loading, getList) {
  // 表单提交前验证
  const submitForm = (uploadFiles) => {
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

  return {
    submitForm
  };
}
