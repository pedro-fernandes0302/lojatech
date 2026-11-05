import type { ReactNode } from 'react'

interface Props { titulo: string; subtitulo?: string; acao?: ReactNode }
export default function PageHeader({titulo, subtitulo, acao}: Props) {
  return <header className="topbar"><div><p className="eyebrow">GESTÃO DE INVENTÁRIO</p><h1>{titulo}</h1>{subtitulo && <p className="page-subtitle">{subtitulo}</p>}</div>{acao}</header>
}
