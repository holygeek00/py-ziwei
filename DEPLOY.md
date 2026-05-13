# Vercel 部署指南

## 前置要求

1. 安装 Vercel CLI（如果还没安装）：
```bash
npm install -g vercel
```

2. 登录 Vercel 账号：
```bash
vercel login
```

## 部署步骤

### 方法一：使用 Vercel CLI（推荐）

1. 在项目根目录运行：
```bash
vercel
```

2. 首次部署时，Vercel 会询问一些问题：
   - Set up and deploy? → **Yes**
   - Which scope? → 选择你的账号
   - Link to existing project? → **No**
   - What's your project's name? → **py-ziwei** (或自定义)
   - In which directory is your code located? → **./** (当前目录)

3. 部署完成后，Vercel 会提供一个预览 URL

4. 如果满意，部署到生产环境：
```bash
vercel --prod
```

### 方法二：通过 Vercel Dashboard

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 "Add New Project"
3. 导入你的 Git 仓库（GitHub/GitLab/Bitbucket）
4. Vercel 会自动检测配置并部署

## 配置说明

项目已包含以下 Vercel 配置文件：

- `vercel.json` - Vercel 部署配置
- `requirements.txt` - Python 依赖
- `api/index.py` - Serverless function 入口
- `.vercelignore` - 部署时忽略的文件

## 访问路径

部署成功后，你可以通过以下路径访问：

- 主页：`https://your-project.vercel.app/`
- 排盘界面：`https://your-project.vercel.app/report`
- API 文档：`https://your-project.vercel.app/docs`
- API 接口：`https://your-project.vercel.app/api/*`

## 环境变量（可选）

如果需要设置环境变量，可以在 Vercel Dashboard 中配置：

1. 进入项目设置
2. 选择 "Environment Variables"
3. 添加需要的环境变量

## 常见问题

### 1. 部署失败

检查 Vercel 部署日志，确保所有依赖都在 `requirements.txt` 中。

### 2. 静态文件无法访问

确保 `public/` 目录中的文件已正确提交到 Git。

### 3. API 路由 404

检查 `vercel.json` 中的路由配置是否正确。

## 本地测试 Vercel 环境

```bash
vercel dev
```

这会在本地启动一个模拟 Vercel 环境的开发服务器。

## 更新部署

每次推送到 Git 仓库的主分支，Vercel 会自动重新部署（如果启用了 Git 集成）。

或者手动部署：
```bash
vercel --prod
```

## 注意事项

1. Vercel 的 serverless functions 有执行时间限制（免费版 10 秒）
2. 确保所有路径使用相对路径
3. 静态文件应放在 `public/` 目录
4. Python 版本由 Vercel 自动管理（通常是 Python 3.9+）
