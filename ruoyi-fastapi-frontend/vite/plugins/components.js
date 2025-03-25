import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default function createComponents() {
    return Components({
        // 指定组件位置，默认是src/components
        dirs: ['src/components'],
        // ui库解析器
        resolvers: [
            ElementPlusResolver()
        ],
        // 配置文件生成位置
        dts: false,
        // 组件的有效文件扩展名
        extensions: ['vue'],
        // 配置 components 名字的转换规则
        directoryAsNamespace: false,
        // 搜索子目录
        deep: true,
        // 允许子目录作为组件的命名空间前缀
        directoryAsNamespace: true
    })
}
