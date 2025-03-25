import { ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { listCarousel, delCarousel, changeCarouselStatus } from '@/api/h5/carousel';

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

  // 获取轮播图列表数据
  const getList = () => {
    loading.value = true;
    
    listCarousel({
      pageNum: pageNum.value,
      pageSize: pageSize.value,
      title: queryParams.value.title,
      type: queryParams.value.type,
      position: queryParams.value.position,
      dateRange: queryParams.value.dateRange
    }).then(response => {
     const {code,total,rows,msg}=response
      ElMessage[code===200?'success':'error']({
        message: msg,
        type: code===200?'success':'error'
      })
      carouselList.value = rows||[];
      total.value =total ||0
      loading.value = false;
    }).catch(() => {
      loading.value = false;
    });
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
    ElMessageBox.confirm(
      `是否确认删除轮播图"${row.title}"?`,
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    ).then(() => {
      delCarousel(row.id).then(() => {
        ElMessage.success("删除成功");
        getList();
      });
    }).catch(() => {});
  };

  // 状态修改
  const handleStatusChange = (row, newStatus) => {
    let text = newStatus === "0" ? "启用" : "停用";
    
    ElMessageBox.confirm(
      `确认要${text}"${row.title}"吗?`,
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    ).then(() => {
      changeCarouselStatus(row.id, newStatus).then((res) => {
        if(res.code===200){
          ElMessage.success(res.msg);
          // 更新成功后，修改状态值
          row.status = newStatus;
          getList();
        }else{
          ElMessage.error(res.msg);
        }
      }).catch(() => {
        ElMessage.error("修改失败");
      });
    }).catch(() => {
      // 用户取消操作，不做任何处理
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
