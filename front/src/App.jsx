import React from 'react';
import Header from './components/Header';
import ProductSection from './components/ProductSection';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <h1>Clothing Store</h1>
        <p>Welcome to our fashion destination!</p>
        <ProductSection />
      </main>
      <Footer />
    </div>
  );
}

export default App;
