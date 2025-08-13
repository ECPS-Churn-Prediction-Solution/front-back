import React, { useEffect, useMemo, useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { getMe as mockGetMe } from '../lib/authMock';
import './CheckoutPage.css';
import './MyPage.css';

const MyPage = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    setUser(mockGetMe());
  }, []);

  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="mypage-title">My Page</h1>
        {!user ? (
          <p>로그인이 필요합니다.</p>
        ) : (
          <div className="mypage-card" style={{
            maxWidth: 960,
            margin: '0 auto',
            textAlign: 'left',
            background: 'rgba(255,255,255,0.4)',
            border: '1px solid rgba(0,0,0,0.06)',
            padding: 20,
            borderRadius: 10,
            boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
          }}>
            <h2 style={{ marginBottom: 12 }}>Customer Information</h2>
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

            <h2 style={{ margin: '24px 0 12px' }}>Order History</h2>
            <div className="order-panel">
              <div className="order-list">
                {[1,2].map((n) => (
                  <div key={n} className="order-item">
                    <img src={`https://picsum.photos/seed/m${n}/120/140`} alt={`Order ${n}`} className="order-thumb" />
                    <div className="order-meta">
                      <div className="order-name">Order #{1000+n}</div>
                      <div className="order-variant">2024-01-0{n} · Paid</div>
                    </div>
                    <div className="order-qty">(2)</div>
                    <div className="order-price">$ {(180 + n*5).toFixed(2)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default MyPage;


