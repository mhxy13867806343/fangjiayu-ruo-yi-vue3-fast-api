import { ref } from 'vue';
import { ElMessage } from 'element-plus';

export default function useCarouselDrag(form) {
  // 处理拖拽开始
  const onDragStart = (evt) => {
    console.log('开始拖拽', evt);
    
    // 检查是否是视频，如果是视频则阻止拖拽
    const item = form.value.mediaList[evt.oldIndex];
    if (item && item.type === 'video') {
      evt.preventDefault();
      ElMessage.warning('视频必须保持在第一位，不能移动位置');
      return false;
    }
    
    // 检查目标位置是否会导致视频不在第一位
    const hasVideo = form.value.mediaList.some(item => item.type === 'video');
    if (hasVideo && evt.newIndex === 0) {
      evt.preventDefault();
      ElMessage.warning('视频必须保持在第一位，其他媒体不能移到第一位');
      return false;
    }
  };

  // 处理拖拽结束
  const onDragEnd = (evt) => {
    console.log('拖拽结束，新顺序已保存', evt);
    
    // 确保视频始终在第一位
    const mediaList = form.value.mediaList;
    const videoIndex = mediaList.findIndex(item => item.type === 'video');
    
    if (videoIndex > 0) {
      // 如果视频不在第一位，将其移到第一位
      const videoItem = mediaList.splice(videoIndex, 1)[0];
      mediaList.unshift(videoItem);
      ElMessage.info('视频已自动移到第一位');
    } else {
      ElMessage.success('媒体文件顺序已更新');
    }
  };

  return {
    onDragStart,
    onDragEnd
  };
}
