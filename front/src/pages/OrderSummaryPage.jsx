import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './CheckoutPage.css';

const OrderSummaryPage = () => {
  const { state } = useLocation();
  const orderId = state?.orderId || 'ORD-000000';
  const items = state?.items || [];
  const subtotal = state?.subtotal ?? 0;
  const shipping = state?.shipping ?? 0;
  const shippingMethod = state?.shippingMethod ?? 'Standard (3-5 business days)';
  const contact = state?.contactInfo;
  const addr = state?.shippingAddress;
  const total = state?.total ?? subtotal + shipping;

  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="checkout-title">ORDER CONFIRMED</h1>
        <div className="checkout-grid">
          <section className="checkout-form">
            <div className="form-section">
              <div className="section-title">THANK YOU</div>
              <p style={{fontSize:'12px'}}>Your order <strong>{orderId}</strong> has been placed successfully.</p>
              <Link to="/" className="next-btn">Back to Home</Link>
            </div>

            <div className="form-section">
              <div className="section-title">ORDER DETAILS</div>
              <div className="summary">
                <div className="summary-row"><span>Order ID</span><span>{orderId}</span></div>
                <div className="summary-row"><span>Date</span><span>{new Date().toLocaleString()}</span></div>
                {contact && (
                  <>
                    <div className="summary-row"><span>Email</span><span>{contact.email}</span></div>
                    <div className="summary-row"><span>Phone</span><span>{contact.phone}</span></div>
                  </>
                )}
                {addr && (
                  <>
                    <div className="summary-row"><span>Ship To</span><span>{addr.firstName} {addr.lastName}</span></div>
                    <div className="summary-row"><span>Address</span><span>{addr.address}, {addr.city}, {addr.stateRegion} {addr.postalCode}, {addr.country}</span></div>
                  </>
                )}
                <div className="summary-row"><span>Shipping Method</span><span>{shippingMethod} · $ {Number(shipping).toFixed(2)}</span></div>
              </div>
            </div>

            <div className="action-row">
              <Link to="/me" className="link-mute">View my orders</Link>
              <Link to="/products" className="link-mute">Continue shopping</Link>
            </div>
          </section>

          <aside className="order-panel">
            <div className="panel-header">
              <div className="panel-title">YOUR ORDER</div>
              <span className="panel-count">({items.length})</span>
            </div>
            {(contact || addr) && (
              <div className="summary" style={{marginTop:0}}>
                <div className="section-title">INFORMATION</div>
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
                    <div className="summary-row"><span>Shipping</span><span>{shippingMethod} · $ {Number(shipping).toFixed(2)}</span></div>
                  </div>
                )}
              </div>
            )}
            <div className="order-list">
              {items.map((it, idx) => (
                <div key={it.id ?? it.productId ?? idx} className="order-item">
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
              <div className="summary-row"><span>Subtotal</span><span>$ {Number(subtotal).toFixed(2)}</span></div>
              <div className="summary-row"><span>Shipping</span><span>$ {Number(shipping).toFixed(2)}</span></div>
              <div className="summary-row"><span>Shipping Method</span><span>{shippingMethod}</span></div>
              <div className="summary-divider" />
              <div className="summary-row total"><span>Total</span><span>$ {Number(total).toFixed(2)}</span></div>
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default OrderSummaryPage;