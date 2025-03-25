import { ref, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useDict } from '@/utils/dict';
import { toRefs } from 'vue';

export default function useCarouselForm() {
  // 对话框标题
  const title = ref('');
  // 是否显示对话框
  const open = ref(false);
  // 加载状态
  const loading = ref(false);

  // 获取字典数据
  const { sys_carousel_type:typeOptions, sys_category:categoryOptions, sys_user_status:statusOptions } = useDict('sys_carousel_type', 'sys_category', 'sys_user_status');
  
  

  // 位置选项
  const positionOptions = ref([
    { value: '1', label: '首页' },
    { value: '0', label: '其他页面' }
  ]);

  // 是否外部链接选项
  const externalLinkOptions = ref([
    { value: '0', label: '否' },
    { value: '1', label: '是' }
  ]);
  // 表单参数
  const form = ref({
    id: null,
    title: '',
    type: '',
    category: '',
    isExternalLink: '0',
    position: '1', // 默认为首页
    url: '',
    startTime: '',
    endTime: '',
    mediaList: [],
    desc: '',
    status: '0'
  });

  // 表单校验规则
  const rules = {
    title: [
      { required: true, message: '标题不能为空', trigger: 'blur' },
      { max: 50, message: '标题长度不能超过50个字符', trigger: 'blur' }
    ],
    type: [
      { required: true, message: '请选择轮播类型', trigger: 'change' }
    ],
    category: [
      { required: true, message: '请选择分类', trigger: 'change' }
    ],
    position: [
      { required: true, message: '请选择显示位置', trigger: 'change' }
    ],
    url: [
      { required: true, message: '请输入URL', trigger: 'blur' },
      {
        pattern: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\w.-]*)*\/?$/,
        message: '请输入有效的URL地址',
        trigger: 'blur'
      }
    ],
    startTime: [
      { required: true, message: '请选择开始时间', trigger: 'blur' }
    ],
    endTime: [
      { required: true, message: '请选择结束时间', trigger: 'blur' },
      {
        validator: (rule, value, callback) => {
          if (value && form.value.startTime) {
            const startTime = new Date(form.value.startTime).getTime();
            const endTime = new Date(value).getTime();
            if (endTime <= startTime) {
              callback(new Error('结束时间必须大于开始时间'));
            } else {
              callback();
            }
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ],
    mediaList: [
      {
        validator: (rule, value, callback) => {
          if (value.length === 0) {
            callback(new Error('请至少上传一个媒体文件'));
          } else {
            callback();
          }
        },
        trigger: 'change'
      }
    ]
  };

  // 表单重置
  const reset = () => {
    form.value = {
      id: null,
      title: '',
      type: '',
      category: '',
      isExternalLink: '0',
      position: '1',
      url: '',
      startTime: '',
      endTime: '',
      mediaList: [],
      desc: '',
      status: '0'
    };
  };

  // 取消按钮
  const cancel = () => {
    open.value = false;
    reset();
  };

  return {
    title,
    open,
    loading,
    typeOptions,
    categoryOptions,
    positionOptions,
    externalLinkOptions,
    statusOptions,
    form,
    rules,
    reset,
    cancel
  };
}
