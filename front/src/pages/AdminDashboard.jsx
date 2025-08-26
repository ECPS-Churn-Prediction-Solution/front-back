import React, { useMemo, useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './AdminDashboard.css';
import { buildGrafanaBoardUrl } from '../lib/grafana';

const publicUrl = import.meta.env.VITE_GRAFANA_PUBLIC_DASHBOARD_URL;
const baseUrl = import.meta.env.VITE_GRAFANA_BASE_URL;
const uid = import.meta.env.VITE_GRAFANA_DASHBOARD_UID;
const orgId = import.meta.env.VITE_GRAFANA_ORG_ID ? Number(import.meta.env.VITE_GRAFANA_ORG_ID) : undefined;
const theme = import.meta.env.VITE_GRAFANA_THEME || 'light';
const timeFrom = import.meta.env.VITE_GRAFANA_TIME_FROM || 'now-30d';
const timeTo = import.meta.env.VITE_GRAFANA_TIME_TO || 'now';

const AdminDashboard = () => {
  const [range, setRange] = useState('7d');
  const effectiveFrom = useMemo(() => {
    if (range === '7d') return 'now-7d';
    if (range === '14d') return 'now-14d';
    return 'now-30d';
  }, [range]);
  const sanitizeGrafanaUrl = (raw) => {
    try {
      const u = new URL(raw);
      // 경로가 /d/ 인 경우 단일 패널이면 /d-solo/ 로 교체
      if (u.pathname.startsWith('/d/') && (u.searchParams.has('panelId') || u.searchParams.has('viewPanel'))) {
        u.pathname = u.pathname.replace('/d/', '/d-solo/');
      }
      const p = u.searchParams;
      // panelId / viewPanel 양쪽 모두 지원 (삭제하지 않음)
      if (p.has('panelId') && !p.has('viewPanel')) p.set('viewPanel', p.get('panelId'));
      if (p.has('viewPanel') && !p.has('panelId')) p.set('panelId', p.get('viewPanel'));
      if (!p.has('kiosk')) p.set('kiosk', 'tv');
      if (!p.has('theme')) p.set('theme', theme);
      // 기간은 셀렉터 값을 우선 사용
      p.set('from', effectiveFrom);
      p.set('to', 'now');
      // 불필요 파라미터 정리
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

  const churnSeries = useMemo(() => {
    // 목업 라인 차트 데이터 (최근 30일)
    const days = Array.from({ length: 30 }, (_, i) => i).map(i => {
      const d = new Date();
      d.setDate(d.getDate() - (29 - i));
      const label = `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      // 3%~6% 사이 랜덤 곡선
      const base = 3 + (i % 7) * 0.3;
      const noise = (Math.sin(i / 3) + 1) * 0.6;
      const value = Math.min(6.2, Math.max(2.5, base + noise));
      return { label, value };
    });
    return days;
  }, []);

  const chart = useMemo(() => {
    const width = 880;
    const height = 320;
    const padding = { left: 40, right: 20, top: 20, bottom: 40 };
    const innerW = width - padding.left - padding.right;
    const innerH = height - padding.top - padding.bottom;

    const maxV = 6.5;
    const minV = 2.0;
    const xStep = innerW / (churnSeries.length - 1);
    const points = churnSeries.map((p, idx) => {
      const x = padding.left + idx * xStep;
      const y = padding.top + innerH - ((p.value - minV) / (maxV - minV)) * innerH;
      return `${x},${y}`;
    }).join(' ');

    const xTicks = [0, 7, 14, 21, 29];
    const xLabels = xTicks.map(i => ({
      x: padding.left + i * xStep,
      label: churnSeries[i].label
    }));

    const yTicks = [2, 3, 4, 5, 6];
    return { width, height, padding, points, xLabels, yTicks };
  }, [churnSeries]);

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

            <div className="kpi-row">
              <div className="kpi-card large">
                <div className="kpi-title">처리해야 할 제안</div>
                <div className="kpi-value">15 건</div>
                <div className="kpi-badge danger">긴급</div>
                <div className="kpi-sub">처리 필요</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-title">금일 신규 고위험군</div>
                <div className="kpi-value">42 명</div>
                <div className="kpi-delta up">+12% vs 어제</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-title">최근 30일 이탈율</div>
                <div className="kpi-value">5.2%</div>
                <div className="kpi-delta down">-0.8% vs 지난달</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-title">전체 활성 고객</div>
                <div className="kpi-value">15,023 명</div>
                <div className="kpi-delta up">+3.2% vs 지난달</div>
              </div>
            </div>

            <div className="panel-toolbar">
              <div className="panel-title">일자별 고객 이탈율 그래프</div>
              <select className="range-select" value={range} onChange={(e) => setRange(e.target.value)}>
                <option value="7d">최근 7일</option>
                <option value="14d">최근 14일</option>
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
                <div className="panel-title">일자별 고객 이탈율</div>
                <svg width={chart.width} height={chart.height} className="line-chart">
                  <polyline fill="none" stroke="#2563eb" strokeWidth="2" points={chart.points} />
                  {chart.xLabels.map(x => (
                    <text key={x.label} x={x.x} y={chart.height - 10} textAnchor="middle" className="axis-label">{x.label}</text>
                  ))}
                  {chart.yTicks.map(y => (
                    <g key={y}>
                      <text x={10} y={20 + (chart.height - 60) - ((y - 2) * ((chart.height - 60) / 4))} className="axis-label">{y}.0%</text>
                    </g>
                  ))}
                </svg>
              </section>
            )}

            {!publicUrl && (!baseUrl || !uid) && (
              <section className="dashboard-hint">
                <p>
                  Grafana 설정 시 자동으로 임베드가 표시됩니다. 현재는 목업 데이터를 표시 중입니다.
                </p>
              </section>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;


