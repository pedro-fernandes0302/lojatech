import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">T</span><div><strong>TechStock</strong><small>Manager</small></div></div>
      <nav>
        <NavLink to="/" end><span>⌂</span> Visão geral</NavLink>
        <NavLink to="/produtos/novo"><span>▦</span> Novo produto</NavLink>
        <NavLink to="/movimentacoes/nova"><span>⇄</span> Movimentar estoque</NavLink>
        <NavLink to="/movimentacoes"><span>≡</span> Histórico</NavLink>
        <NavLink to="/categorias"><span>◇</span> Categorias</NavLink>
        <NavLink to="/fornecedores"><span>♙</span> Fornecedores</NavLink>
      </nav>
      <div className="sidebar-user"><div className="avatar">TS</div><div><strong>TechStore</strong><small>Administrador</small></div></div>
    </aside>
    <main><Outlet /></main>
  </div>
}
