import React, { useMemo } from 'react';
import { useLocation, Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './CheckoutPage.css';

const CheckoutPage = () => {
  const location = useLocation();
  const passed = location.state;
  const items = useMemo(() => (
    passed?.items || [
      { id: 1, name: 'Basic Heavy T-Shirt', variant: 'Black/L', price: 99, qty: 1, image: 'https://picsum.photos/seed/ck1/200/240' },
      { id: 2, name: 'Basic Fit T-Shirt', variant: 'Black/L', price: 99, qty: 1, image: 'https://picsum.photos/seed/ck2/200/240' },
    ]
  ), [passed]);

  const subtotal = items.reduce((s, i) => s + i.price * i.qty, 0);

  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="checkout-title">CHECKOUT</h1>
        <div className="checkout-grid">
          <section className="checkout-form">
            <nav className="checkout-steps">
              <span className="step active">INFORMATION</span>
              <span className="step">SHIPPING</span>
              <span className="step">PAYMENT</span>
            </nav>

            <div className="form-section">
              <div className="section-title">CONTACT INFO</div>
              <input className="input" placeholder="Email" />
              <input className="input" placeholder="Phone" />
            </div>

            <div className="form-section">
              <div className="section-title">SHIPPING ADDRESS</div>
              <div className="row">
                <input className="input" placeholder="First Name" />
                <input className="input" placeholder="Last Name" />
              </div>
              <input className="input" placeholder="Country" />
              <input className="input" placeholder="State / Region" />
              <input className="input" placeholder="Address" />
              <div className="row">
                <input className="input" placeholder="City" />
                <input className="input" placeholder="Postal Code" />
              </div>
            </div>

            <button className="next-btn">Shipping</button>
          </section>

          <aside className="order-panel">
            <div className="panel-header">
              <div className="panel-title">YOUR ORDER</div>
              <Link to="/cart" className="panel-count">({items.length})</Link>
            </div>

            <div className="order-list">
              {items.map((it) => (
                <div key={it.id} className="order-item">
                  <img src={it.image} alt={it.name} className="order-thumb" />
                  <div className="order-meta">
                    <div className="order-name">{it.name}</div>
                    <div className="order-variant">{it.variant}</div>
                  </div>
                  <div className="order-qty">({it.qty})</div>
                  <div className="order-price">$ {it.price}</div>
                </div>
              ))}
            </div>

            <div className="summary">
              <div className="summary-row"><span>Subtotal</span><span>$ {subtotal.toFixed(2)}</span></div>
              <div className="summary-row"><span>Shipping</span><span className="muted">Calculated at next step</span></div>
              <div className="summary-divider" />
              <div className="summary-row total"><span>Total</span><span>$ {subtotal.toFixed(2)}</span></div>
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default CheckoutPage;


