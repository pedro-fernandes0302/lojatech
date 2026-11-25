import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { DashboardResponse, Sessao } from '../types'
import PageHeader from '../components/PageHeader'
import Aviso from '../components/Aviso'

const money = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export default function Dashboard() {
  const [dados, setDados] = useState<DashboardResponse>({ produtos: [], categorias: 0, fornecedores: 0 })
  const [usuario, setUsuario] = useState<Sessao | null>(null)
  const [busca, setBusca] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(true)
  const carregar = () => {
    setCarregando(true)
    api.dashboard().then(setDados).catch(e => setErro(e.message)).finally(() => setCarregando(false))
  }
  useEffect(() => {
    carregar()
    api.sessao().then(setUsuario).catch(e => setErro(e.message))
  }, [])
  const filtrados = useMemo(() => dados.produtos.filter(p =>
    [p.sku, p.nome, p.fabricante, p.categoria, p.fornecedor].join(' ').toLowerCase().includes(busca.toLowerCase())
  ), [dados, busca])
  const risco = dados.produtos.filter(p => p.estoque_atual <= p.estoque_minimo)
  const valor = dados.produtos.reduce((soma, p) => soma + p.preco * p.estoque_atual, 0)
  return <>
    <PageHeader titulo="Catálogo TechStore" subtitulo="Hardware físico e licenças digitais em uma única visão"
      acao={<Link className="primary-button" to={usuario?.perfil === 'GERENTE' ? '/produtos/novo' : '/pdv'}>{usuario?.perfil === 'GERENTE' ? '＋ Novo produto' : '＋ Abrir PDV'}</Link>} />
    <Aviso tipo="erro" mensagem={erro} />
    <section className="metrics">
      <article><div className="metric-icon blue">▦</div><div><span>Total em produtos</span><strong>{dados.produtos.length}</strong><small>{dados.produtos.filter(p => p.tipo === 'Software').length} licenças digitais</small></div></article>
      <article><div className="metric-icon purple">R$</div><div><span>Valor do estoque</span><strong>{money.format(valor)}</strong><small>Preço × saldo atual</small></div></article>
      <article><div className="metric-icon orange">!</div><div><span>Alerta de reposição</span><strong>{risco.length}</strong><small>Saldo no ponto mínimo ou abaixo</small></div></article>
      <article><div className="metric-icon green">◇</div><div><span>Cadastro</span><strong>{dados.categorias}</strong><small>{dados.fornecedores} fornecedores ativos</small></div></article>
    </section>
    <section className="panel"><div className="panel-heading"><div><h2>Catálogo consolidado</h2><p>Saldo único, chaves digitais disponíveis e ponto de reposição</p></div><label className="search"><span>⌕</span><input value={busca} onChange={e => setBusca(e.target.value)} placeholder="Buscar produto ou fornecedor" /></label></div>
      {carregando ? <div className="loading">Carregando inventário...</div> : <div className="table-wrap"><table><thead><tr><th>Produto</th><th>Tipo</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Ativos disponíveis</th><th>Status</th>{usuario?.perfil === 'GERENTE' && <th></th>}</tr></thead><tbody>
        {filtrados.map(p => {
          const alerta = p.estoque_atual <= p.estoque_minimo
          return <tr key={p.id} className={alerta ? 'risk-row' : ''}>
            <td><div className="product-cell"><div className="product-icon">{p.tipo === 'Software' ? '▣' : '▤'}</div><div><strong>{p.nome}</strong><span>{p.sku} · {p.fabricante}</span></div></div></td>
            <td><span className="status">{p.tipo_catalogo}</span></td><td>{p.categoria}</td><td>{money.format(p.preco)}</td>
            <td><strong>{p.estoque_atual}</strong><span className="minimum"> / mín. {p.estoque_minimo}</span></td>
            <td>{p.tipo === 'Software' ? `${p.chaves_disponiveis} chave(s)` : `${p.quantidade_fisica} unidade(s) física(s)`}</td>
            <td>{alerta ? <span className="status risk">ALERTA · Reposição</span> : <span className="status ok">Estoque normal</span>}</td>
            {usuario?.perfil === 'GERENTE' && <td><button className="more-button" aria-label={`Excluir ${p.nome}`} onClick={async () => {
              if (confirm(`Descontinuar ${p.nome}?`)) {
                try { await api.produtos.excluir(p.id); carregar() }
                catch (e) { setErro((e as Error).message) }
              }
            }}>⌫</button></td>}
          </tr>
        })}
        {!filtrados.length && <tr><td colSpan={usuario?.perfil === 'GERENTE' ? 8 : 7} className="empty">Nenhum produto encontrado.</td></tr>}
      </tbody></table></div>}
    </section>
  </>
}
