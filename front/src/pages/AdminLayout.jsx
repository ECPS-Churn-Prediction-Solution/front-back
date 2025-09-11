import React from "react";
import { Link, Outlet, NavLink } from "react-router-dom";
import "./AdminLayout.css";

const AdminLayout = () => {
  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="brand">dummymall</div>
        <nav>
          <NavLink to="/admin" end>
            대시보드
          </NavLink>
          <NavLink to="/admin/orders">고객 주문</NavLink>
          <NavLink to="/admin/customers">고객 관리</NavLink>
          <NavLink to="/admin/reviews">고객 리뷰</NavLink>
          <NavLink to="/admin/churn-causes">이탈 고객 주요 원인</NavLink>

          <div className="sidebar-section">OTHERS</div>
          <NavLink to="/admin/admin-list">관리자 리스트</NavLink>
          <NavLink to="/admin/settings">설정</NavLink>
          <NavLink to="/admin/help">도움말</NavLink>
        </nav>
      </aside>

      <div className="admin-main">
        <header className="admin-topbar">
          <input className="search" placeholder="검색" />
          <div className="user">Delicious Burger ▾</div>
        </header>
        <Outlet />
      </div>
    </div>
  );
};

export default AdminLayout;
