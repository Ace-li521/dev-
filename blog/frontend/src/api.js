import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// 请求拦截器：自动添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 用户相关
export const register = (data) => api.post('/api/users/register/', data);
export const login = (data) => api.post('/api/users/login/', data);
export const getProfile = () => api.get('/api/users/profile/');

// 文章相关
export const getPosts = () => api.get('/api/posts/');
export const getPost = (id) => api.get(`/api/posts/${id}/`);
export const createPost = (data) => api.post('/api/posts/', data);
export const deletePost = (id) => api.delete(`/api/posts/${id}/`);

// 评论
export const addComment = (postId, content) => api.post(`/api/posts/${postId}/comments/`, { content });

// 上传图片
export const uploadImage = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/posts/upload/', formData);
};

export default api;
