import React, { useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './CheckoutPage.css';
import { apiFetch } from '../lib/api.js';

// API 호출은 apiFetch 사용

const PaymentPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const items = useMemo(() => location.state?.items || [], [location.state]);
  const isBuyNow = useMemo(() => items.length > 0 && !!items[0].variantId, [items]);
  const [paymentMethod, setPaymentMethod] = useState('credit');
  const [cardInfo, setCardInfo] = useState({ number: '', name: '', expiry: '', cvc: '' });

  const subtotal = useMemo(() => items.reduce((s, i) => s + i.price * i.qty, 0), [items]);
  const shipping = useMemo(() => location.state?.shipping ?? 0, [location.state]);
  const shippingMethod = useMemo(() => location.state?.shippingMethod ?? 'Standard (3-5 business days)', [location.state]);
  const total = useMemo(() => subtotal + shipping, [subtotal, shipping]);

  const contact = useMemo(() => location.state?.contactInfo, [location.state]);
  const addr = useMemo(() => location.state?.shippingAddress, [location.state]);

  const handleCardInfoChange = (e) => {
    setCardInfo({ ...cardInfo, [e.target.name]: e.target.value });
  };

  const handlePlaceOrder = async () => {
    if (isBuyNow && (!contact || !addr || !contact.email || !addr.address)) {
      alert('배송 및 연락처 정보를 확인해주세요.');
      navigate('/checkout');
      return;
    }

    try {
      let response;
      if (isBuyNow) {
        const orderItem = items[0];
        const orderPayload = {
          variant_id: orderItem.variantId,
          quantity: orderItem.qty,
          recipient_name: `${addr.firstName} ${addr.lastName}`,
          shipping_address: {
            zip_code: addr.postalCode,
            address_main: addr.address,
            address_detail: `${addr.city}, ${addr.stateRegion}`
          },
          phone_number: contact.phone,
          payment_method: 'credit_card', // 'credit'와 'debit' 모두 'credit_card'로 처리
          shopping_memo: location.state?.shippingMemo || "",
        };

        // 즉시 구매 API
        response = await apiFetch('/api/orders/direct', {
          method: 'POST',
          body: orderPayload,
        });
      } else {
        const orderPayload = {
          recipient_name: `${addr.firstName} ${addr.lastName}`,
          shipping_address: {
            zip_code: addr.postalCode,
            address_main: addr.address,
            address_detail: `${addr.city}, ${addr.stateRegion}`
          },
          phone_number: contact.phone,
          payment_method: 'credit_card', // 'credit'와 'debit' 모두 'credit_card'로 처리
          shopping_memo: location.state?.shippingMemo || "",
        };

        // 장바구니 주문 API
        response = await apiFetch('/api/orders/', {
          method: 'POST',
          body: orderPayload,
        });
      }

      if (response) {
        const orderData = response;
        navigate('/order', {
          state: {
            orderId: orderData.order_id || `ORD-${Date.now().toString().slice(-6)}`,
            items,
            subtotal,
            shipping,
            shippingMethod,
            total,
          },
        });
      }
    } catch (error) {
      alert('주문 처리 중 오류가 발생했습니다.');
      console.error('Order placement error:', error);
    }
  };

  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="checkout-title">CHECKOUT</h1>
        <div className="checkout-grid">
          <section className="checkout-form">
            <nav className="checkout-steps">
              <Link className="step" to="/checkout">INFORMATION</Link>
              <span className="step active">PAYMENT</span>
            </nav>

            <div className="form-section">
              <div className="section-title">PAYMENT METHOD</div>
              <label className="summary-row" style={{border:'1px solid #D9D9D9', padding:'10px'}}>
                <input
                  type="radio"
                  name="pay"
                  value="credit"
                  checked={paymentMethod === 'credit'}
                  onChange={() => setPaymentMethod('credit')}
                />
                <span>Credit Card</span>
              </label>
              <label className="summary-row" style={{border:'1px solid #D9D9D9', padding:'10px', marginTop: '10px'}}>
                <input
                  type="radio"
                  name="pay"
                  value="debit"
                  checked={paymentMethod === 'debit'}
                  onChange={() => setPaymentMethod('debit')}
                />
                <span>Debit Card</span>
              </label>
              <div className="row">
                <input className="input" name="number" placeholder="Card Number" value={cardInfo.number} onChange={handleCardInfoChange} />
                <input className="input" name="name" placeholder="Name on Card" value={cardInfo.name} onChange={handleCardInfoChange} />
              </div>
              <div className="row">
                <input className="input" name="expiry" placeholder="MM/YY" value={cardInfo.expiry} onChange={handleCardInfoChange} />
                <input className="input" name="cvc" placeholder="CVC" value={cardInfo.cvc} onChange={handleCardInfoChange} />
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
                    <div className="summary-row"><span>Address</span><span>{`${addr.address}, ${addr.city}, ${addr.stateRegion} ${addr.postalCode}, ${addr.country}`}</span></div>
                    <div className="summary-row"><span>Shipping</span><span>{shippingMethod} · ₩ {shipping.toFixed(2)}</span></div>
                  </div>
                )}
              </div>
            )}

            <button
              className="next-btn"
              onClick={handlePlaceOrder}
              disabled={!items || items.length === 0}
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
              <div className="summary-row"><span>Subtotal</span><span>₩ {subtotal.toFixed(2)}</span></div>
              <div className="summary-row"><span>Shipping</span><span>₩ {shipping.toFixed(2)}</span></div>
              <div className="summary-divider" />
              <div className="summary-row total"><span>Total</span><span>₩ {total.toFixed(2)}</span></div>
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default PaymentPage;