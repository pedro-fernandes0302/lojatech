import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import NovoProduto from './pages/NovoProduto'
import NovaMovimentacao from './pages/NovaMovimentacao'
import Movimentacoes from './pages/Movimentacoes'
import Categorias from './pages/Categorias'
import Fornecedores from './pages/Fornecedores'
import PDV from './pages/PDV'
import LivroRazao from './pages/LivroRazao'
import Login from './pages/Login'

export default function App() {
  return <BrowserRouter><Routes>
    <Route path="/login" element={<Login />} />
    <Route element={<Layout />}>
    <Route path="/" element={<Dashboard />} />
    <Route path="/pdv" element={<PDV />} />
    <Route path="/livro-razao" element={<LivroRazao />} />
    <Route path="/produtos/novo" element={<NovoProduto />} />
    <Route path="/movimentacoes/nova" element={<NovaMovimentacao />} />
    <Route path="/movimentacoes" element={<Movimentacoes />} />
    <Route path="/categorias" element={<Categorias />} />
    <Route path="/fornecedores" element={<Fornecedores />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Route></Routes></BrowserRouter>
}
