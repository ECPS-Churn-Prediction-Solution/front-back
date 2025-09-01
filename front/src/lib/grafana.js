// 단순 Grafana 임베드 URL 생성 헬퍼
// 대시보드 uid, 테마, 기간 등을 받아 iframe src를 만들어줍니다.

/**
 * buildGrafanaEmbedUrl
 * @param {Object} params
 * @param {string} params.baseUrl - Grafana 베이스 URL (예: https://grafana.example.com)
 * @param {string} params.dashboardUid - 공개(익명/뷰어) 접근 가능한 대시보드 UID
 * @param {string} [params.theme="light"] - light | dark
 * @param {string} [params.from="now-30d"] - 조회 시작 시점 (예: now-7d)
 * @param {string} [params.to="now"] - 조회 종료 시점
 * @param {string} [params.orgId] - 필요 시 orgId
 * @param {Record<string,string>} [params.vars] - 대시보드 변수 key/value
 * @returns {string}
 */
export function buildGrafanaEmbedUrl({
  baseUrl,
  dashboardUid,
  theme = "light",
  from = "now-30d",
  to = "now",
  orgId,
  vars = {},
}) {
  const url = new URL(`${baseUrl.replace(/\/$/, "")}/d-solo/${dashboardUid}/_`);
  const params = url.searchParams;
  params.set("from", from);
  params.set("to", to);
  params.set("theme", theme);
  params.set("viewPanel", ""); // 개별 패널용. 전체 대시보드는 d/ 경로 사용 권장
  if (orgId) params.set("orgId", String(orgId));
  Object.entries(vars).forEach(([k, v]) => params.set(`var-${k}`, v));
  return url.toString();
}

/**
 * 전체 대시보드 임베드 URL (보통 TV모드/전체 프레임)
 */
export function buildGrafanaBoardUrl({
  baseUrl,
  dashboardUid,
  theme = "light",
  from = "now-30d",
  to = "now",
  orgId,
  vars = {},
}) {
  const url = new URL(`${baseUrl.replace(/\/$/, "")}/d/${dashboardUid}/_`);
  const params = url.searchParams;
  params.set("from", from);
  params.set("to", to);
  params.set("theme", theme);
  if (orgId) params.set("orgId", String(orgId));
  Object.entries(vars).forEach(([k, v]) => params.set(`var-${k}`, v));
  // kiosk 모드로 크롬 UI 제거
  params.set("kiosk", "tv");
  return url.toString();
}


