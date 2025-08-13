import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { getMe as mockGetMe } from '../lib/authMock';

const MyPage = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    setUser(mockGetMe());
  }, []);

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <h1>My Page</h1>
        {!user ? (
          <p>로그인이 필요합니다.</p>
        ) : (
          <div className="mypage-card" style={{
            maxWidth: 560,
            margin: '0 auto',
            textAlign: 'left',
            background: '#fff',
            padding: 20,
            borderRadius: 10,
            boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
          }}>
            <h2 style={{ marginBottom: 12 }}>회원 정보</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', rowGap: 8, columnGap: 12 }}>
              <div>이메일</div>
              <div>{user.email}</div>
              <div>이름</div>
              <div>{user.user_name}</div>
              <div>성별</div>
              <div>{user.gender || '-'}</div>
              <div>생년월일</div>
              <div>{user.birthdate}</div>
              <div>전화번호</div>
              <div>{user.phone_number || '-'}</div>
              <div>가입일</div>
              <div>{new Date(user.created_at).toLocaleString()}</div>
              <div>관심사</div>
              <div>{Array.isArray(user.interest_categories) && user.interest_categories.length ? user.interest_categories.join(', ') : '-'}</div>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default MyPage;


