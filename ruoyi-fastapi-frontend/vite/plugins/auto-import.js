import AutoImport from 'unplugin-auto-import/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default function createAutoImport() {
    return AutoImport({
        imports: [
            'vue',
            'vue-router',
            'pinia',
            '@vueuse/core'
        ],
        // 解析器
        resolvers: [
            ElementPlusResolver()
        ],
        // 自动导入目录下的模块
        dirs: [
            'src/composables',
            'src/stores'
        ],
        // 自动导入.vue文件中的API
        vueTemplate: true,
        // 配置文件生成位置
        dts: 'src/auto-imports.d.ts',
        // 缓存目录
        cache: false,
        // eslint禁用规则，防止冲突报错
        eslintrc: {
            enabled: true, // 默认false
            filepath: './.eslintrc-auto-import.json', // 默认"./.eslintrc-auto-import.json"
            globalsPropValue: true // 默认true (true | false | 'readonly' | 'readable' | 'writable' | 'writeable')
        }
    })
}
