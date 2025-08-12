import React from 'react';
import './ProductGrid.css';

const ProductGrid = ({ items, renderItem, variant = 'list', className = '' }) => {
  return (
    <div className={`product-grid product-grid--${variant} ${className}`.trim()}>
      {items.map((item, index) => (
        <div key={item.id ?? index} className="product-grid__item">
          {renderItem(item, index)}
        </div>
      ))}
    </div>
  );
};

export default ProductGrid;


