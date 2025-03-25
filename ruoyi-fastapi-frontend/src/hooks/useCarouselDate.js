import { ref } from 'vue';

export default function useCarouselDate(form) {
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

  return {
    disabledStartDate,
    disabledEndDate,
    handleStartTimeChange
  };
}
