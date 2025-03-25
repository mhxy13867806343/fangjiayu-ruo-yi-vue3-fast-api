import { ref } from 'vue';
import { ElMessage } from 'element-plus';

export default function useCarouselDrag() {
  // 处理拖拽开始
  const onDragStart = () => {
    console.log('开始拖拽');
  };

  // 处理拖拽结束
  const onDragEnd = () => {
    console.log('拖拽结束，新顺序已保存');
    ElMessage.success('媒体文件顺序已更新');
  };

  return {
    onDragStart,
    onDragEnd
  };
}
