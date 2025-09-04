import React, { useMemo, useState, useEffect } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './AdminDashboard.css';
import {
  getOverallChurnRate,
  getRfmChurnRate,
  getChurnRiskDistribution,
  getHighRiskUsers,
  approvePolicyAction,
  rejectPolicyAction,
} from '../lib/api';

// Grafana 임베드는 제거되었습니다.

// YYYY-MM-DD 포맷으로 날짜를 반환하는 함수
const getISODate = (date) => {
  return date.toISOString().split('T')[0];
};

const AdminDashboard = () => {
  const [range, setRange] = useState('30d');
  const [dashboardData, setDashboardData] = useState(null);
  const [activeTab, setActiveTab] = useState('risk');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState({});
  const [trend, setTrend] = useState(null);
  const [trendLoading, setTrendLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(50);

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


  const reportDate = useMemo(() => {
    // 더미 데이터 기준일 고정
    const now = new Date('2025-08-29T12:00:00Z');
    return getISODate(now);
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
        getHighRiskUsers(reportDate, horizonDays, page, perPage),
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
  }, [range, reportDate, page, perPage]);


  // 기간 바뀔 때 페이지 초기화
  useEffect(() => { setPage(1); }, [range]);

  // Horizon별 분포 시계열(1/7/15/30)을 가져와 꺾은선 데이터를 만든다
  useEffect(() => {
    const fetchTrend = async () => {
      try {
        setTrendLoading(true);
        const horizons = [1, 7, 15, 30];
        const responses = await Promise.all(
          horizons.map(h => getChurnRiskDistribution(reportDate, h))
        );
        const toBandMap = (dist) => {
          const map = { VH: 0, H: 0, M: 0, L: 0 };
          (dist.bands || []).forEach(b => { map[b.riskBand] = b.ratio; });
          return map;
        };
        const series = responses.map(toBandMap);
        setTrend({ horizons, series });
      } catch (e) {
        console.error(e);
      } finally {
        setTrendLoading(false);
      }
    };
    fetchTrend();
  }, [reportDate]);

  const kpi = dashboardData?.overall;

  // 위험 밴드 분포를 도넛 차트 스타일로 계산
  const bandPercents = useMemo(() => {
    const bands = dashboardData?.distribution?.bands || [];
    const byKey = { VH: 0, H: 0, M: 0, L: 0 };
    bands.forEach(b => {
      byKey[b.riskBand] = Math.round(b.ratio * 1000) / 10; // 한 자리 반올림
    });
    return byKey;
  }, [dashboardData]);

  const donutStyle = useMemo(() => {
    const vh = bandPercents.VH || 0;
    const h = bandPercents.H || 0;
    const m = bandPercents.M || 0;
    const l = bandPercents.L || 0;
    const p1 = vh;
    const p2 = p1 + h;
    const p3 = p2 + m;
    const p4 = p3 + l;
    return {
      background: `conic-gradient(var(--vh) 0% ${p1}%, var(--h) ${p1}% ${p2}%, var(--m) ${p2}% ${p3}%, var(--l) ${p3}% ${p4}%)`
    };
  }, [bandPercents]);

  // Segment Analysis 보조 계산
  const segmentMetrics = useMemo(() => {
    const segments = dashboardData?.rfm?.segments || [];
    const rates = segments.map(s => s.churnRate);
    const maxRate = rates.length ? Math.max(...rates) : 0.2; // 안전한 기본값
    return { segments, maxRate };
  }, [dashboardData]);

  const rateToClass = (rate) => {
    const pct = rate * 100;
    if (pct >= 15) return 'high';
    if (pct >= 8) return 'mid';
    return 'low';
  };

  // 꺾은선 그래프용 path 생성기 (0~1 비율 → y축 픽셀)
  const buildPath = (values, width = 360, height = 140, padding = 12) => {
    const xs = (i) => padding + (i * (width - padding * 2)) / Math.max(1, (values.length - 1));
    const ys = (v) => padding + (1 - v) * (height - padding * 2);
    return values
      .map((v, i) => `${i === 0 ? 'M' : 'L'} ${xs(i)} ${ys(v)}`)
      .join(' ');
  };

  // Trend lines: horizon 변경 시 분포 비율에 따라 선 위치를 변경
  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  const trendLineTops = useMemo(() => {
    return {
      vh: 100 - clamp(bandPercents.VH || 0, 5, 95),
      h: 100 - clamp(bandPercents.H || 0, 5, 95),
      m: 100 - clamp(bandPercents.M || 0, 5, 95),
      l: 100 - clamp(bandPercents.L || 0, 5, 95),
    };
  }, [bandPercents]);

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
                    <div className="kpi-card">
                      <div className="kpi-title">Total Customers</div>
                      <div className="kpi-value">{kpi.customersTotal.toLocaleString()}</div>
                      <div className="kpi-delta">vs last month</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-title">{kpi.horizonDays}-Day Churn Rate</div>
                      <div className="kpi-value">{(kpi.churnRate * 100).toFixed(1)}%</div>
                      <div className="kpi-delta">vs last month</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-title">Retention Rate</div>
                      <div className="kpi-value">{(kpi.retentionRate * 100).toFixed(1)}%</div>
                      <div className="kpi-delta">vs last month</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-title">Churn Customers</div>
                      <div className="kpi-value">{kpi.churnCustomers.toLocaleString()}</div>
                      <div className="kpi-delta">vs yesterday</div>
                    </div>
                  </div>
              )}

              <div className="panel-toolbar">
                <div className="tabs">
                  <button className={`tab ${activeTab === 'risk' ? 'active' : ''}`} onClick={() => setActiveTab('risk')}>위험 분포</button>
                  <button className={`tab ${activeTab === 'segments' ? 'active' : ''}`} onClick={() => setActiveTab('segments')}>세그먼트 분석</button>
                </div>
                <div className="horizon-select">
                  <span>기간:</span>
                  <select className="range-select" value={range} onChange={(e) => setRange(e.target.value)}>
                    <option value="1d">1일</option>
                    <option value="7d">7일</option>
                    <option value="15d">15일</option>
                    <option value="30d">30일</option>
                  </select>
                </div>
              </div>

              {activeTab === 'risk' && (
                <section className="panel split">
                  <div className="split-left">
                    <div className="panel-title">현재 분포</div>
                    <div className="risk-distribution">
                      <div className="donut" style={donutStyle}>
                        <div className="donut-inner">
                          <div className="donut-text">100%</div>
                        </div>
                      </div>
                      <ul className="legend-list">
                        <li className="legend-item vh"><span className="dot"/>Very High Risk <span className="right">{(bandPercents.VH || 0).toFixed(0)}%</span></li>
                        <li className="legend-item h"><span className="dot"/>High Risk <span className="right">{(bandPercents.H || 0).toFixed(0)}%</span></li>
                        <li className="legend-item m"><span className="dot"/>Medium Risk <span className="right">{(bandPercents.M || 0).toFixed(0)}%</span></li>
                        <li className="legend-item l"><span className="dot"/>Low Risk <span className="right">{(bandPercents.L || 0).toFixed(0)}%</span></li>
                      </ul>
                    </div>
                  </div>
                  <div className="split-right">
                    <div className="panel-title">기간별 위험 추세</div>
                    <div className="trend-chart">
                      <svg viewBox="0 0 360 160" preserveAspectRatio="none">
                        <g className="grid">
                          <line x1="0" x2="360" y1="40" y2="40" />
                          <line x1="0" x2="360" y1="80" y2="80" />
                          <line x1="0" x2="360" y1="120" y2="120" />
                        </g>
                        {trend && trend.series && trend.series.length > 0 && (
                          <>
                            <path className="vh" d={buildPath(trend.series.map(s => s.VH || 0))} />
                            <path className="h" d={buildPath(trend.series.map(s => s.H || 0))} />
                            <path className="m" d={buildPath(trend.series.map(s => s.M || 0))} />
                            <path className="l" d={buildPath(trend.series.map(s => s.L || 0))} />
                          </>
                        )}
                      </svg>
                      <div className="trend-x">
                        {(trend?.horizons || [1,7,15,30]).map((h) => (
                          <span key={h}>{h}d</span>
                        ))}
                      </div>
                      <div className="trend-legend">
                        <span className="vh"><span className="dot"/>매우 높음</span>
                        <span className="h"><span className="dot"/>높음</span>
                        <span className="m"><span className="dot"/>보통</span>
                        <span className="l"><span className="dot"/>낮음</span>
                      </div>
                    </div>
                  </div>
                </section>
              )}

              {activeTab === 'segments' && (
                <section className="panel full">
                  <div className="panel-title">RFM 세그먼트 분석</div>
                  <div className="hbar-chart">
                    <div className="hbar-header">
                      <div>Segment</div>
                      <div>Churn Rate</div>
                      <div>Customers</div>
                    </div>
                    {segmentMetrics.segments.map(seg => {
                      const pct = seg.churnRate * 100;
                      const width = Math.max(4, Math.round((seg.churnRate / segmentMetrics.maxRate) * 100));
                      return (
                        <div className="hbar-row" key={seg.bucket}>
                          <div className="hbar-seg">{seg.bucket}</div>
                          <div className="hbar-track" aria-label={`Churn ${pct.toFixed(1)}%`}>
                            <div className={`hbar-fill ${rateToClass(seg.churnRate)}`} style={{ width: `${width}%` }} />
                            <div className="hbar-label">{pct.toFixed(1)}%</div>
                          </div>
                          <div className="hbar-meta">{seg.customers.toLocaleString()}</div>
                        </div>
                      );
                    })}
                    {segmentMetrics.segments.length === 0 && (
                      <div className="empty">세그먼트 데이터가 없습니다.</div>
                    )}
                  </div>
                </section>
              )}

              {false && (
                  <section />
              )}

              {false && <section className="dashboard-hint" />}
              <div className="policy-table-section">
                <div className="panel-title">대응정책 승인 대기</div>
                <div className="policy-toolbar">
                  <div>총 {dashboardData?.highRisk?.total?.toLocaleString?.() || 0}건</div>
                  <div className="policy-controls">
                    <label>표시 개수
                      <select value={perPage} onChange={(e) => { setPerPage(Number(e.target.value)); setPage(1); }} className="range-select" style={{ marginLeft: 6 }}>
                        <option value={10}>10</option>
                        <option value={20}>20</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                    </label>
                    <button className="approve-btn" onClick={() => setPage(p => Math.max(1, p - 1))}>이전</button>
                    <button className="approve-btn" onClick={() => {
                      const total = dashboardData?.highRisk?.total || 0;
                      const maxPage = Math.max(1, Math.ceil(total / perPage));
                      setPage(p => Math.min(maxPage, p + 1));
                    }}>다음</button>
                  </div>
                </div>
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