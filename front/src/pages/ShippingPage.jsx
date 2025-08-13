import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './CheckoutPage.css';

const ShippingPage = () => {
  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="checkout-title">CHECKOUT</h1>
        <div className="checkout-grid">
          <section className="checkout-form">
            <nav className="checkout-steps">
              <Link className="step" to="/checkout">INFORMATION</Link>
              <span className="step active">SHIPPING</span>
              <span className="step">PAYMENT</span>
            </nav>

            <div className="form-section">
              <div className="section-title">SHIPPING METHOD</div>
              <label className="summary-row" style={{border:'1px solid #D9D9D9', padding:'10px'}}>
                <input type="radio" name="method" defaultChecked />
                <span>Standard (3-5 business days)</span>
                <span style={{marginLeft:'auto'}}>$ 5.00</span>
              </label>
              <label className="summary-row" style={{border:'1px solid #D9D9D9', padding:'10px'}}>
                <input type="radio" name="method" />
                <span>Express (1-2 business days)</span>
                <span style={{marginLeft:'auto'}}>$ 12.00</span>
              </label>
            </div>

            <Link to="/payment" className="next-btn">Payment</Link>
          </section>

          <aside className="order-panel">
            <div className="panel-header">
              <div className="panel-title">YOUR ORDER</div>
              <Link to="/cart" className="panel-count">(2)</Link>
            </div>
            <div className="summary">
              <div className="summary-row"><span>Subtotal</span><span>$ 180.00</span></div>
              <div className="summary-row"><span>Shipping</span><span>$ 5.00</span></div>
              <div className="summary-divider" />
              <div className="summary-row total"><span>Total</span><span>$ 185.00</span></div>
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ShippingPage;