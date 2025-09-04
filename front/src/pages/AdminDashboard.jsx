import React, { useMemo, useState, useEffect } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './AdminDashboard.css';
import { buildGrafanaBoardUrl } from '../lib/grafana';
import {
  getOverallChurnRate,
  getRfmChurnRate,
  getChurnRiskDistribution,
  getHighRiskUsers,
  approvePolicyAction,
  rejectPolicyAction,
} from '../lib/api';

const publicUrl = import.meta.env.VITE_GRAFANA_PUBLIC_DASHBOARD_URL;
const baseUrl = import.meta.env.VITE_GRAFANA_BASE_URL;
const uid = import.meta.env.VITE_GRAFANA_DASHBOARD_UID;
const orgId = import.meta.env.VITE_GRAFANA_ORG_ID ? Number(import.meta.env.VITE_GRAFANA_ORG_ID) : undefined;
const theme = import.meta.env.VITE_GRAFANA_THEME || 'light';

// YYYY-MM-DD 포맷으로 날짜를 반환하는 함수
const getISODate = (date) => {
  return date.toISOString().split('T')[0];
};

const AdminDashboard = () => {
  const [range, setRange] = useState('30d');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState({});

  // 정책 승인 핸들러
  const handleApprove = async (userId, policyId) => {
    const actionKey = `${userId}-${policyId}`;
    const reason = prompt("승인 사유를 입력해주세요 :");
    
    if (reason === null) return;
    
    try {
      setActionLoading(prev => ({ ...prev, [actionKey]: 'approving' }));
      
      const result = await approvePolicyAction(userId, policyId, reason || "운영자 승인");
      
      const message = result.message || `'${result.policyName}' 정책이 승인되었습니다.`;
      alert(`✅ 정책 승인 성공하였습니다\n${message}`);
      console.log('승인 완료:', result);
      
      await fetchDashboardData();
      
    } catch (error) {
      console.error('승인 실패:', error);
      alert(`❌ 승인 실패: ${error.message}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: null }));
    }
  };

  // 정책 거절 핸들러
  const handleReject = async (userId, policyId) => {
    const actionKey = `${userId}-${policyId}`;
    const reason = prompt("거절 사유를 입력해주세요 :");
    
    if (reason === null) return;
    
    try {
      setActionLoading(prev => ({ ...prev, [actionKey]: 'rejecting' }));
      
      const result = await rejectPolicyAction(userId, policyId, reason || "운영자 거절");
      
      const message = result.message || `'${result.policyName}' 정책이 거절되었습니다.`;
      alert(`❌ 정책 거절 성공하였습니다\n${message}`);
      console.log('거절 완료:', result);
      
      await fetchDashboardData();
      
    } catch (error) {
      console.error('거절 실패:', error);
      alert(`❌ 거절 실패: ${error.message}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [actionKey]: null }));
    }
  };

  const { effectiveFrom, reportDate } = useMemo(() => {
    // NOTE: Hardcode report date to match dummy data
    const now = new Date('2025-08-29T12:00:00Z'); // Use a fixed date for which dummy data exists
    let days;
    if (range === '7d') days = 7;
    else if (range === '14d') days = 14;
    else days = 30;
    // The 'from' date for Grafana doesn't need to be precise for this case
    return { effectiveFrom: `now-${range}`, reportDate: getISODate(now) };
  }, [range]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const horizonDays = parseInt(range.replace('d', ''), 10);

      const [overall, rfm, distribution, highRisk] = await Promise.all([
        getOverallChurnRate(reportDate, horizonDays),
        getRfmChurnRate(reportDate, horizonDays),
        getChurnRiskDistribution(reportDate, horizonDays),
        getHighRiskUsers(reportDate, horizonDays, 1, 10),
      ]);

      setDashboardData({ overall, rfm, distribution, highRisk });
    } catch (err) {
      setError(err.message || '데이터를 불러오는 데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [range, reportDate]);

  const sanitizeGrafanaUrl = (raw) => {
    try {
      const u = new URL(raw);
      if (u.pathname.startsWith('/d/') && (u.searchParams.has('panelId') || u.searchParams.has('viewPanel'))) {
        u.pathname = u.pathname.replace('/d/', '/d-solo/');
      }
      const p = u.searchParams;
      if (p.has('panelId') && !p.has('viewPanel')) p.set('viewPanel', p.get('panelId'));
      if (p.has('viewPanel') && !p.has('panelId')) p.set('panelId', p.get('viewPanel'));
      if (!p.has('kiosk')) p.set('kiosk', 'tv');
      if (!p.has('theme')) p.set('theme', theme);
      p.set('from', effectiveFrom);
      p.set('to', 'now');
      p.delete('refresh');
      p.delete('timezone');
      p.delete('__feature.dashboardSceneSolo');
      return u.toString();
    } catch (_) {
      return raw;
    }
  };

  const url = publicUrl && publicUrl.length > 0
      ? sanitizeGrafanaUrl(publicUrl)
      : buildGrafanaBoardUrl({
        baseUrl: baseUrl,
        dashboardUid: uid,
        theme: theme,
        from: effectiveFrom,
        to: 'now',
        orgId,
      });

  const kpi = dashboardData?.overall;

  return (
      <div className="App admin-dashboard">
        <div className="admin-shell">
          <aside className="admin-sidebar">
            <div className="brand">dummymall</div>
            <nav>
              <a className="active">대시보드</a>
              <a>고객 주문</a>
              <a>고객 관리</a>
              <a>고객 리뷰</a>
              <a>이탈 고객 주요 원인</a>
              <div className="sidebar-section">OTHERS</div>
              <a>설정</a>
              <a>도움말</a>
            </nav>
          </aside>

          <div className="admin-main">
            <header className="admin-topbar">
              <input className="search" placeholder="검색" />
              <div className="user">Delicious Burger ▾</div>
            </header>

            <main className="dashboard-container">
              <div className="dashboard-header">
                <div>
                  <h1>운영자 대시보드</h1>
                  <div className="dashboard-meta">고객 이탈 방지 관리 시스템</div>
                </div>
              </div>

              {loading && <div className="loading-indicator">데이터를 불러오는 중...</div>}
              {error && <div className="error-message">{error}</div>}

              {!loading && !error && kpi && (
                  <div className="kpi-row">
                    <div className="kpi-card large">
                      <div className="kpi-title">이탈 예측 사용자</div>
                      <div className="kpi-value">{kpi.churnCustomers.toLocaleString()} 명</div>
                      <div className="kpi-badge info">지난 {kpi.horizonDays}일 예측</div>
                      <div className="kpi-sub">전체 {kpi.customersTotal.toLocaleString()}명 중</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-title">전체 이탈률</div>
                      <div className="kpi-value">{(kpi.churnRate * 100).toFixed(1)}%</div>
                      <div className="kpi-delta">({(kpi.retentionRate * 100).toFixed(1)}% 유지)</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-title">RFM 이탈률 (상위)</div>
                      {dashboardData.rfm?.segments?.length > 0 ? (
                          <>
                            <div className="kpi-value">{(dashboardData.rfm.segments[0].churnRate * 100).toFixed(1)}%</div>
                            <div className="kpi-delta up">{dashboardData.rfm.segments[0].bucket}</div>
                          </>
                      ) : (
                          <>
                            <div className="kpi-value">N/A</div>
                            <div className="kpi-delta">데이터 없음</div>
                          </>
                      )}
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-title">고위험 사용자</div>
                      {dashboardData.distribution?.bands?.length > 0 ? (
                          <>
                            <div className="kpi-value">{dashboardData.distribution.bands[0].userCount.toLocaleString()} 명</div>
                            <div className="kpi-delta down">{dashboardData.distribution.bands[0].riskBand} 등급</div>
                          </>
                      ) : (
                          <>
                            <div className="kpi-value">N/A</div>
                            <div className="kpi-delta">데이터 없음</div>
                          </>
                      )}
                    </div>
                  </div>
              )}

              <div className="panel-toolbar">
                <div className="panel-title">일자별 고객 이탈율 그래프</div>
                <select className="range-select" value={range} onChange={(e) => setRange(e.target.value)}>
                  <option value="1d">최근 1일</option>
                  <option value="7d">최근 7일</option>
                  <option value="15d">최근 15일</option>
                  <option value="30d">최근 30일</option>
                </select>
              </div>

              {(publicUrl || (baseUrl && uid)) ? (
                  <section className="dashboard-embed">
                    <iframe
                        title="Grafana Admin Dashboard"
                        src={url}
                        frameBorder="0"
                        loading="lazy"
                        referrerPolicy="no-referrer"
                        allowFullScreen
                    />
                  </section>
              ) : (
                  <section className="panel full">
                    <div className="panel-title">데이터 시각화 영역</div>
                    <div className="placeholder-content">
                      {loading && <p>차트 데이터를 불러오는 중입니다...</p>}
                      {error && <p>차트 데이터를 불러오는 데 실패했습니다: {error}</p>}
                      {!loading && !error && dashboardData && (
                          <p>
                            API 연결이 완료되었습니다. <br/>
                            이 영역에 <code>dashboardData.rfm</code>, <code>dashboardData.distribution</code> 등의 데이터를 사용하여<br/>
                            차트나 테이블을 구현할 수 있습니다.
                          </p>
                      )}
                    </div>
                  </section>
              )}

              {!publicUrl && (!baseUrl || !uid) && !loading && !error && (
                  <section className="dashboard-hint">
                    <p>
                      Grafana가 설정되지 않아 API 기반의 목업 데이터를 표시합니다.
                    </p>
                  </section>
              )}
              <div className="policy-table-section">
                <div className="panel-title">고객별 대응정책 제안</div>
                <table className="policy-table">
                  <thead>
                  <tr>
                    <th>고객 ID</th>
                    <th>위험군</th>
                    <th>대응정책</th>
                    <th>실행</th>
                  </tr>
                  </thead>
                  <tbody>
                  {dashboardData?.highRisk?.items.map(item => {
                    const actionKey = `${item.userId}-${item.action.policyId}`;
                    const isApproving = actionLoading[actionKey] === 'approving';
                    const isRejecting = actionLoading[actionKey] === 'rejecting';
                    const isProcessing = isApproving || isRejecting;
                    
                    return (
                      <tr key={item.userId}>
                        <td>{item.userId}</td>
                        <td>{item.riskBand}</td>
                        <td>{item.action.policy_name}</td>
                        <td>
                          <button 
                            className="approve-btn"
                            onClick={() => handleApprove(item.userId, item.action.policyId)}
                            disabled={isProcessing}
                          >
                            {isApproving ? '승인중...' : '승인'}
                          </button>
                          <button 
                            className="reject-btn"
                            onClick={() => handleReject(item.userId, item.action.policyId)}
                            disabled={isProcessing}
                          >
                            {isRejecting ? '거절중...' : '거절'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                  </tbody>
                </table>
              </div>
            </main>
          </div>
        </div>
      </div>
  );
};

export default AdminDashboard;