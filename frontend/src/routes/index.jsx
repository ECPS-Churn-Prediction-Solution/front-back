import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import HomePage from '../pages/HomePage';
import CartPage from '../pages/CartPage';
import ProductDetailPage from '../pages/ProductDetailPage';
import CategoryPage from '../pages/CategoryPage';
import AdminDashboard from '../pages/AdminDashboard';
import NotFound from '../pages/NotFound';

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<MainLayout />}>
      <Route index element={<HomePage />} />
      <Route path="cart" element={<CartPage />} />
      <Route path="product/:id" element={<ProductDetailPage />} />
      <Route path="category/:category" element={<CategoryPage />} />
      <Route path="*" element={<NotFound />} />
    </Route>
    <Route path="/admin" element={<AdminDashboard />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
);

export default AppRoutes;