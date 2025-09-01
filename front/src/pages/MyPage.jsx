import React, { useEffect, useMemo, useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
// import { getMe as mockGetMe } from '../lib/authMock'; // Removed mock import
import './CheckoutPage.css';
import './MyPage.css';
import { useAuth } from '../lib/authContext.jsx';
import { apiFetch } from '../lib/api.js';

const MyPage = () => {
  const { user, loading } = useAuth();
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    const loadOrders = async () => {
      try {
        const res = await apiFetch('/api/orders/', { silent401: true });
        if (res && Array.isArray(res.orders)) {
          setOrders(res.orders);
        } else {
          setOrders([]);
        }
      } catch {
        setOrders([]);
      }
    };
    if (!loading && user) {
      loadOrders();
    } else if (!user) {
      setOrders([]);
    }
  }, [loading, user]);

  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="mypage-title">My Page</h1>
        {loading ? (
          <p>Loading...</p>
        ) : !user ? (
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
                {orders.length === 0 ? (
                  <div style={{ padding: 12, color: '#666' }}>주문 내역이 없습니다.</div>
                ) : (
                  orders.map((o) => {
                    const itemsCount = Array.isArray(o.items) ? o.items.reduce((s, it) => s + (it.quantity || 0), 0) : 0;
                    const firstName = o.items && o.items[0] ? o.items[0].product_name : 'Order';
                    const dateStr = o.order_date ? new Date(o.order_date).toLocaleString() : '';
                    const thumb = `https://picsum.photos/seed/ord${o.order_id}/120/140`;
                    const amount = Number(o.total_amount || 0).toFixed(2);
                    return (
                      <div key={o.order_id} className="order-item">
                        <img src={thumb} alt={`Order ${o.order_id}`} className="order-thumb" />
                        <div className="order-meta">
                          <div className="order-name">Order #{o.order_id} · {firstName}</div>
                          <div className="order-variant">{dateStr} · {o.status}</div>
                        </div>
                        <div className="order-qty">({itemsCount})</div>
                        <div className="order-price">₩ {amount}</div>
                      </div>
                    );
                  })
                )}
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