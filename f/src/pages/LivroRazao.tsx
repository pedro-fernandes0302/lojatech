import { useEffect, useState } from 'react'
import Aviso from '../components/Aviso'
import PageHeader from '../components/PageHeader'
import { api } from '../services/api'
import type { LinhaRazao } from '../types'

export default function LivroRazao() {
  const [linhas, setLinhas] = useState<LinhaRazao[]>([])
  const [venda, setVenda] = useState('')
  const [erro, setErro] = useState('')
  const carregar = () => api.vendas.livroRazao(venda ? Number(venda) : undefined).then(setLinhas).catch(e => setErro(e.message))
  useEffect(() => { carregar() }, [])
  return <>
    <PageHeader titulo="Livro-Razão" subtitulo="Registro imutável de entradas e saídas com contexto da venda" />
    <Aviso tipo="erro" mensagem={erro} />
    <section className="panel">
      <div className="panel-heading"><label>Filtrar por ID da venda <input type="number" min="1" value={venda} onChange={e => setVenda(e.target.value)} /></label><button className="primary-button" onClick={carregar}>Filtrar</button></div>
      <div className="table-wrap"><table><thead><tr><th>Data/hora</th><th>Venda</th><th>Cliente / CNPJ</th><th>Produto</th><th>Movimento</th><th>Usuário</th></tr></thead>
        <tbody>{linhas.map(l => <tr key={l.id}><td>{l.data_hora}</td><td>{l.numero_pedido ?? '—'}</td><td>{l.cliente ?? '—'} {l.cnpj ? `· ${l.cnpj}` : ''}</td><td>{l.sku} · {l.produto}</td><td>{l.tipo} · {l.quantidade}</td><td>{l.usuario ?? '—'}</td></tr>)}{!linhas.length && <tr><td colSpan={6} className="empty">Nenhuma movimentação encontrada.</td></tr>}</tbody>
      </table></div>
    </section>
  </>
}
