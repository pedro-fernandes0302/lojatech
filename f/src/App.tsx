import type { ReactNode } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import './App.css'
import Layout from './components/Layout'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/useAuth'
import Categorias from './pages/Categorias'
import Dashboard from './pages/Dashboard'
import Fornecedores from './pages/Fornecedores'
import Login from './pages/Login'
import Movimentacoes from './pages/Movimentacoes'
import NovaMovimentacao from './pages/NovaMovimentacao'
import NovoProduto from './pages/NovoProduto'
import Register from './pages/Register'

function SessionLoading() {
  return <main className="session-loading" role="status">Verificando sessão...</main>
}

function RequireAuth({ children }: { children: ReactNode }) {
  const { usuario, carregando } = useAuth()
  const location = useLocation()
  if (carregando) return <SessionLoading />
  if (!usuario) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

function RequireManager({ children }: { children: ReactNode }) {
  const { usuario } = useAuth()
  if (usuario?.perfil !== 'GERENTE') return <Navigate to="/" replace />
  return children
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { usuario, carregando } = useAuth()
  if (carregando) return <SessionLoading />
  if (usuario) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
          <Route path="/registrar" element={<PublicOnly><Register /></PublicOnly>} />
          <Route element={<RequireAuth><Layout /></RequireAuth>}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/produtos/novo" element={<RequireManager><NovoProduto /></RequireManager>} />
            <Route path="/movimentacoes/nova" element={<NovaMovimentacao />} />
            <Route path="/movimentacoes" element={<Movimentacoes />} />
            <Route path="/categorias" element={<RequireManager><Categorias /></RequireManager>} />
            <Route path="/fornecedores" element={<RequireManager><Fornecedores /></RequireManager>} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
