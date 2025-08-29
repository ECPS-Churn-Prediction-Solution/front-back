import React, { useState, useEffect, useMemo } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './CartPage.css';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const CartPage = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);

  const colorNameToHexMap = useMemo(() => ({
    'gray': '#A9A9A9',
    '그레이': '#A9A9A9',
    'light-gray': '#D9D9D9',
    'black': '#1E1E1E',
    '블랙': '#1E1E1E',
    'mint': '#A6D6CA',
    '민트': '#A6D6CA',
    'white': '#FFFFFF',
    '화이트': '#FFFFFF',
    'blue': '#B9C1E8',
    '블루': '#B9C1E8'
  }), []);

  const fetchCartItems = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cart/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        const formattedItems = data.items.map(item => ({
          id: item.cart_item_id,
          name: item.product_name,
          category: 'Clothing',
          price: item.price,
          image: item.image_url || "https://api.builder.io/api/v1/image/assets/TEMP/68fa811baecae42e4253dd9f1bba64b08c4ab399?width=734",
          color: item.color,
          size: item.size,
          qty: item.quantity,
        }));
        setItems(formattedItems);
      } else if (response.status === 401) {
        setItems([]);
      } else {
        console.error("Failed to fetch cart items");
      }
    } catch (error) {
      console.error("Error fetching cart items:", error);
    }
  };

  useEffect(() => {
    fetchCartItems();
  }, []);

  const changeQty = async (id, newQty) => {
    if (newQty < 1) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/cart/items/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQty }),
        credentials: 'include',
      });

      if (response.ok) {
        setItems(prev => prev.map(it => it.id === id ? { ...it, qty: newQty } : it));
      } else {
        alert('수량 변경에 실패했습니다.');
      }
    } catch (error) {
      alert('수량 변경 중 오류가 발생했습니다.');
    }
  };

  const removeItem = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/cart/items/${id}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (response.ok) {
        setItems(prev => prev.filter(it => it.id !== id));
      } else {
        alert('상품 삭제에 실패했습니다.');
      }
    } catch (error) {
      alert('상품 삭제 중 오류가 발생했습니다.');
    }
  };

  const subtotal = items.reduce((sum, it) => sum + it.price * it.qty, 0);
  const shipping = items.length > 0 ? 3000 : 0;
  const total = subtotal + shipping;

  return (
      <div className="App">
        <Header />
        <main className="cart-main">
          <h1 className="cart-title">CART</h1>
          <div className="cart-list">
            {items.map((it) => {
              const colorValue = colorNameToHexMap[it.color.toLowerCase()] || 'transparent';
              return (
                <div key={it.id} className="cart-card">
                  <div className="cart-card__image-wrap">
                    <img src={it.image} alt={it.name} className="cart-card__image" />
                  </div>
                  <div className="cart-card__meta">
                    <div className="cart-card__category">{it.category}</div>
                    <div className="cart-card__name">{it.name}</div>
                    <div className="cart-card__price">₩ {it.price}</div>
                  </div>
                  <div className="cart-card__options">
                    <div className="option-stack">
                      <div className="opt-label">Size</div>
                      <div className="opt-value opt-size">{it.size}</div>
                      <div className="opt-label">Color</div>
                      <span className="color-chip" style={{backgroundColor: colorValue, border: colorValue !== 'transparent' ? '1px solid #D9D9D9' : 'none'}}/>
                      <div className="opt-label">Quantity</div>
                      <div className="qty-stepper vertical">
                        <button className="qty-square" onClick={() => changeQty(it.id, it.qty + 1)} aria-label="Increase">+</button>
                        <div className="qty-square" aria-live="polite">{it.qty}</div>
                        <button className="qty-square" onClick={() => changeQty(it.id, it.qty - 1)} aria-label="Decrease">−</button>
                      </div>
                    </div>
                  </div>
                  <button className="remove-btn" aria-label="Remove" onClick={() => removeItem(it.id)}>×</button>
                </div>
              )
            })}
          </div>

          <aside className="order-summary">
            <div className="summary-title">ORDER SUMMARY</div>
            <div className="summary-row">
              <span>Subtotal</span>
              <span>₩ {subtotal.toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span>Shipping</span>
              <span>₩ {shipping.toFixed(2)}</span>
            </div>
            <div className="summary-divider" />
            <div className="summary-total">
              <span>TOTAL <small>(TAX INCL.)</small></span>
              <span>₩ {total.toFixed(2)}</span>
            </div>
            <label className="terms">
              <input type="checkbox" />
              <span>I agree to the Terms and Conditions</span>
            </label>
            <button
                type="button"
                className="continue-btn"
                onClick={() => navigate('/checkout', { state: { items: items } })}
            >
              CONTINUE
            </button>
          </aside>
        </main>
        <Footer />
      </div>
  );
};

export default CartPage;