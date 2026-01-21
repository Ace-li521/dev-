import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import * as api from './api';

// 登录/注册页
function AuthPage({ setUser }) {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ username: '', password: '', email: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = isLogin ? await api.login(form) : await api.register(form);
      localStorage.setItem('token', res.data.token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      setUser(res.data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || '操作失败');
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>{isLogin ? '登录' : '注册'}</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input placeholder="用户名" value={form.username} onChange={e => setForm({...form, username: e.target.value})} required />
          {!isLogin && <input type="email" placeholder="邮箱" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />}
          <input type="password" placeholder="密码" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
          <button className="btn btn-primary" type="submit">{isLogin ? '登录' : '注册'}</button>
        </form>
        <p style={{marginTop: 15, fontSize: 14}}>
          {isLogin ? '没有账号？' : '已有账号？'}
          <a href="#" onClick={() => setIsLogin(!isLogin)}>{isLogin ? '去注册' : '去登录'}</a>
        </p>
      </div>
    </div>
  );
}

// 文章列表
function PostList() {
  const [posts, setPosts] = useState([]);
  useEffect(() => { api.getPosts().then(res => setPosts(res.data)); }, []);

  return (
    <div className="container">
      {posts.map(post => (
        <div className="card" key={post.id}>
          {post.cover && <img src={post.cover} alt="" className="cover-img" />}
          <h2><Link to={`/post/${post.id}`}>{post.title}</Link></h2>
          <p className="meta">作者: {post.author.username} | {new Date(post.created_at).toLocaleDateString()} | {post.comment_count} 评论</p>
        </div>
      ))}
      {posts.length === 0 && <p>暂无文章</p>}
    </div>
  );
}


// 文章详情
function PostDetail({ user }) {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [comment, setComment] = useState('');

  useEffect(() => { api.getPost(id).then(res => setPost(res.data)); }, [id]);

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    await api.addComment(id, comment);
    setComment('');
    api.getPost(id).then(res => setPost(res.data));
  };

  if (!post) return <div className="container">加载中...</div>;

  return (
    <div className="container">
      <div className="card">
        {post.cover && <img src={post.cover} alt="" className="cover-img" />}
        <h2>{post.title}</h2>
        <p className="meta">作者: {post.author.username} | {new Date(post.created_at).toLocaleDateString()}</p>
        <div style={{marginTop: 20, lineHeight: 1.8}} dangerouslySetInnerHTML={{__html: post.content.replace(/\n/g, '<br/>')}} />
      </div>

      <div className="card">
        <h3>评论 ({post.comments.length})</h3>
        {user && (
          <form onSubmit={handleComment} style={{marginTop: 15}}>
            <textarea placeholder="写下你的评论..." value={comment} onChange={e => setComment(e.target.value)} />
            <button className="btn btn-primary" type="submit">发表评论</button>
          </form>
        )}
        {post.comments.map(c => (
          <div className="comment" key={c.id}>
            <strong>{c.author.username}</strong>
            <span className="meta" style={{marginLeft: 10}}>{new Date(c.created_at).toLocaleDateString()}</span>
            <p style={{marginTop: 5}}>{c.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// 发布文章
function CreatePost({ user }) {
  const [form, setForm] = useState({ title: '', content: '', cover: '' });
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await api.uploadImage(file);
      setForm({...form, cover: res.data.url});
    } catch (err) {
      alert('上传失败');
    }
    setUploading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await api.createPost(form);
    navigate('/');
  };

  if (!user) return <div className="container"><p>请先登录</p></div>;

  return (
    <div className="container">
      <div className="card">
        <h2>发布文章</h2>
        <form onSubmit={handleSubmit}>
          <input placeholder="标题" value={form.title} onChange={e => setForm({...form, title: e.target.value})} required />
          <div className="form-group">
            <label>封面图</label>
            <input type="file" accept="image/*" onChange={handleUpload} />
            {uploading && <span>上传中...</span>}
            {form.cover && <img src={form.cover} alt="" style={{maxWidth: 200, marginTop: 10}} />}
          </div>
          <textarea placeholder="内容" value={form.content} onChange={e => setForm({...form, content: e.target.value})} required style={{minHeight: 200}} />
          <button className="btn btn-primary" type="submit">发布</button>
        </form>
      </div>
    </div>
  );
}

// 主应用
function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <BrowserRouter>
      <div className="header">
        <h1><Link to="/" style={{color: '#333', textDecoration: 'none'}}>📝 博客系统</Link></h1>
        <nav>
          {user ? (
            <>
              <span>欢迎, {user.username}</span>
              <Link to="/create">发布文章</Link>
              <a href="#" onClick={logout}>退出</a>
            </>
          ) : (
            <Link to="/auth">登录/注册</Link>
          )}
        </nav>
      </div>
      <Routes>
        <Route path="/" element={<PostList />} />
        <Route path="/auth" element={<AuthPage setUser={setUser} />} />
        <Route path="/post/:id" element={<PostDetail user={user} />} />
        <Route path="/create" element={<CreatePost user={user} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
