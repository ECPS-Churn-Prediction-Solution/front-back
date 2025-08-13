import React, { useMemo } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './CheckoutPage.css';

const PaymentPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const items = useMemo(() => (
    location.state?.items || [
      { id: 1, name: 'Basic Heavy T-Shirt', variant: 'Black/L', price: 99, qty: 1, image: 'https://picsum.photos/seed/ck1/200/240' },
      { id: 2, name: 'Basic Fit T-Shirt', variant: 'Black/L', price: 99, qty: 1, image: 'https://picsum.photos/seed/ck2/200/240' },
    ]
  ), [location.state]);
  const subtotal = items.reduce((s, i) => s + i.price * i.qty, 0);
  const shipping = Number(location.state?.shipping ?? 5);
  const shippingMethod = location.state?.shippingMethod ?? 'Standard (3-5 business days)';
  const total = subtotal + shipping;
  const contact = location.state?.contactInfo;
  const addr = location.state?.shippingAddress;
  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="checkout-title">CHECKOUT</h1>
        <div className="checkout-grid">
          <section className="checkout-form">
            <nav className="checkout-steps">
              <Link className="step" to="/checkout">INFORMATION</Link>
              {/* <Link className="step" to="/shipping">SHIPPING</Link> */}
              <span className="step active">PAYMENT</span>
            </nav>

            <div className="form-section">
              <div className="section-title">PAYMENT METHOD</div>
              <label className="summary-row" style={{border:'1px solid #D9D9D9', padding:'10px'}}>
                <input type="radio" name="pay" defaultChecked />
                <span>Credit / Debit Card</span>
              </label>
              <div className="row">
                <input className="input" placeholder="Card Number" />
                <input className="input" placeholder="Name on Card" />
              </div>
              <div className="row">
                <input className="input" placeholder="MM/YY" />
                <input className="input" placeholder="CVC" />
              </div>
            </div>

            {(contact || addr) && (
              <div className="form-section">
                <div className="section-title">REVIEW INFORMATION</div>
                {contact && (
                  <div className="summary">
                    <div className="summary-row"><span>Email</span><span>{contact.email}</span></div>
                    <div className="summary-row"><span>Phone</span><span>{contact.phone}</span></div>
                  </div>
                )}
                {addr && (
                  <div className="summary">
                    <div className="summary-row"><span>Name</span><span>{addr.firstName} {addr.lastName}</span></div>
                    <div className="summary-row"><span>Address</span><span>{addr.address}, {addr.city}, {addr.stateRegion} {addr.postalCode}, {addr.country}</span></div>
                    <div className="summary-row"><span>Shipping</span><span>{shippingMethod} · $ {shipping.toFixed(2)}</span></div>
                  </div>
                )}
              </div>
            )}

            <button
              className="next-btn"
              onClick={() =>
                navigate('/order', {
                  state: {
                    orderId: `ORD-${Date.now().toString().slice(-6)}`,
                    items,
                    subtotal,
                    shipping,
                    shippingMethod,
                    total,
                  },
                })
              }
            >
              Pay
            </button>
          </section>

          <aside className="order-panel">
            <div className="panel-header">
              <div className="panel-title">YOUR ORDER</div>
              <Link to="/cart" className="panel-count">({items.length})</Link>
            </div>
            <div className="summary">
              <div className="summary-row"><span>Subtotal</span><span>$ {subtotal.toFixed(2)}</span></div>
              <div className="summary-row"><span>Shipping</span><span>$ {shipping.toFixed(2)}</span></div>
              <div className="summary-divider" />
              <div className="summary-row total"><span>Total</span><span>$ {total.toFixed(2)}</span></div>
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default PaymentPage;


