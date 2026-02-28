import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CardDetail from './pages/CardDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/card/:id" element={<CardDetail />} />
      </Routes>
    </BrowserRouter>
  )
}