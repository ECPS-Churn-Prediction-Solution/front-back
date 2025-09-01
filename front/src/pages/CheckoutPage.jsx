import React, { useMemo, useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { useNavigate } from 'react-router-dom';
import './CheckoutPage.css';

const CheckoutPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const passed = location.state;
  const items = useMemo(() => passed?.items || [], [passed]);

  const subtotal = items.reduce((s, i) => s + i.price * i.qty, 0);
  const [shippingMethod, setShippingMethod] = useState('Standard (3-5 business days)');
  const [shippingFee, setShippingFee] = useState(items.length > 0 ? 3000 : 0);

  const total = subtotal + shippingFee;

  const koreanToEnglishColorMap = useMemo(() => ({
    '그레이': 'gray',
    '블랙': 'black',
    '민트': 'mint',
    '화이트': 'white',
    '블루': 'blue',
  }), []);

  // Contact & address state
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [country, setCountry] = useState('');
  const [stateRegion, setStateRegion] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [postalCode, setPostalCode] = useState('');

  const handleShippingChange = (method, fee) => {
    setShippingMethod(method);
    setShippingFee(fee);
  };

  return (
    <div className="App">
      <Header />
      <main className="checkout-main">
        <h1 className="checkout-title">CHECKOUT</h1>
        <div className="checkout-grid">
          <section className="checkout-form">
            <nav className="checkout-steps">
              <span className="step active">INFORMATION</span>
              <span className="step">PAYMENT</span>
            </nav>

            <div className="form-section">
              <div className="section-title">CONTACT INFO</div>
              <label className="input-label">Email</label>
              <input className="input" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
              <label className="input-label">Phone</label>
              <input className="input" placeholder="Phone" value={phone} onChange={(e)=>setPhone(e.target.value)} />
            </div>

            <div className="form-section">
              <div className="section-title">SHIPPING ADDRESS</div>
              <div className="row">
                <div>
                  <label className="input-label">First Name</label>
                  <input className="input" placeholder="First Name" value={firstName} onChange={(e)=>setFirstName(e.target.value)} />
                </div>
                <div>
                  <label className="input-label">Last Name</label>
                  <input className="input" placeholder="Last Name" value={lastName} onChange={(e)=>setLastName(e.target.value)} />
                </div>
              </div>
              <label className="input-label">Country</label>
              <input className="input" placeholder="Country" value={country} onChange={(e)=>setCountry(e.target.value)} />
              <label className="input-label">State / Region</label>
              <input className="input" placeholder="State / Region" value={stateRegion} onChange={(e)=>setStateRegion(e.target.value)} />
              <label className="input-label">Address</label>
              <input className="input" placeholder="Address" value={address} onChange={(e)=>setAddress(e.target.value)} />
              <div className="row">
                <div>
                  <label className="input-label">City</label>
                  <input className="input" placeholder="City" value={city} onChange={(e)=>setCity(e.target.value)} />
                </div>
                <div>
                  <label className="input-label">Postal Code</label>
                  <input className="input" placeholder="Postal Code" value={postalCode} onChange={(e)=>setPostalCode(e.target.value)} />
                </div>
              </div>
            </div>

            <div className="form-section">
              <div className="section-title">SHIPPING METHOD</div>
              <label className="summary-row" style={{border:'1px solid #D9D9D9', padding:'10px'}}>
                <input
                  type="radio"
                  name="method"
                  defaultChecked
                  disabled={items.length === 0}
                  onChange={() => handleShippingChange('Standard (3-5 business days)', items.length > 0 ? 3000 : 0)}
                />
                <span>Standard (3-5 business days)</span>
                <span style={{marginLeft:'auto'}}>₩ {items.length > 0 ? '3000.00' : '0.00'}</span>
              </label>
              <label className="summary-row" style={{border:'1px solid #D9D9D9', padding:'10px'}}>
                <input
                  type="radio"
                  name="method"
                  disabled={items.length === 0}
                  onChange={() => handleShippingChange('Express (1-2 business days)', items.length > 0 ? 5000 : 0)}
                />
                <span>Express (1-2 business days)</span>
                <span style={{marginLeft:'auto'}}>₩ {items.length > 0 ? '5000.00' : '0.00'}</span>
              </label>
            </div>

            <div className="action-row">
              <a href="/products" className="link-mute">Continue shopping</a>
            </div>

            <button
              onClick={() => navigate('/payment', { state: {
                items,
                shipping: shippingFee,
                subtotal: subtotal,
                total: total,
                shippingMethod,
                contactInfo: { email, phone },
                shippingAddress: { firstName, lastName, country, stateRegion, address, city, postalCode },
              } })}
              className="next-btn"
            >
              Payment
            </button>
          </section>

          <aside className="order-panel">
            <div className="panel-header">
              <div className="panel-title">YOUR ORDER</div>
              <Link to="/cart" className="panel-count">({items.length})</Link>
            </div>

            <div className="order-list">
              {items.map((it, idx) => {
                const rawColor = (it?.color ?? '').toString();
                const colorKey = rawColor ? rawColor.toLowerCase() : '';
                const colorInEnglish = colorKey ? (koreanToEnglishColorMap[colorKey] || rawColor) : '-';
                const size = it?.size ?? '-';
                const image = it?.image || 'https://api.builder.io/api/v1/image/assets/TEMP/68fa811baecae42e4253dd9f1bba64b08c4ab399?width=734';
                const name = it?.name || 'Item';
                const qty = Number(it?.qty ?? 1);
                const price = Number(it?.price ?? 0);
                return (
                  <div key={it.id ?? it.productId ?? idx} className="order-item">
                    <img src={image} alt={name} className="order-thumb" />
                    <div className="order-meta">
                      <div className="order-name">{name}</div>
                      <div className="order-variant">{colorInEnglish} / {size}</div>
                    </div>
                    <div className="order-qty">({qty})</div>
                    <div className="order-price">₩ {(price * qty).toFixed(2)}</div>
                  </div>
                )
              })}
            </div>

            <div className="summary">
              <div className="summary-row"><span>Subtotal</span><span>₩ {subtotal.toFixed(2)}</span></div>
              <div className="summary-row"><span>Shipping</span><span>₩ {shippingFee.toFixed(2)}</span></div>
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

export default CheckoutPage;