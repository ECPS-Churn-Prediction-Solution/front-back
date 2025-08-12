import React from 'react';

const ProductMetaRow = ({
  category,
  name,
  price,
  colorCount,
  colorSwatch,
  className = ''
}) => {
  return (
    <div className={`product-meta-row ${className}`.trim()}>
      {category && <span className="product-category">{category}</span>}
      {name && <span className="product-name">{name}</span>}
      {typeof colorSwatch === 'string' && colorSwatch !== '' && (
        <span className="color-swatch" style={{ backgroundColor: colorSwatch }} />
      )}
      {typeof colorCount === 'number' && colorCount > 0 && (
        <span className="color-count">+{colorCount}</span>
      )}
      {price && <span className="product-price">{price}</span>}
    </div>
  );
};

export default ProductMetaRow;


