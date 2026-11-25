import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { Sessao } from '../types'

export default function Layout() {
  const [usuario, setUsuario] = useState<Sessao | null>(null)
  const navegar = useNavigate()
  useEffect(() => { api.sessao().then(setUsuario).catch(() => setUsuario(null)) }, [])
  async function sair() {
    try { await api.logout(); navegar('/login') } catch { navegar('/login') }
  }
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">T</span><div><strong>TechStock</strong><small>Manager</small></div></div>
      <nav>
        <NavLink to="/" end><span>⌂</span> Visão geral</NavLink>
        <NavLink to="/pdv"><span>$</span> PDV B2B</NavLink>
        {usuario?.perfil === 'GERENTE' && <NavLink to="/livro-razao"><span>≡</span> Livro-Razão</NavLink>}
        {usuario?.perfil === 'GERENTE' && <NavLink to="/produtos/novo"><span>▦</span> Novo produto</NavLink>}
        <NavLink to="/movimentacoes/nova"><span>⇄</span> Movimentar estoque</NavLink>
        {usuario?.perfil === 'GERENTE' && <NavLink to="/movimentacoes"><span>≡</span> Histórico</NavLink>}
        {usuario?.perfil === 'GERENTE' && <NavLink to="/categorias"><span>◇</span> Categorias</NavLink>}
        {usuario?.perfil === 'GERENTE' && <NavLink to="/fornecedores"><span>♙</span> Fornecedores</NavLink>}
      </nav>
      <div className="sidebar-user"><div className="avatar">TS</div><div><strong>{usuario?.nome ?? 'TechStore'}</strong><small>{usuario?.perfil ?? <Link to="/login">Entrar</Link>}</small></div>{usuario && <button className="danger-button" onClick={sair}>Sair</button>}</div>
    </aside>
    <main><Outlet /></main>
  </div>
}
