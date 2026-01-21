# 博客系统

前后端分离架构，支持用户注册登录、发布文章、评论、图片上传到 OSS。

## 架构

```
用户 → CDN (前端) → Nginx → Django (后端) → OSS (图片)
```

## 后端部署

```bash
cd backend
pip install -r requirements.txt

# 配置 OSS（环境变量）
export OSS_ACCESS_KEY_ID=xxx
export OSS_ACCESS_KEY_SECRET=xxx
export OSS_BUCKET_NAME=xxx
export OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# 初始化数据库
python manage.py migrate

# 开发环境
python manage.py runserver 0.0.0.0:8000

# 生产环境
gunicorn blog_api.wsgi:application -b 0.0.0.0:8000 --workers 4
```

## 前端部署

```bash
cd frontend
npm install

# 开发环境
npm start

# 生产构建
npm run build
# 将 build/ 目录上传到 OSS
```

## API 接口

| 接口 | 方法 | 说明 |
|-----|------|------|
| /api/users/register/ | POST | 注册 |
| /api/users/login/ | POST | 登录 |
| /api/users/profile/ | GET/PUT | 个人信息 |
| /api/posts/ | GET/POST | 文章列表/创建 |
| /api/posts/:id/ | GET/PUT/DELETE | 文章详情 |
| /api/posts/:id/comments/ | POST | 添加评论 |
| /api/posts/upload/ | POST | 上传图片 |
