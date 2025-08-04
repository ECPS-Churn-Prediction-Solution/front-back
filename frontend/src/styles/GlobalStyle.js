import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

  html, body, #root {
    height: 100%;
    margin: 0;
    padding: 0;
    font-family: 'Noto Sans KR', sans-serif;
    background: #f5f5f5;
    color: #222;
    font-size: 16px;
    line-height: 1.5;
  }

  *, *::before, *::after {
    box-sizing: border-box;
  }

  a {
    color: inherit;
    text-decoration: none;
    transition: color 0.2s;
  }

  button {
    cursor: pointer;
    border: none;
    outline: none;
    background: #222;
    color: #fff;
    border-radius: 6px;
    padding: 0.5rem 1.2rem;
    font-size: 1rem;
    transition: background 0.2s;
  }
  button:hover {
    background: #444;
  }

  input, textarea {
    font-family: inherit;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 0.5rem;
    background: #fff;
    color: #222;
  }

  img {
    max-width: 100%;
    display: block;
  }

  @media (max-width: 768px) {
    html, body {
      font-size: 15px;
    }
  }
`;

export default GlobalStyle;
