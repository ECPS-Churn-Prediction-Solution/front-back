import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './CartPage.css';
import { useNavigate } from 'react-router-dom';


const CartPage = () => {
  const location = useLocation();
  const passedItem = location.state?.item;
  const [items, setItems] = useState(() => (
    passedItem
    ? [
        {
          id: 1,
          name: 'Full Sleeve Zipper',
          category: 'Cotton T Shirt',
          price: 99,
          image: 'https://picsum.photos/seed/cart1/600/750',
          ...passedItem,
        },
        {
          id: 2,
          name: 'Basic Slim Fit T-Shirt',
          category: 'Cotton T Shirt',
          price: 99,
          image: 'https://picsum.photos/seed/cart2/600/750',
          color: 'black',
          size: 'L',
          qty: 1,
        },
      ]
    : [
        {
          id: 1,
          name: 'Full Sleeve Zipper',
          category: 'Cotton T Shirt',
          price: 99,
          image: 'https://picsum.photos/seed/cart1/600/750',
          color: 'black',
          size: 'L',
          qty: 1,
        },
        {
          id: 2,
          name: 'Basic Slim Fit T-Shirt',
          category: 'Cotton T Shirt',
          price: 99,
          image: 'https://picsum.photos/seed/cart2/600/750',
          color: 'black',
          size: 'L',
          qty: 1,
        },
      ]
  ));

  const changeQty = (id, delta) => {
    setItems(prev => prev.map(it => it.id === id ? { ...it, qty: Math.max(1, (it.qty || 1) + delta) } : it));
  };

  const subtotal = items.reduce((sum, it) => sum + it.price * it.qty, 0);
  const shipping = 10;
  const total = subtotal + shipping;

  return (
    <div className="App">
      <Header />
      <main className="cart-main">
        <h1 className="cart-title">CART</h1>
        <div className="cart-list">
          {items.map((it) => (
            <div key={it.id} className="cart-card">
              <div className="cart-card__image-wrap">
                <img src={it.image} alt={it.name} className="cart-card__image" />
                {/* <button className="cart-card__zoom" aria-label="Zoom"></button> */}
              </div>
              <div className="cart-card__meta">
                <div className="cart-card__category">{it.category}</div>
                <div className="cart-card__name">{it.name}</div>
                <div className="cart-card__price">$ {it.price}</div>
              </div>
              <div className="cart-card__options">
                <div className="option-stack">
                  <div className="opt-label">Size</div>
                  <div className="opt-value opt-size">{it.size}</div>
                  <div className="opt-label">Color</div>
                  <span className="color-chip" />
                  <div className="opt-label">Quantity</div>
                  <div className="qty-stepper vertical">
                    <button className="qty-square" onClick={() => changeQty(it.id, 1)} aria-label="Increase">+</button>
                    <div className="qty-square" aria-live="polite">{it.qty}</div>
                    <button className="qty-square" onClick={() => changeQty(it.id, -1)} aria-label="Decrease">−</button>
                  </div>
                </div>
              </div>
              <button className="remove-btn" aria-label="Remove">×</button>
            </div>
          ))}
        </div>

        <aside className="order-summary">
          <div className="summary-title">ORDER SUMMARY</div>
          <div className="summary-row">
            <span>Subtotal</span>
            <span>$ {subtotal}</span>
          </div>
          <div className="summary-row">
            <span>Shipping</span>
            <span>$ {shipping}</span>
          </div>
          <div className="summary-divider" />
          <div className="summary-total">
            <span>TOTAL <small>(TAX INCL.)</small></span>
            <span>$ {total}</span>
          </div>
          <label className="terms">
            <input type="checkbox" />
            <span>I agree to the Terms and Conditions</span>
          </label>
            <button
              type="button"
              className="continue-btn"
              onClick={() => navigate('/checkout')}
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


