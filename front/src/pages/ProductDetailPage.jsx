import React from 'react';
import { useParams } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';

const ProductDetailPage = () => {
  const { id } = useParams();
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <h1>Product Detail</h1>
        <p>상품 상세 페이지 준비 중 (ID: {id})</p>
      </main>
      <Footer />
    </div>
  );
};

export default ProductDetailPage;


