import React, { useState, useEffect } from 'react';
import { apiFetch } from '../lib/api.js';
import { Link } from 'react-router-dom';
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

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await apiFetch('/api/products');
        // 백엔드 스키마를 UI에 맞게 매핑
        const mapped = (data || []).map((p) => ({
          id: p.product_id,
          image: p.image_url,
          category: p.category_name || '',
          name: p.product_name,
          // 가격은 문자열 표기로 노출
          price: `₩${p.price}`,
          colorCount: p.available_variants || 0,
          colorSwatch: '#DBDCCE',
          altText: p.product_name,
        }));
        setProducts(mapped);
      } catch (e) {
        setError(e?.message || '상품 목록을 불러오지 못했습니다.');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

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
        {/* <div className="breadcrumb-section">
          <span className="breadcrumb-home">Home</span>
          <span className="breadcrumb-current"> / Products</span>
        </div> */}
        
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

            {error && (
              <div style={{ color: 'red', marginBottom: 16 }}>{error}</div>
            )}
            <ProductGrid
              variant="list"
              items={products}
              renderItem={(product) => (
                <div className="product-card">
                  <div className="product-image-container">
                    <img src={product.image} alt={product.altText} className="product-image" />
                    <Link
                      to={`/products/${product.id}`}
                      className="floating-add-button"
                      aria-label={`View details for ${product.name}`}
                    >
                      <svg width="13" height="14" viewBox="0 0 13 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.5 7.00005L6.5 7.00005M6.5 7.00005L0.5 7.00005M6.5 7.00005L6.5 1M6.5 7.00005L6.5 13" stroke="#0C0C0C" strokeLinecap="round"/>
                      </svg>
                    </Link>
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