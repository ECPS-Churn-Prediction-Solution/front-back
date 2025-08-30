import React, { useState, useEffect, useMemo } from 'react';
import { apiFetch } from '../lib/api.js';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './ProductDetailPage.css';

// API 호출은 apiFetch를 통해 프록시 경유 및 쿠키 포함

const ProductDetailPage = () => {
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedColor, setSelectedColor] = useState(null);
  const [selectedSize, setSelectedSize] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const data = await apiFetch(`/api/products/${id}`);
        setProduct(data);
      } catch (error) {
        console.error("Error fetching product:", error);
      }
    };
    fetchProduct();
  }, [id]);

  // UI 색상 이름과 DB 색상 이름(한글/영문)을 매핑합니다.
  const uiColorToDbColorMap = useMemo(() => ({
    'light-gray': ['gray', '그레이'],
    'gray': ['gray', '그레이'],
    'black': ['black', '블랙'],
    'mint': ['mint', '민트'],
    'white': ['white', '화이트'],
    'blue': ['blue', '블루']
  }), []);

  // 서버에서 가져온 데이터를 기반으로 실제 구매 가능한 색상과 사이즈 목록을 계산합니다.
  const availableOptions = useMemo(() => {
    if (!product) return { colors: new Set(), sizes: new Set() };

    // DB에 있는 모든 색상 이름을 소문자로 변환하여 가져옵니다.
    const dbColors = new Set(product.variants.map(v => v.color.toLowerCase()));

    // UI 색상 이름이 DB에 존재하는지 확인하여 실제 구매 가능한 UI 색상 목록을 만듭니다.
    const availableUiColors = new Set(
        Object.keys(uiColorToDbColorMap).filter(uiColor =>
            uiColorToDbColorMap[uiColor].some(dbColor => dbColors.has(dbColor))
        )
    );

    // 현재 선택된 UI 색상에 해당하는 사이즈 목록을 계산합니다.
    const sizes = selectedColor
        ? new Set(product.variants
            .filter(v => uiColorToDbColorMap[selectedColor].includes(v.color.toLowerCase()))
            .map(v => v.size))
        : new Set();

    return { colors: availableUiColors, sizes: sizes };
  }, [product, selectedColor, uiColorToDbColorMap]);

  const increaseQty = () => setQuantity((q) => q + 1);
  const decreaseQty = () => setQuantity((q) => Math.max(1, q - 1));

  const handleColorSelect = (color) => {
    setSelectedColor(color);
    setSelectedSize(null); // 색상이 바뀌면 사이즈 선택을 초기화합니다.
  };

  const addToCart = async () => {
    if (!selectedColor || !selectedSize || !product) {
      alert('색상과 사이즈를 선택해 주세요.');
      return;
    }

    const possibleDbColors = uiColorToDbColorMap[selectedColor] || [selectedColor];
    const variant = product.variants.find(
        (v) => possibleDbColors.includes(v.color.toLowerCase()) && v.size === selectedSize
    );

    if (!variant) {
      alert('선택한 옵션의 상품이 없습니다.');
      return;
    }

    try {
      await apiFetch('/api/cart/items', {
        method: 'POST',
        body: { variant_id: variant.variant_id, quantity }
      });
      {
        if (window.confirm('장바구니에 추가되었습니다. 장바구니로 이동하시겠습니까?')) {
          navigate('/cart');
        }
      }
    } catch (error) {
      if (error.status === 401) alert('로그인이 필요합니다.');
      else alert(error.message);
    }
  };

  const buyNow = () => {
    if (!selectedColor || !selectedSize || !product) {
      alert('색상과 사이즈를 선택해 주세요.');
      return;
    }

    const possibleDbColors = uiColorToDbColorMap[selectedColor] || [selectedColor];
    const variant = product.variants.find(
        (v) => possibleDbColors.includes(v.color.toLowerCase()) && v.size === selectedSize
    );

    if (!variant) {
      alert('선택한 옵션의 상품이 없습니다.');
      return;
    }

    navigate('/checkout', {
      state: {
        items: [{
          variantId: variant.variant_id,
          qty: quantity,
          price: product.price,
          name: product.product_name,
          image: product.image_url || "https://api.builder.io/api/v1/image/assets/TEMP/68fa811baecae42e4253dd9f1bba64b08c4ab399?width=734"
        }],
        subtotal: product.price * quantity,
      },
    });
  };

  if (!product) {
    return <div>Loading...</div>;
  }

  // UI 렌더링을 위한 전체 색상/사이즈 목록
  const allUiColors = [
    { name: 'light-gray', value: '#D9D9D9' },
    { name: 'gray', value: '#A9A9A9' },
    { name: 'black', value: '#1E1E1E' },
    { name: 'mint', value: '#A6D6CA' },
    { name: 'white', value: '#FFFFFF' },
    { name: 'blue', value: '#B9C1E8' }
  ];
  const allUiSizes = ['XS', 'S', 'M', 'L', 'XL', '2X'];

  return (
      <div className="App">
        <Header />
        <main className="main-content">
          <div className="product-detail-container">
            <div className="product-images-section">
              <img
                  src={product.image_url || "https://api.builder.io/api/v1/image/assets/TEMP/68fa811baecae42e4253dd9f1bba64b08c4ab399?width=734"}
                  alt="Abstract Print Shirt Main Image"
                  className="main-product-image"
              />
              <div className="thumbnail-gallery">
                <img src="https://api.builder.io/api/v1/image/assets/TEMP/fd6f43aa65dd55b5b7c5fd751b26805fcddd20ec?width=124" alt="Thumbnail 1" className="thumbnail-image" />
                <img src="https://api.builder.io/api/v1/image/assets/TEMP/0cc8464c427a5593db184890e929ccc982e4cd44?width=128" alt="Thumbnail 2" className="thumbnail-image" />
                <img src="https://api.builder.io/api/v1/image/assets/TEMP/8de037596bc1211c28fcb954993bf192e7bcf75b?width=128" alt="Thumbnail 3" className="thumbnail-image" />
                <img src="https://api.builder.io/api/v1/image/assets/TEMP/5a08084676a2b0bda0164006274bdb2bb26d7160?width=128" alt="Thumbnail 4" className="thumbnail-image" />
                <img src="https://api.builder.io/api/v1/image/assets/TEMP/eec94166fb78cc3bd556d7b48a624edd3bd26804?width=128" alt="Thumbnail 5" className="thumbnail-image" />
              </div>
            </div>

            <div className="product-info-panel">
              <div className="info-content">
                <div className="product-title">{product.product_name}</div>
                <div className="product-price">₩{product.price}</div>
                <div className="price-disclaimer">MRP incl. of all taxes</div>
                <div className="product-description">{product.description}</div>

                <div className="option-label color-label">Color</div>
                <div className="color-options">
                  {allUiColors.map(color => {
                    return (
                        <div
                            key={color.name}
                            className={`color-option color-option-${color.name.replace('_', '-')} ${selectedColor === color.name ? 'selected' : ''}`}
                            style={{
                              backgroundColor: color.value,
                              border: selectedColor === color.name ? '2px solid #000' : (color.name === 'white' ? '1px solid #E5E5E5' : 'none')
                            }}
                            onClick={() => handleColorSelect(color.name)}
                        />
                    );
                  })}
                </div>

                <div className="option-label size-label">Size</div>
                <div className="size-options">
                  {allUiSizes.map(sz => {
                    return (
                        <button
                            key={sz}
                            type="button"
                            className={`size-option ${selectedSize === sz ? 'selected' : ''}`}
                            onClick={() => setSelectedSize(sz)}
                            aria-pressed={selectedSize === sz}
                        >
                          <div className="size-text">{sz}</div>
                        </button>
                    );
                  })}
                </div>

                <div className="quantity-stepper" role="group" aria-label="Quantity selector">
                  <button type="button" className="qty-btn qty-btn-minus" onClick={decreaseQty} aria-label="Decrease quantity" disabled={quantity <= 1}>−</button>
                  <div className="qty-value" aria-live="polite" aria-atomic="true">{quantity}</div>
                  <button type="button" className="qty-btn qty-btn-plus" onClick={increaseQty} aria-label="Increase quantity">+</button>
                </div>

                <div className="size-guide-link">FIND YOUR SIZE | MEASUREMENT GUIDE</div>

                <div className="actions-row">
                  <button type="button" className="add-to-cart-button" onClick={addToCart} disabled={!selectedColor || !selectedSize}>
                    <div className="add-button-text">ADD</div>
                  </button>
                  <button type="button" className="buy-now-button" onClick={buyNow} disabled={!selectedColor || !selectedSize}>
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