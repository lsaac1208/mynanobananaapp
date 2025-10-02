import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  // 公开路由
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false }
  },

  // 认证后的路由 - 使用统一布局
  {
    path: '/app',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      // 用户功能路由
      {
        path: '',
        name: 'Generate',
        component: () => import('../views/app/Generate.vue'),
        meta: { title: 'AI生成' }
      },
      {
        path: 'gallery',
        name: 'Gallery',
        component: () => import('../views/app/Gallery.vue'),
        meta: { title: '我的画廊' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/app/Profile.vue'),
        meta: { title: '个人中心' }
      }
    ]
  },

  // 管理员路由 - 使用统一布局
  {
    path: '/admin',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true, requiresRole: 'admin' },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { title: '数据仪表板', requiresRole: 'admin' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/UserManagement.vue'),
        meta: { title: '用户管理', requiresRole: 'admin' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('../views/admin/SystemSettings.vue'),
        meta: { title: '系统设置', requiresRole: 'admin' }
      }
    ]
  },

  // 404路由
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 检查是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresRole = to.matched.some(record => record.meta.requiresRole)
  const requiredRoleName = to.matched.find(record => record.meta.requiresRole)?.meta.requiresRole as string

  if (requiresAuth) {
    // 检查用户是否已登录
    if (!authStore.isLoggedIn) {
      // 尝试初始化认证状态（检查本地存储的token）
      await authStore.initAuth()

      if (!authStore.isLoggedIn) {
        // 未登录，保存原始目标路由，重定向到登录页面
        localStorage.setItem('redirectAfterLogin', to.fullPath)
        next({
          name: 'Login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }

    // 检查是否需要特定角色
    if (requiresRole && requiredRoleName) {
      if (!authStore.hasRole(requiredRoleName)) {
        // 没有所需角色，重定向到用户主页
        next({ path: '/app' })
        return
      }
    }
  }

  // 如果已登录用户访问登录页面，智能重定向
  if (authStore.isLoggedIn && to.name === 'Login') {
    // 检查是否有保存的重定向路径
    const savedRedirect = localStorage.getItem('redirectAfterLogin')
    if (savedRedirect) {
      localStorage.removeItem('redirectAfterLogin')
      next(savedRedirect)
      return
    }

    // 根据用户角色智能跳转
    if (authStore.isAdmin) {
      next({ path: '/admin' })
    } else {
      next({ path: '/app' })
    }
    return
  }

  next()
})

export default router