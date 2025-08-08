import React from 'react';
import './Footer.css';

const Footer = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* To Top Button */}
        <button className="to-top-button" onClick={scrollToTop} aria-label="Scroll to top">
          <svg className="to-top-icon" width="14" height="17" viewBox="0 0 14 17" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 7L7 1M7 1L13 7M7 1L7 17" stroke="black" strokeWidth="1.25"/>
          </svg>
    
        </button>

        {/* Footer Logo */}
        <div className="decorative-diamond">
          <img
            className="footer-logo"
            src="https://api.builder.io/api/v1/image/assets/TEMP/edd4bb23229320fd02af7208b0e1f4237dcff2c0?width=70"
            alt="Brand Logo"
          />
        </div>

        {/* Info Section */}
        <section className="info-section">
          <h3 className="section-title">Info</h3>
          <nav className="info-nav">
            <div className="nav-item">
              <a href="#pricing" className="nav-link">Pricing</a>
              <span className="nav-separator">/</span>
            </div>
            <div className="nav-item">
              <a href="#about" className="nav-link">About</a>
              <span className="nav-separator">/</span>
            </div>
            <a href="#contacts" className="nav-link">Contacts</a>
          </nav>
        </section>

        {/* Languages Section */}
        <section className="languages-section">
          <h3 className="section-title">Languages</h3>
          <div className="languages-nav">
            <div className="language-item">
              <button className="language-link">Eng</button>
              <span className="language-separator">/</span>
            </div>
            <div className="language-item">
              <button className="language-link">Esp</button>
              <span className="language-separator">/</span>
            </div>
            <button className="language-link">Sve</button>
          </div>
        </section>

        {/* Technologies Section */}
        <section className="technologies-section">
          <h3 className="section-title">Technologies</h3>
          <div className="technologies-content">
            <div className="tech-item vr">VR</div>
            <div className="tech-row">
              <div className="tech-item xiv">XIV</div>
              <div className="tech-description">Near-field communication</div>
              <div className="tech-separator">/</div>
            </div>
            <div className="tech-item qr">QR</div>
          </div>
        </section>
        
        {/* Copyright */}
        <div className="copyright">
          © {new Date().getFullYear()} Brand. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
