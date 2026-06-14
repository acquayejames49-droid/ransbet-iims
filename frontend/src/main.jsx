// Entry point: this is the first JavaScript that runs. It mounts the React
// <App> component into the <div id="root"> in index.html.
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
