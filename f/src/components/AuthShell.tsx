import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface Props {
  titulo: string
  descricao: string
  alternativa: string
  linkAlternativa: string
  textoLink: string
  children: ReactNode
}

export default function AuthShell({
  titulo,
  descricao,
  alternativa,
  linkAlternativa,
  textoLink,
  children,
}: Props) {
  return (
    <main className="auth-page">
      <section className="auth-story" aria-label="Sobre o TechStock">
        <Link className="auth-brand" to="/login" aria-label="TechStock">
          <span className="auth-brand-mark" aria-hidden="true">T</span>
          <span><strong>TechStock</strong><small>GESTÃO INTELIGENTE</small></span>
        </Link>
        <div className="auth-story-copy">
          <p className="auth-eyebrow">CONTROLE QUE MOVE O NEGÓCIO</p>
          <h1>Seu estoque,<br />em boa perspectiva.</h1>
          <p>Uma operação mais clara começa com informação confiável e decisões no momento certo.</p>
        </div>
        <div className="auth-story-foot">
          <span>GESTÃO DE INVENTÁRIO</span>
          <span>TECHSTOCK <span aria-hidden="true">/</span> 01</span>
        </div>
      </section>

      <section className="auth-form-side">
        <div className="auth-form-wrap">
          <div className="auth-mobile-brand">
            <span className="auth-brand-mark" aria-hidden="true">T</span>
            <strong>TechStock</strong>
          </div>
          <p className="auth-form-eyebrow">ÁREA DO CLIENTE</p>
          <h2>{titulo}</h2>
          <p className="auth-form-description">{descricao}</p>
          {children}
          <p className="auth-switch">
            {alternativa} <Link to={linkAlternativa}>{textoLink}</Link>
          </p>
          <p className="auth-legal">Ao continuar, você acessa o ambiente de gestão TechStock.</p>
        </div>
      </section>
    </main>
  )
}
