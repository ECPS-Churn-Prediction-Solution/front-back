import React from 'react';
import { Link } from 'react-router-dom';
import './ProductCard.css';
import ProductMetaRow from './ProductMetaRow';

const ProductCard = ({ 
  id,
  image, 
  category, 
  name, 
  price, 
  colorCount, 
  colorSwatch,
  altText = ""
}) => {
  return (
    <div className="product-card">
      <div className="product-image-container">
        <img 
          src={image} 
          alt={altText}
          className="product-image" 
        />
        <Link to={`/products/${id}`} className="add-to-cart-btn" aria-label={`View ${name}`}>
          <div className="add-btn-background"></div>
          <svg 
            className="add-icon" 
            width="14" 
            height="13" 
            viewBox="0 0 14 13" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path 
              d="M12.667 6.32273L6.66699 6.32273M6.66699 6.32273L0.666992 6.32273M6.66699 6.32273L6.66699 0.774414M6.66699 6.32273L6.66699 11.871" 
              stroke="#0C0C0C" 
              strokeLinecap="round"
            />
          </svg>
        </Link>
      </div>
      
      <div className="product-details">
        <ProductMetaRow
          category={category}
          name={name}
          price={price}
          colorCount={colorCount}
          colorSwatch={colorSwatch}
        />
      </div>
    </div>
  );
};

export default ProductCard;
