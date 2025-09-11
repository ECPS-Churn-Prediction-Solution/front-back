// front/src/pages/CouponPage.jsx 파일의 전체 내용을 교체하세요.

import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { useAuth } from '../lib/authContext.jsx';
import { apiFetch } from '../lib/api.js';
import './AdminDashboard.css'; // 스타일 재사용

const CouponPage = () => {
  const { user, loading: authLoading } = useAuth();
  const [coupons, setCoupons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCoupons = async () => {
      if (!user) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const data = await apiFetch('/api/users/my-coupons');
        setCoupons(data || []);
      } catch (err) {
        setError('쿠폰을 불러오는 데 실패했습니다.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (!authLoading) {
      fetchCoupons();
    }
  }, [user, authLoading]);

  const renderContent = () => {
    if (loading || authLoading) {
      return <p>쿠폰을 불러오는 중입니다...</p>;
    }
    if (error) {
      return <p style={{ color: 'red' }}>{error}</p>;
    }
    if (!user) {
      return <p>쿠폰을 보려면 로그인이 필요합니다.</p>;
    }
    if (coupons.length === 0) {
      return <p>사용 가능한 쿠폰이 없습니다.</p>;
    }
    return (
        <div className="policy-table-section" style={{ maxWidth: '960px', margin: '0 auto' }}>
          <table className="policy-table">
            <thead>
            <tr>
              <th>쿠폰 이름</th>
              <th>쿠폰 코드</th>
              <th>할인</th>
              <th>만료 기한</th>
            </tr>
            </thead>
            <tbody>
            {coupons.map(coupon => (
                <tr key={coupon.coupon_id}>
                  <td>{coupon.policy_name}</td>
                  <td>{coupon.coupon_code}</td>
                  <td>{coupon.discount_amount.toLocaleString()}원</td>
                  <td>{new Date(coupon.expires_at).toLocaleString()}</td>
                </tr>
            ))}
            </tbody>
          </table>
        </div>
    );
  };

  return (
      <div className="App">
        <Header />
        <main className="main-content">
          <h1>My Coupons</h1>
          {renderContent()}
        </main>
        <Footer />
      </div>
  );
};

export default CouponPage;