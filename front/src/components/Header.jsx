import React, { useState } from 'react';
import './Header.css';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header className="header">
      <div className="hamburger-menu" onClick={toggleMenu}>
        <svg width="28" height="17" viewBox="0 0 28 17" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M27 1.33203L1 1.33203" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M19 8.72949L1 8.72949" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
          <path d="M14 16.1274H1" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </div>

      <nav className={`main-navigation ${isMenuOpen ? 'mobile-menu-open' : ''}`}>
        <a href="#" className="nav-link">Home</a>
        <a href="#" className="nav-link">Collections</a>
        <a href="#" className="nav-link">New</a>
      </nav>

      <div className="logo-container">
        <img
          src="https://api.builder.io/api/v1/image/assets/TEMP/edd4bb23229320fd02af7208b0e1f4237dcff2c0?width=70"
          alt="Brand Logo"
          className="logo"
        />
      </div>

      <div className="category-links">
        <div className="category-text">
          MEN<br/>
          WOMEN<br/>
          KIDS
        </div>
      </div>

      <div className="login-button">
        <button className="login-btn signin-btn" aria-label="Sign in">
          sign in
        </button>
        <button className="login-btn signup-btn" aria-label="Sign up">
          sign up
        </button>
      </div>

      <div className="search-container">
        <div className="search-box">
          <svg className="search-icon" width="15" height="19" viewBox="0 0 15 19" fill="none" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="6.9437" cy="9.09685" rx="5.86362" ry="8.09685" stroke="black" strokeWidth="1.5"/>
            <path d="M11.2646 15.063L13.4249 18.046" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input
            type="text"
            placeholder="Search"
            className="search-input"
            aria-label="Search products"
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
