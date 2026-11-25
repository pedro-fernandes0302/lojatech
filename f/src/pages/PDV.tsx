import { useEffect, useMemo, useState } from 'react'
import Aviso from '../components/Aviso'
import PageHeader from '../components/PageHeader'
import { api, ErroApi } from '../services/api'
import type { ProdutoOpcoes, Recibo } from '../types'

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
const vazio: ProdutoOpcoes = { categorias: [], fornecedores: [], produtos: [], clientes: [] }

export default function PDV() {
  const [opcoes, setOpcoes] = useState<ProdutoOpcoes>(vazio)
  const [cliente, setCliente] = useState('')
  const [produto, setProduto] = useState('')
  const [quantidade, setQuantidade] = useState(1)
  const [carrinho, setCarrinho] = useState<Array<{ id_produto: number; quantidade: number }>>([])
  const [recibo, setRecibo] = useState<Recibo | null>(null)
  const [erro, setErro] = useState('')
  const [sucesso, setSucesso] = useState('')

  useEffect(() => { api.produtos.opcoes().then(setOpcoes).catch(e => setErro(e.message)) }, [])
  const total = useMemo(() => carrinho.reduce((soma, item) => {
    const p = opcoes.produtos.find(p => p.id === item.id_produto)
    return soma + Math.round((p?.preco ?? 0) * 100) * item.quantidade
  }, 0) / 100, [carrinho, opcoes])

  function adicionar() {
    setErro('')
    if (!produto || quantidade < 1 || !Number.isInteger(quantidade)) {
      setErro('Selecione um produto e uma quantidade inteira positiva.')
      return
    }
    const id = Number(produto)
    setCarrinho(atual => atual.some(item => item.id_produto === id)
      ? atual.map(item => item.id_produto === id ? { ...item, quantidade: item.quantidade + quantidade } : item)
      : [...atual, { id_produto: id, quantidade }])
    setQuantidade(1)
  }

  async function finalizar() {
    setErro('')
    setSucesso('')
    setRecibo(null)
    try {
      if (!cliente || !carrinho.length) throw new Error('Selecione um cliente e adicione itens à venda.')
      const venda = await api.vendas.registrar({ id_cliente: Number(cliente), itens: carrinho })
      setSucesso(`Venda ${venda.numero_pedido} registrada.`)
      setCarrinho([])
      try {
        setRecibo(await api.vendas.recibo(venda.id_venda))
      } catch {
        setErro(`A venda ${venda.numero_pedido} foi registrada, mas o recibo não pôde ser carregado. Atualize a tela para consultar o pedido.`)
      }
      api.produtos.opcoes().then(setOpcoes).catch(e => {
        setErro(`Venda ${venda.numero_pedido} registrada, mas o catálogo não atualizou: ${(e as Error).message}`)
      })
    } catch (e) {
      if (e instanceof ErroApi) {
        setErro(`${e.message} O backend rejeitou a venda e reverteu integralmente a transação.`)
      } else {
        setErro('Não foi possível confirmar a resposta da venda. Consulte o histórico antes de tentar novamente.')
      }
    }
  }

  return <>
    <PageHeader titulo="PDV B2B" subtitulo="Venda multi-itens com baixa de estoque atômica" />
    <Aviso tipo="erro" mensagem={erro} /><Aviso mensagem={sucesso} />
    {!recibo ? <>
      <section className="form-panel">
        <div className="form-grid">
          <label className="span-2">Cliente B2B *
            <select value={cliente} onChange={e => setCliente(e.target.value)}>
              <option value="">Selecione o cliente</option>
              {opcoes.clientes.map(c => <option key={c.id} value={c.id}>{c.nome} · CNPJ {c.cnpj}</option>)}
            </select>
          </label>
          <label>Produto
            <select value={produto} onChange={e => setProduto(e.target.value)}>
              <option value="">Selecione o produto</option>
              {opcoes.produtos.map(p => <option key={p.id} value={p.id}>{p.sku} · {p.nome} · saldo {p.estoque_atual}</option>)}
            </select>
          </label>
          <label>Quantidade
            <input type="number" min="1" step="1" value={quantidade} onChange={e => setQuantidade(Number(e.target.value))} />
          </label>
          <div className="form-actions"><button type="button" className="primary-button" onClick={adicionar}>Adicionar ao carrinho</button></div>
        </div>
      </section>
      <section className="panel" style={{ marginTop: 20 }}>
        <div className="panel-heading"><div><h2>Carrinho</h2><p>Total atualizado com os preços atuais do catálogo</p></div></div>
        <div className="table-wrap"><table><thead><tr><th>SKU / Produto</th><th>Quantidade</th><th>Preço unitário</th><th>Subtotal</th><th></th></tr></thead>
          <tbody>{carrinho.map(item => {
            const p = opcoes.produtos.find(p => p.id === item.id_produto)
            if (!p) return null
            return <tr key={p.id}><td>{p.sku} · {p.nome}</td><td>{item.quantidade}</td><td>{moeda.format(p.preco)}</td><td>{moeda.format(Math.round(p.preco * 100) * item.quantidade / 100)}</td><td><button className="danger-button" onClick={() => setCarrinho(atual => atual.filter(x => x.id_produto !== p.id))}>Remover</button></td></tr>
          })}{!carrinho.length && <tr><td colSpan={5} className="empty">Adicione um ou mais produtos.</td></tr>}</tbody>
        </table></div>
        <div className="panel-heading"><strong>Total: {moeda.format(total)}</strong><button className="primary-button" disabled={!carrinho.length} onClick={finalizar}>Finalizar venda</button></div>
      </section>
    </> : <section className="panel" style={{ padding: 24 }}>
      <h2>Recibo de Faturamento B2B</h2>
      <p><strong>Pedido:</strong> {recibo.numero_pedido} · <strong>Data:</strong> {recibo.data_venda}</p>
      <p><strong>Cliente:</strong> {recibo.cliente_nome} · CNPJ {recibo.cliente_cnpj}</p>
      <div className="table-wrap"><table><thead><tr><th>SKU</th><th>Produto</th><th>Quantidade</th><th>Unitário</th><th>Subtotal</th></tr></thead>
        <tbody>{recibo.itens.map(item => <tr key={item.sku}><td>{item.sku}</td><td>{item.produto}</td><td>{item.quantidade}</td><td>{moeda.format(item.preco_unitario_centavos / 100)}</td><td>{moeda.format(item.subtotal_centavos / 100)}</td></tr>)}</tbody>
      </table></div>
      <p><strong>Total: {moeda.format(recibo.valor_total_centavos / 100)}</strong></p>
      <p>Operador: {recibo.operador} ({recibo.operador_email})</p>
      <a className="primary-button" target="_blank" rel="noreferrer" href={`/api/vendas/${recibo.id_venda}/recibo/imprimir`}>Abrir recibo para impressão</a>
      <button className="primary-button" style={{ marginLeft: 8 }} onClick={() => { setRecibo(null); setSucesso(''); }}>Nova venda</button>
    </section>}
  </>
}
