import { ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

export default function useCarouselList() {
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
      total.value = carouselList.value.length;
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

  return {
    carouselList,
    total,
    loading,
    queryParams,
    pageNum,
    pageSize,
    getList,
    handleQuery,
    resetQuery,
    handleDelete,
    handleStatusChange
  };
}
