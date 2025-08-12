import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './ProductListPage.css';
import ProductGrid from '../components/ProductGrid';
import ProductMetaRow from '../components/ProductMetaRow';

const ProductListPage = () => {
  const [selectedSizes, setSelectedSizes] = useState([]);
  const [availabilityFilters, setAvailabilityFilters] = useState({
    availability: false,
    outOfStock: false
  });
  const [expandedSections, setExpandedSections] = useState({
    availability: true,
    category: true,
    colors: true,
    priceRange: true,
    collections: true,
    tags: true,
    ratings: true
  });

  // Sidebar filter selections
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedColors, setSelectedColors] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [selectedCollections, setSelectedCollections] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [selectedRatings, setSelectedRatings] = useState([]);

  const sizes = ['XS', 'S', 'M', 'L', 'XL', '2X'];
  const categoryTags = [
    { label: 'New', active: true },
    { label: 'Shirts', active: false },
    { label: 'Polo Shirts', active: false },
    { label: 'Shorts', active: false },
    { label: 'Suits', active: false },
    { label: 'Best sellers', active: false },
    { label: 'T-Shirts', active: false },
    { label: 'Jeans', active: false },
    { label: 'Jackets', active: false },
    { label: 'Coats', active: false }
  ];

  // Sidebar options
  const categoryOptions = ['Shirts', 'T-Shirts', 'Jeans', 'Jackets', 'Coats', 'Polo Shirts'];
  const colorOptions = [
    { name: 'White', value: '#FFFFFF' },
    { name: 'Beige', value: '#EAE8D9' },
    { name: 'Olive', value: '#DBDCCE' },
    { name: 'Black', value: '#000000' },
    { name: 'Grey', value: '#D7D7D7' },
    { name: 'Blue', value: '#3A66CC' },
  ];
  const collectionOptions = ['New', 'Best sellers', 'Summer', 'Winter'];
  const tagOptions = ['Casual', 'Formal', 'Outdoor', 'Office', 'Holiday', 'Limited'];
  const ratingOptions = [5, 4, 3, 2, 1];

  const products = [
    {
      id: 1,
      image: 'https://api.builder.io/api/v1/image/assets/TEMP/28aaf2ba5e88328230c826a33d6b366fa79e0d26?width=530',
      category: 'T-Shirt',
      name: 'Slim Fit Tee',
      price: '$99',
      colorCount: 3,
      colorSwatch: '#DBDCCE',
      altText: 'Slim Fit Tee'
    },
    {
      id: 2,
      image: 'https://api.builder.io/api/v1/image/assets/TEMP/1d2fa53212fad3ac0e7a3879941e28198d597d27?width=530',
      category: 'Shirt',
      name: 'Oxford Shirt',
      price: '$129',
      colorCount: 2,
      colorSwatch: '#EAE8D9',
      altText: 'Oxford Shirt'
    },
    {
      id: 3,
      image: 'https://api.builder.io/api/v1/image/assets/TEMP/76264e2f906385fbf7ef33d77775adfc04b54481?width=530',
      category: 'Polo',
      name: 'Classic Polo',
      price: '$89',
      colorCount: 4,
      colorSwatch: '#FFF',
      altText: 'Classic Polo'
    },
    {
      id: 4,
      image: 'https://api.builder.io/api/v1/image/assets/TEMP/9d4fb13e41340ce70069ddc8d73ff1099ff3794a?width=530',
      category: 'Jacket',
      name: 'Lightweight Jacket',
      price: '$199',
      colorCount: 2,
      colorSwatch: '#DBDCCE',
      altText: 'Lightweight Jacket'
    },
    {
      id: 5,
      image: 'https://api.builder.io/api/v1/image/assets/TEMP/65eb82da31b7df60666ebbe29b6ee0f84f395361?width=530',
      category: 'Jeans',
      name: 'Regular Fit Jeans',
      price: '$149',
      colorCount: 3,
      colorSwatch: '#EAE8D9',
      altText: 'Regular Fit Jeans'
    },
    {
      id: 6,
      image: 'https://api.builder.io/api/v1/image/assets/TEMP/1f9216617eb9dbed992e6a9ad07bd892e85ff2ab?width=530',
      category: 'Coat',
      name: 'Wool Coat',
      price: '$249',
      colorCount: 1,
      colorSwatch: '#FFF',
      altText: 'Wool Coat'
    }
  ];

  const toggleSize = (size) => {
    setSelectedSizes(prev => 
      prev.includes(size) 
        ? prev.filter(s => s !== size)
        : [...prev, size]
    );
  };

  const toggleAvailability = (type) => {
    setAvailabilityFilters(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const toggleFromList = (value, list, setList) => {
    setList(prev => prev.includes(value) ? prev.filter(v => v !== value) : [...prev, value]);
  };

  const onPriceChange = (field, val) => {
    const onlyNum = val.replace(/[^0-9]/g, '');
    setPriceRange(prev => ({ ...prev, [field]: onlyNum }));
  };

  return (
    <div className="App">
      <Header />
      <main className="products-main">
        <div className="breadcrumb-section">
          <span className="breadcrumb-home">Home</span>
          <span className="breadcrumb-current"> / Products</span>
        </div>
        
        <h1 className="products-title">PRODUCTS</h1>
        
        <div className="products-container">
          <aside className="filters-sidebar">
            <h2 className="filters-title">Filters</h2>
            
            <div className="size-section">
              <h3 className="filter-section-title">Size</h3>
              <div className="size-grid">
                {sizes.map(size => (
                  <button
                    key={size}
                    className={`size-button ${selectedSizes.includes(size) ? 'selected' : ''}`}
                    onClick={() => toggleSize(size)}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            <div className="availability-section">
              <div className="filter-section-header" onClick={() => toggleSection('availability')}>
                <h3 className="filter-section-title">Availability</h3>
                <svg 
                  className={`section-arrow ${expandedSections.availability ? 'expanded' : ''}`}
                  width="10" height="7" viewBox="0 0 10 7" fill="none" xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M9.5 6L5 1L0.5 6" stroke="black" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              
              {expandedSections.availability && (
                <div className="availability-options">
                  <label className="availability-option">
                    <input
                      type="checkbox"
                      checked={availabilityFilters.availability}
                      onChange={() => toggleAvailability('availability')}
                    />
                    Availability <span className="count">(450)</span>
                  </label>
                  <label className="availability-option">
                    <input
                      type="checkbox"
                      checked={availabilityFilters.outOfStock}
                      onChange={() => toggleAvailability('outOfStock')}
                    />
                    Out Of Stack <span className="count">(18)</span>
                  </label>
                </div>
              )}
            </div>

            <div className="filter-sections">
              {['category', 'colors', 'priceRange', 'collections', 'tags', 'ratings'].map(section => {
                const isExpanded = expandedSections[section];
                const title = section === 'priceRange' ? 'Price Range' : section.charAt(0).toUpperCase() + section.slice(1);
                return (
                  <div key={section} className="filter-section">
                    <div className="filter-section-header" onClick={() => toggleSection(section)}>
                      <h3 className="filter-section-title">{title}</h3>
                      <svg 
                        className={`section-arrow ${isExpanded ? 'expanded' : ''}`}
                        width="10" height="7" viewBox="0 0 10 7" fill="none" xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M9.5 6L5 1L0.5 6" stroke="black" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>

                    {isExpanded && section === 'category' && (
                      <div className="filter-options">
                        {categoryOptions.map(opt => (
                          <label key={opt} className="filter-option">
                            <input
                              type="checkbox"
                              checked={selectedCategories.includes(opt)}
                              onChange={() => toggleFromList(opt, selectedCategories, setSelectedCategories)}
                            />
                            {opt}
                          </label>
                        ))}
                      </div>
                    )}

                    {isExpanded && section === 'colors' && (
                      <div className="color-palette">
                        {colorOptions.map(c => (
                          <button
                            key={c.value}
                            className={`color-swatch-filter ${selectedColors.includes(c.value) ? 'selected' : ''}`}
                            style={{ backgroundColor: c.value }}
                            aria-label={c.name}
                            onClick={() => toggleFromList(c.value, selectedColors, setSelectedColors)}
                          />
                        ))}
                      </div>
                    )}

                    {isExpanded && section === 'priceRange' && (
                      <div className="price-range">
                        <input
                          className="price-input"
                          inputMode="numeric"
                          placeholder="Min"
                          value={priceRange.min}
                          onChange={(e) => onPriceChange('min', e.target.value)}
                        />
                        <span className="price-separator">-</span>
                        <input
                          className="price-input"
                          inputMode="numeric"
                          placeholder="Max"
                          value={priceRange.max}
                          onChange={(e) => onPriceChange('max', e.target.value)}
                        />
                      </div>
                    )}

                    {isExpanded && section === 'collections' && (
                      <div className="filter-options">
                        {collectionOptions.map(opt => (
                          <label key={opt} className="filter-option">
                            <input
                              type="checkbox"
                              checked={selectedCollections.includes(opt)}
                              onChange={() => toggleFromList(opt, selectedCollections, setSelectedCollections)}
                            />
                            {opt}
                          </label>
                        ))}
                      </div>
                    )}

                    {isExpanded && section === 'tags' && (
                      <div className="tag-options">
                        {tagOptions.map(opt => (
                          <button
                            key={opt}
                            className={`tag-chip ${selectedTags.includes(opt) ? 'active' : ''}`}
                            onClick={() => toggleFromList(opt, selectedTags, setSelectedTags)}
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    )}

                    {isExpanded && section === 'ratings' && (
                      <div className="rating-options">
                        {ratingOptions.map(stars => (
                          <label key={stars} className="rating-option">
                            <input
                              type="checkbox"
                              checked={selectedRatings.includes(stars)}
                              onChange={() => toggleFromList(stars, selectedRatings, setSelectedRatings)}
                            />
                            <span className="stars" aria-hidden>
                              {'★'.repeat(stars)}{'☆'.repeat(5 - stars)}
                            </span>
                            <span className="sr-only">{stars} stars & up</span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </aside>

          <div className="products-content">
            <div className="search-and-filters">
              {/* <div className="products-search-bar">
                <svg className="search-icon" width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="8.30834" cy="7.80834" r="6.80834" stroke="black" strokeWidth="1.5"/>
                  <path d="M13.3252 12.825L15.8335 15.3334" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span className="search-placeholder">Search</span>
              </div> */}
              
              <div className="category-tags">
                {categoryTags.map((tag, index) => (
                  <button 
                    key={tag.label}
                    className={`category-tag ${tag.active ? 'active' : ''}`}
                  >
                    {tag.label}
                  </button>
                ))}
              </div>
            </div>

            <ProductGrid
              variant="list"
              items={products}
              renderItem={(product) => (
                <div className="product-card">
                  <div className="product-image-container">
                    <img src={product.image} alt={product.altText} className="product-image" />
                    <div className="floating-add-button" aria-label="Add to cart">
                      <svg width="13" height="14" viewBox="0 0 13 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.5 7.00005L6.5 7.00005M6.5 7.00005L0.5 7.00005M6.5 7.00005L6.5 1M6.5 7.00005L6.5 13" stroke="#0C0C0C" strokeLinecap="round"/>
                      </svg>
                    </div>
                  </div>
                  <div className="product-details">
                    <ProductMetaRow
                      category={product.category}
                      name={product.name}
                      price={product.price}
                      colorCount={product.colorCount}
                      colorSwatch={product.colorSwatch}
                    />
                  </div>
                </div>
              )}
            />

            
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ProductListPage;
