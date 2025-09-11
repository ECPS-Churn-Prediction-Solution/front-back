import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainPage from "./pages/MainPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import PaymentPage from "./pages/PaymentPage";
import OrderSummaryPage from "./pages/OrderSummaryPage";
import CouponPage from "./pages/CouponPage";
import MyPage from "./pages/MyPage";
import ProductListPage from "./pages/ProductListPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import "./App.css";

// Admin 관련 페이지 및 레이아웃 import
import AdminLayout from "./pages/AdminLayout";
import AdminDashboard from "./pages/AdminDashboard";
import AdminListPage from "./pages/AdminListPage";
import AdminLoginPage from "./pages/AdminLogin.jsx"; // 추가

import { AuthProvider } from "./lib/authContext.jsx";
import RouteTracker from "./lib/RouteTracker.jsx";

function App() {
  return (
    <BrowserRouter
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <AuthProvider>
        <RouteTracker />
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/payment" element={<PaymentPage />} />
          <Route path="/order" element={<OrderSummaryPage />} />
          <Route path="/coupon" element={<CouponPage />} />
          <Route path="/me" element={<MyPage />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/products/:id" element={<ProductDetailPage />} />

          {/* 관리자 로그인 페이지 라우트 추가 */}
          <Route path="/admin/login" element={<AdminLoginPage />} />

          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="admin-list" element={<AdminListPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
