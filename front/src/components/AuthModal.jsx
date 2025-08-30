import React, { useEffect, useMemo, useState } from 'react';
import Modal from './Modal';
import './AuthModal.css';
import { useAuth } from '../lib/authContext.jsx';
import { categories } from '../data/categories';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const initialLogin = { email: '', password: '' };
const initialRegister = {
  email: '',
  password: '',
  user_name: '',
  gender: 'other',
  birthdate: '',
  phone_number: ''
};

const AuthModal = ({ isOpen, onClose, defaultTab = 'login', onAuthed }) => {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [loginForm, setLoginForm] = useState(initialLogin);
  const [registerForm, setRegisterForm] = useState(initialRegister);
  const [submitting, setSubmitting] = useState(false);
  const { login, register } = useAuth();
  const [error, setError] = useState('');
  const [selectedCategories, setSelectedCategories] = useState([]);

  const switchTab = (tab) => {
    setActiveTab(tab);
    setError('');
  };

  // 모달이 열릴 때마다 부모의 defaultTab으로 동기화
  useEffect(() => {
    if (isOpen) {
      setActiveTab(defaultTab);
      setError('');
    }
  }, [isOpen, defaultTab]);

  const handleInput = (setter) => (e) => {
    const { name, value } = e.target;
    setter((prev) => ({ ...prev, [name]: value }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await register({ ...registerForm, interest_categories: selectedCategories });
      // Assuming the backend returns { message: "..." }
      // After successful registration, switch to login tab
      setActiveTab('login');
      alert('회원가입이 성공적으로 완료되었습니다.');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const topLevel = useMemo(() => categories.filter(c => c.parent_id == null), []);
  const byParent = useMemo(() => {
    const map = new Map();
    for (const c of categories) {
      if (c.parent_id == null) continue;
      if (!map.has(c.parent_id)) map.set(c.parent_id, []);
      map.get(c.parent_id).push(c);
    }
    return map;
  }, []);

  const toggleCategory = (id) => {
    setSelectedCategories((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const selectParent = (parentId) => {
    const children = byParent.get(parentId) || [];
    const ids = [parentId, ...children.map((c) => c.category_id)];
    const hasAll = ids.every((id) => selectedCategories.includes(id));
    setSelectedCategories((prev) => {
      if (hasAll) return prev.filter((id) => !ids.includes(id));
      const set = new Set(prev.concat(ids));
      return Array.from(set);
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const user = await login(loginForm.email, loginForm.password);
      onAuthed?.(user);
      onClose?.();
      setLoginForm(initialLogin);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={activeTab === 'login' ? '로그인' : '회원가입'} width={520}>
      {/* <div className="auth-tabs">
        {activeTab !== 'login' && (
          <button className="auth-tab" onClick={() => switchTab('login')}>
            로그인
          </button>
        )}
        {activeTab !== 'register' && (
          <button className="auth-tab" onClick={() => switchTab('register')}>
            회원가입
          </button>
        )}
      </div> */}

      {error && <div className="auth-error" role="alert">{error}</div>}

      {activeTab === 'login' ? (
        <form className="auth-form" onSubmit={handleLogin}>
          <label className="auth-label">
            이메일
            <input
              name="email"
              type="email"
              required
              value={loginForm.email}
              onChange={handleInput(setLoginForm)}
              placeholder="you@example.com"
            />
          </label>
          <label className="auth-label">
            비밀번호
            <input
              name="password"
              type="password"
              required
              value={loginForm.password}
              onChange={handleInput(setLoginForm)}
              placeholder="••••••••"
            />
          </label>
          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? '로그인 중…' : '로그인'}
          </button>
        </form>
      ) : (
        <form className="auth-form" onSubmit={handleRegister}>
          <label className="auth-label">
            이메일
            <input
              name="email"
              type="email"
              required
              value={registerForm.email}
              onChange={handleInput(setRegisterForm)}
              placeholder="you@example.com"
            />
          </label>
          <label className="auth-label">
            비밀번호 (6자 이상)
            <input
              name="password"
              type="password"
              minLength={6}
              required
              value={registerForm.password}
              onChange={handleInput(setRegisterForm)}
              placeholder="••••••••"
            />
          </label>

          <label className="auth-label">
            이름
            <input
              name="user_name"
              type="text"
              required
              value={registerForm.user_name}
              onChange={handleInput(setRegisterForm)}
              placeholder="홍길동"
            />
          </label>

          <div className="auth-grid">
            <label className="auth-label">
              성별
              <select
                name="gender"
                value={registerForm.gender}
                onChange={handleInput(setRegisterForm)}
              >
                <option value="male">남성</option>
                <option value="female">여성</option>
                <option value="other">기타</option>
              </select>
            </label>
            <label className="auth-label">
              생년월일
              <input
                name="birthdate"
                type="date"
                required
                value={registerForm.birthdate}
                onChange={handleInput(setRegisterForm)}
              />
            </label>
          </div>

          <label className="auth-label">
            전화번호 (선택)
            <input
              name="phone_number"
              type="tel"
              value={registerForm.phone_number}
              onChange={handleInput(setRegisterForm)}
              placeholder="010-1234-5678"
            />
          </label>

          <div className="auth-field">
            <div className="auth-field-title">관심사 (선택)</div>
            <div className="category-section">
              <div className="category-group">
                {topLevel.map((p) => {
                  const parentId = p.category_id;
                  const childList = byParent.get(parentId) || [];
                  const allIds = [parentId, ...childList.map((c) => c.category_id)];
                  const isAllChecked = allIds.every((id) => selectedCategories.includes(id));
                  return (
                    <div key={parentId} className="category-block">
                      <div className="category-parent">
                        <input
                          id={`cat-${parentId}`}
                          type="checkbox"
                          checked={isAllChecked}
                          onChange={() => selectParent(parentId)}
                        />
                        <label htmlFor={`cat-${parentId}`}>{p.category_name}</label>
                      </div>
                      <div className="category-children">
                        {childList.map((c) => (
                          <div key={c.category_id} className="category-child">
                            <input
                              id={`cat-${c.category_id}`}
                              type="checkbox"
                              checked={selectedCategories.includes(c.category_id)}
                              onChange={() => toggleCategory(c.category_id)}
                            />
                            <label htmlFor={`cat-${c.category_id}`}>{c.category_name}</label>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? '가입 중…' : '가입하기'}
          </button>
        </form>
      )}
    </Modal>
  );
};

export default AuthModal;


