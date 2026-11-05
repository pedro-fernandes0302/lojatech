import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { DashboardResponse } from '../types'
import PageHeader from '../components/PageHeader'
import Aviso from '../components/Aviso'

const money = new Intl.NumberFormat('pt-BR', {style:'currency', currency:'BRL'})

export default function Dashboard() {
  const [dados, setDados] = useState<DashboardResponse>({produtos:[],categorias:0,fornecedores:0})
  const [busca,setBusca]=useState(''); const [erro,setErro]=useState(''); const [carregando,setCarregando]=useState(true)
  const carregar=()=>{setCarregando(true);api.dashboard().then(setDados).catch(e=>setErro(e.message)).finally(()=>setCarregando(false))}
  useEffect(carregar,[])
  const filtrados=useMemo(()=>dados.produtos.filter(p=>[p.sku,p.nome,p.fabricante,p.categoria,p.fornecedor].join(' ').toLowerCase().includes(busca.toLowerCase())),[dados,busca])
  const risco=dados.produtos.filter(p=>p.estoque_atual<=p.estoque_minimo)
  const valor=dados.produtos.reduce((s,p)=>s+p.preco*p.estoque_atual,0)
  return <><PageHeader titulo="Olá, TechStore 👋" acao={<Link className="primary-button" to="/produtos/novo">＋ Novo produto</Link>} />
    <Aviso tipo="erro" mensagem={erro}/>
    <section className="metrics">
      <article><div className="metric-icon blue">▦</div><div><span>Total em produtos</span><strong>{dados.produtos.length}</strong><small>{dados.produtos.filter(p=>p.tipo==='Software').length} licenças de software</small></div></article>
      <article><div className="metric-icon purple">R$</div><div><span>Valor do estoque</span><strong>{money.format(valor)}</strong><small>Preço × saldo atual</small></div></article>
      <article><div className="metric-icon orange">!</div><div><span>Risco de ruptura</span><strong>{risco.length}</strong><small>Reposição necessária</small></div></article>
      <article><div className="metric-icon green">◇</div><div><span>Cadastro</span><strong>{dados.categorias}</strong><small>{dados.fornecedores} fornecedores ativos</small></div></article>
    </section>
    <section className="panel"><div className="panel-heading"><div><h2>Produtos em estoque</h2><p>Acompanhe o saldo e os níveis mínimos</p></div><label className="search"><span>⌕</span><input value={busca} onChange={e=>setBusca(e.target.value)} placeholder="Buscar produto ou fornecedor" /></label></div>
      {carregando?<div className="loading">Carregando inventário...</div>:<div className="table-wrap"><table><thead><tr><th>Produto</th><th>Categoria</th><th>Fornecedor</th><th>Preço</th><th>Saldo</th><th>Status</th><th></th></tr></thead><tbody>{filtrados.map(p=>{const alerta=p.estoque_atual<=p.estoque_minimo;return <tr key={p.id} className={alerta?'risk-row':''}><td><div className="product-cell"><div className="product-icon">{p.tipo==='Software'?'▣':'▤'}</div><div><strong>{p.nome}</strong><span>{p.sku} · {p.fabricante}</span></div></div></td><td>{p.categoria}</td><td>{p.fornecedor}</td><td>{money.format(p.preco)}</td><td><strong>{p.estoque_atual}</strong><span className="minimum"> / mín. {p.estoque_minimo}</span></td><td>{alerta?<span className="status risk">Risco de Ruptura / Reposição Necessária</span>:<span className="status ok">Estoque normal</span>}</td><td><button className="more-button" onClick={async()=>{if(confirm('Descontinuar este produto?')){try{await api.produtos.excluir(p.id);carregar()}catch(e){setErro((e as Error).message)}}}}>⌫</button></td></tr>})}{!filtrados.length&&<tr><td colSpan={7} className="empty">Nenhum produto encontrado.</td></tr>}</tbody></table></div>}</section></>
}
