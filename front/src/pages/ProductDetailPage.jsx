import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './ProductDetailPage.css';

const ProductDetailPage = () => {
  const [quantity, setQuantity] = useState(1);
  const [selectedColor, setSelectedColor] = useState(null);
  const [selectedSize, setSelectedSize] = useState(null);
  const increaseQty = () => setQuantity((q) => q + 1);
  const decreaseQty = () => setQuantity((q) => Math.max(1, q - 1));
  const { id } = useParams();
  const navigate = useNavigate();

  const addToCart = () => {
    if (!selectedColor || !selectedSize) {
      alert('색상과 사이즈를 선택해 주세요.');
      return;
    }
    // API 없이 장바구니 페이지로 이동 (선택 정보는 state로 전달)
    navigate('/cart', {
      state: {
        item: {
          productId: Number(id),
          color: selectedColor,
          size: selectedSize,
          qty: quantity,
        },
      },
    });
  };

  const buyNow = () => {
    if (!selectedColor || !selectedSize) {
      alert('색상과 사이즈를 선택해 주세요.');
      return;
    }
    // API 없이 체크아웃으로 이동 (더미 데이터와 함께 전달)
    navigate('/checkout', {
      state: {
        items: [{ productId: Number(id), color: selectedColor, size: selectedSize, qty: quantity }],
        subtotal: 99 * quantity,
      },
    });
  };
  
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <div className="product-detail-container">
          <div className="product-images-section">
            <img
              src="https://api.builder.io/api/v1/image/assets/TEMP/68fa811baecae42e4253dd9f1bba64b08c4ab399?width=734"
              alt="Abstract Print Shirt Main Image"
              className="main-product-image"
            />
            <div className="thumbnail-gallery">
              <img
                src="https://api.builder.io/api/v1/image/assets/TEMP/fd6f43aa65dd55b5b7c5fd751b26805fcddd20ec?width=124"
                alt="Thumbnail 1"
                className="thumbnail-image"
              />
              <img
                src="https://api.builder.io/api/v1/image/assets/TEMP/0cc8464c427a5593db184890e929ccc982e4cd44?width=128"
                alt="Thumbnail 2"
                className="thumbnail-image"
              />
              <img
                src="https://api.builder.io/api/v1/image/assets/TEMP/8de037596bc1211c28fcb954993bf192e7bcf75b?width=128"
                alt="Thumbnail 3"
                className="thumbnail-image"
              />
              <img
                src="https://api.builder.io/api/v1/image/assets/TEMP/5a08084676a2b0bda0164006274bdb2bb26d7160?width=128"
                alt="Thumbnail 4"
                className="thumbnail-image"
              />
              <img
                src="https://api.builder.io/api/v1/image/assets/TEMP/eec94166fb78cc3bd556d7b48a624edd3bd26804?width=128"
                alt="Thumbnail 5"
                className="thumbnail-image"
              />
            </div>
          </div>
          
          <div className="product-info-panel">
            <div className="close-button">
              <div className="close-button-bg" />
              <div>
                <svg
                  width="10"
                  height="10"
                  viewBox="0 0 10 10"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="close-icon"
                >
                  <path
                    d="M6.77919 9.48979L6.75766 9.14045L6.77919 9.48979ZM3.66808 3.87948L3.64172 4.22849C3.7366 4.23565 3.8303 4.20389 3.90126 4.1405C3.97221 4.07711 4.01431 3.98757 4.01784 3.89249L3.66808 3.87948ZM8.89345 7.60105L9.23816 7.66168L8.89345 7.60105ZM6.77919 9.48979L6.75766 9.14045C5.85892 9.19583 4.91962 9.30499 4.00199 9.19854C3.10232 9.09417 2.26301 8.78436 1.58002 8.01982L1.319 8.253L1.05799 8.48617C1.88652 9.41363 2.90496 9.77597 3.92133 9.89388C4.91974 10.0097 5.95477 9.89125 6.80072 9.83912L6.77919 9.48979ZM1.319 8.253L1.58002 8.01982C0.911499 7.27148 0.773741 6.26616 1.11525 5.48669C1.44702 4.72943 2.26111 4.12421 3.64172 4.22849L3.66808 3.87948L3.69444 3.53048C2.05623 3.40674 0.940026 4.14228 0.474082 5.20578C0.0178738 6.24707 0.214989 7.54251 1.05799 8.48617L1.319 8.253ZM6.77919 9.48979L6.80072 9.83912C7.10445 9.82041 7.42963 9.79931 7.72475 9.7394C8.01975 9.67951 8.3232 9.57396 8.56343 9.35935L8.33026 9.09833L8.09708 8.83732C7.98938 8.93354 7.82513 9.00474 7.58549 9.05339C7.34597 9.10201 7.06958 9.12123 6.75766 9.14045L6.77919 9.48979ZM8.89345 7.60105L9.23816 7.66168C9.38497 6.82694 9.61892 5.81176 9.61597 4.80666C9.61297 3.78348 9.36732 2.73078 8.53879 1.80332L8.27777 2.0365L8.01675 2.26967C8.69974 3.03421 8.91332 3.90301 8.91598 4.80871C8.91869 5.73249 8.70472 6.65359 8.54874 7.54042L8.89345 7.60105ZM8.27777 2.0365L8.53879 1.80332C7.69579 0.859669 6.43067 0.518298 5.34474 0.854663C4.23563 1.19821 3.37938 2.22473 3.31832 3.86648L3.66808 3.87948L4.01784 3.89249C4.06929 2.5089 4.76213 1.76794 5.55185 1.52332C6.36475 1.27153 7.34823 1.52133 8.01675 2.26967L8.27777 2.0365ZM8.89345 7.60105L8.54874 7.54042C8.49461 7.84821 8.44447 8.12069 8.36925 8.35323C8.29399 8.58589 8.20479 8.7411 8.09708 8.83732L8.33026 9.09833L8.56343 9.35935C8.80366 9.14474 8.94263 8.85507 9.03527 8.56866C9.12796 8.28214 9.18544 7.96139 9.23816 7.66168L8.89345 7.60105Z"
                    fill="#1E1E1E"
                  />
                </svg>
              </div>
            </div>
            <div className="info-content">
              <div className="product-title">
              ABSTRACT PRINT SHIRT
              </div>
              
              <div className="product-price">
              $99
              </div>
              
              <div className="price-disclaimer">
              MRP incl. of all taxes
              </div>
              
              <div className="product-description">
              Relaxed-fit shirt. Camp collar and short sleeves. Button-up front.
              </div>
              
              <div className="option-label color-label">
              Color
              </div>
              
              <div className="color-options">
              <div className={`color-option color-option-light-gray ${selectedColor==='light-gray' ? 'selected' : ''}`} onClick={() => setSelectedColor('light-gray')} />
              <div className={`color-option color-option-gray ${selectedColor==='gray' ? 'selected' : ''}`} onClick={() => setSelectedColor('gray')} />
              <div className={`color-option color-option-black ${selectedColor==='black' ? 'selected' : ''}`} onClick={() => setSelectedColor('black')} />
              <div className={`color-option color-option-mint ${selectedColor==='mint' ? 'selected' : ''}`} onClick={() => setSelectedColor('mint')} />
              <div className={`color-option color-option-white ${selectedColor==='white' ? 'selected' : ''}`} onClick={() => setSelectedColor('white')} />
              <div className={`color-option color-option-blue ${selectedColor==='blue' ? 'selected' : ''}`} onClick={() => setSelectedColor('blue')} />
              </div>
              
              <div className="option-label size-label">
              Size
              </div>
              
              <div className="size-options">
              {['XS','S','M','L','XL','2X'].map((sz) => (
                <button
                  key={sz}
                  type="button"
                  className={`size-option ${selectedSize===sz ? 'selected' : ''}`}
                  onClick={() => setSelectedSize(sz)}
                  aria-pressed={selectedSize===sz}
                >
                  <div className="size-text">{sz}</div>
                </button>
              ))}
              </div>

              <div className="quantity-stepper" role="group" aria-label="Quantity selector">
              <button
                type="button"
                className="qty-btn qty-btn-minus"
                onClick={decreaseQty}
                aria-label="Decrease quantity"
                disabled={quantity <= 1}
              >
                −
              </button>
              <div className="qty-value" aria-live="polite" aria-atomic="true">{quantity}</div>
              <button
                type="button"
                className="qty-btn qty-btn-plus"
                onClick={increaseQty}
                aria-label="Increase quantity"
              >
                +
              </button>
              </div>
              
              <div className="size-guide-link">
              FIND YOUR SIZE | MEASUREMENT GUIDE
              </div>
              
              <div className="actions-row">
                <button
                  type="button"
                  className="add-to-cart-button"
                  onClick={addToCart}
                  disabled={!selectedColor || !selectedSize}
                >
                  <div className="add-button-text">ADD</div>
                </button>
                <button
                  type="button"
                  className="buy-now-button"
                  onClick={buyNow}
                  disabled={!selectedColor || !selectedSize}
                >
                  BUY NOW
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ProductDetailPage;