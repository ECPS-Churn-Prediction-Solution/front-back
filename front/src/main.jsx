import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { track } from './lib/analytics.js'

ReactDOM.createRoot(document.getElementById('root')).render(
  <App />
)

// 초기 페이지뷰 로깅
track('page_view', { page_url: location.href, referrer: document.referrer })