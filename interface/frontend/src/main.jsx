import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Home from './Home.jsx'
import Settings from './Settings.jsx'
import CompanyTab from './CompanyTab.jsx'
import { SettingsProvider } from './SettingsContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SettingsProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/companyTab/:companyName" element={<CompanyTab />} />
        </Routes>
      </BrowserRouter>
    </SettingsProvider>
  </StrictMode>
)
