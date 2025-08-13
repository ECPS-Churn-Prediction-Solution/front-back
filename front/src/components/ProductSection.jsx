import React from 'react';
import ProductCard from './ProductCard';
import ProductGrid from './ProductGrid';
import './ProductSection.css';

const ProductSection = () => {
  const products = [
    {
      id: 1,
      image: "https://api.builder.io/api/v1/image/assets/TEMP/414d77028ca2c9c002d9b85c46480f1f01fafe50?width=610",
      category: "V-Neck T-Shirt",
      name: "Embroidered Seersucker Shirt",
      price: "$99",
      colorCount: 5,
      colorSwatch: "#FFF",
      altText: "V-Neck T-Shirt - Embroidered Seersucker Shirt"
    },
    {
      id: 2,
      image: "https://api.builder.io/api/v1/image/assets/TEMP/8583cb89e4be78e73527e097969880aa3c5d452d?width=608",
      category: "Cotton T Shirt",
      name: "Basic Slim Fit T-Shirt",
      price: "$99",
      colorCount: 5,
      colorSwatch: "#FFF",
      altText: "Cotton T Shirt - Basic Slim Fit T-Shirt"
    },
    {
      id: 3,
      image: "https://api.builder.io/api/v1/image/assets/TEMP/e39f353a2cb61a863390e8dd7f307c0befdf0df1?width=608",
      category: "Henley T-Shirt",
      name: "Blurred Print T-Shirt",
      price: "$ 99",
      colorCount: 3,
      colorSwatch: "#DBDCCE",
      altText: "Henley T-Shirt - Blurred Print T-Shirt"
    },
    {
      id: 4,
      image: "https://api.builder.io/api/v1/image/assets/TEMP/e39f353a2cb61a863390e8dd7f307c0befdf0df1?width=608",
      category: "Crewneck T-Shirt",
      name: "Full Sleeve Zipper",
      price: "$ 99",
      colorCount: 2,
      colorSwatch: "#EAE8D9",
      altText: "Crewneck T-Shirt - Full Sleeve Zipper"
    }
  ];

  return (
    <section className="product-section">
      <div className="section-header">
        <h2 className="product-section-title">
          New<br />This week
        </h2>
        <span className="product-count">(50)</span>
      </div>
      
      <ProductGrid
        variant="section"
        items={products}
        renderItem={(product) => (
          <ProductCard
            image={product.image}
            category={product.category}
            name={product.name}
            price={product.price}
            colorCount={product.colorCount}
            colorSwatch={product.colorSwatch}
            altText={product.altText}
          />
        )}
      />
      
      <div className="navigation-controls">
        <button className="nav-btn nav-btn-prev" aria-label="Previous products">
          <div className="nav-btn-border"></div>
          <svg 
            className="nav-icon nav-icon-prev" 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M15 19l-7-7 7-7" stroke="#1E1E1E" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" strokeOpacity="0.7"/>
          </svg>
        </button>
        
        <button className="nav-btn nav-btn-next" aria-label="Next products">
          <div className="nav-btn-border"></div>
          <svg 
            className="nav-icon nav-icon-next" 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M9 5l7 7-7 7" stroke="#1E1E1E" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </section>
  );
};

export default ProductSection;
