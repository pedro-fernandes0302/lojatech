import { Link, NavLink, Outlet } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../context/useAuth'

export default function Layout() {
  const { usuario, sair } = useAuth()
  const [erroSair, setErroSair] = useState('')
  const gerente = usuario?.perfil === 'GERENTE'

  async function encerrarSessao() {
    setErroSair('')
    try {
      await sair()
    } catch (erro) {
      setErroSair(erro instanceof Error ? erro.message : 'Não foi possível encerrar a sessão no servidor.')
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#conteudo">Pular para o conteúdo</a>
      <aside className="sidebar">
        <Link className="brand" to="/" aria-label="TechStock — página inicial">
          <span className="brand-mark" aria-hidden="true">T</span>
          <div><strong>TechStock</strong><small>GESTÃO INTELIGENTE</small></div>
        </Link>
        <p className="nav-caption">Workspace</p>
        <nav aria-label="Navegação principal">
          <NavLink to="/" end><span aria-hidden="true">⌂</span> Visão geral</NavLink>
          {gerente && <NavLink to="/produtos/novo"><span aria-hidden="true">▦</span> Novo produto</NavLink>}
          <NavLink to="/movimentacoes/nova"><span aria-hidden="true">⇄</span> Movimentar estoque</NavLink>
          <NavLink to="/movimentacoes"><span aria-hidden="true">≡</span> Histórico</NavLink>
          {gerente && <NavLink to="/categorias"><span aria-hidden="true">◇</span> Categorias</NavLink>}
          {gerente && <NavLink to="/fornecedores"><span aria-hidden="true">♙</span> Fornecedores</NavLink>}
        </nav>
        <div className="sidebar-user">
          <div className="avatar" aria-hidden="true">TS</div>
          <div className="sidebar-user-info">
            <strong>{usuario?.nome}</strong>
            <small>{usuario?.perfil === 'GERENTE' ? 'Gerente' : 'Operador'}</small>
          </div>
          <button className="logout-button" type="button" onClick={encerrarSessao} aria-label="Sair da conta" title="Sair">
            <span aria-hidden="true">↗</span>
          </button>
        </div>
        {erroSair && <p className="logout-error" role="alert">{erroSair}</p>}
      </aside>
      <div className="workspace">
        <header className="workspace-topbar">
          <div className="workspace-context">
            <span className="workspace-context-mark" aria-hidden="true">✦</span>
            <span>TechStock <span aria-hidden="true">/</span> Operações</span>
          </div>
          <span className="workspace-status">Painel de gestão</span>
        </header>
        <main className="workspace-main" id="conteudo"><Outlet /></main>
      </div>
    </div>
  )
}
