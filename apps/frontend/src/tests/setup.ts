/**
 * Vitest 测试环境设置
 */
import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'

// 全局配置 Vue Test Utils
config.global.plugins = [ElementPlus]

// Mock Element Plus 图标
vi.mock('@element-plus/icons-vue', () => ({
  UserFilled: 'UserFilled',
  Setting: 'Setting',
  Coin: 'Coin',
  PictureFilled: 'PictureFilled',
  EditPen: 'EditPen',
  Picture: 'Picture',
  FolderOpened: 'FolderOpened',
  Lock: 'Lock',
  User: 'User'
}))

// Mock Vue Router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    go: vi.fn(),
    back: vi.fn(),
    forward: vi.fn()
  }),
  useRoute: () => ({
    path: '/',
    name: 'Home',
    params: {},
    query: {},
    fullPath: '/',
    meta: {}
  })
}))

// 设置测试环境
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})