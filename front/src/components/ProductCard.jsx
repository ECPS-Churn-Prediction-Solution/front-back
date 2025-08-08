import React from 'react';
import './ProductCard.css';

const ProductCard = ({ 
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
        <div className="add-to-cart-btn">
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
        </div>
      </div>
      
      <div className="product-details">
        <div className="product-meta-row">
          <span className="product-category">{category}</span>
          <span className="product-name">{name}</span>
          {colorSwatch && (
            <span 
              className="color-swatch" 
              style={{ backgroundColor: colorSwatch }}
            />
          )}
          {colorCount && <span className="color-count">+{colorCount}</span>}
          <span className="product-price">{price}</span>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
