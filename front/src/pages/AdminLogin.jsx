import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/authContext';
import { apiFetch } from '../lib/api.js';

function AdminLoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { setAuthData } = useAuth(); // login 대신 setAuthData를 사용
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await apiFetch('/api/admin/login', {
                method: 'POST',
                body: { email, password },
            });

            if (response.user && response.user.is_admin) {
                setAuthData(response.user); // 사용자 정보로 인증 상태 직접 설정
                navigate('/admin');
            } else {
                setError('관리자 권한이 없습니다.');
            }
        } catch (err) {
            setError(err.message || '이메일 또는 비밀번호가 올바르지 않습니다.');
            console.error('Admin login failed:', err);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
            <h2>관리자 로그인</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '15px' }}>
                    <label htmlFor="email">이메일</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                    />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label htmlFor="password">비밀번호</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                    />
                </div>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
                    로그인
                </button>
            </form>
        </div>
    );
}

export default AdminLoginPage;
