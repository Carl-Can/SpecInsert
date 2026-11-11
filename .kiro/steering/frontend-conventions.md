---
inclusion: fileMatch
fileMatchPattern: "frontend/src/**/*.{ts,tsx}"
---

# 前端开发规范

## TypeScript 约定

- `tsconfig.app.json` 中开启 `verbatimModuleSyntax`，所有类型导入必须使用 `import type`：
  ```ts
  // ✅ 正确
  import type { Hypothesis, CESAnalysis } from '../types';
  // ❌ 错误
  import { Hypothesis } from '../types';
  ```
- 不引入 `React` 命名空间（项目使用 React 19 自动 JSX 转换）
- 组件 props 必须用 `interface Props` 定义，不用内联类型或 `type Props`

## 组件样式约定

- 样式全部使用内联 `style={{}}`，不新增 `.css` 文件
- 颜色值必须引用 CSS 变量，不硬编码十六进制：
  ```ts
  // ✅ 正确
  color: 'var(--accent-blue)'
  // ✅ 可以（动态计算时）
  color: `rgba(14,165,233,${opacity})`
  // ❌ 避免
  color: '#0ea5e9'
  ```
- 可用 CSS 变量（定义在 `src/index.css`）：
  - `--bg-primary` / `--bg-secondary` / `--bg-card`
  - `--border-color` / `--text-primary` / `--text-secondary` / `--text-muted`
  - `--accent-blue` (#0ea5e9) / `--accent-cyan` (#22d3ee)
  - `--accent-green` (#10b981) / `--accent-green-bright` (#34d399)
  - `--accent-red` (#ef4444) / `--accent-amber` (#f59e0b)
  - `--font-mono`（JetBrains Mono）
- 动画类名（在 `index.css` 中已定义）：`animate-slide-in`、`animate-fade-in`、`animate-pulse-glow`

## 状态管理

- 使用原生 `useState` / `useEffect`，不引入 Redux / Zustand 等
- 核心状态 `DiagnosisState` 定义在 `src/types.ts`，统一在 `App.tsx` 管理
- 子组件只接收 props，不直接调用 `api.ts`（由 `App.tsx` 统一调度）

## API 调用约定

- 所有后端请求通过 `src/api.ts` 封装，组件不直接 `fetch`
- API 基址是 `import.meta.env.VITE_API_BASE_URL`，缺省为 `http://localhost:8000`。不要再把生产地址写死
- SSE 解析：事件必须以 `data: ` 开头，使用 `ReadableStream` + `TextDecoder` 逐块解析
- 健康检查在 `App.tsx` 的 `useEffect` 中启动时执行一次
- 教学免责声明文案放在 `src/disclaimer.ts`，顶部栏、空白板和最终裁决都要能看到。不要加入剧集商标 logo

## 新增组件检查清单

新增组件文件时确认：
- [ ] 文件顶部无 `import React from 'react'`
- [ ] 所有类型导入用 `import type`
- [ ] Props 用 `interface Props` 定义
- [ ] 样式用内联 `style={{}}`，颜色用 CSS 变量
- [ ] 组件在 `Whiteboard.tsx` 或 `App.tsx` 中正确引用
