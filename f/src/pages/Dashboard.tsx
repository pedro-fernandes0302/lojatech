import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import type { DashboardResponse, Produto } from '../types'
import Aviso from '../components/Aviso'
import { useAuth } from '../context/useAuth'

const money = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

function emRisco(produto: Produto) {
  return produto.estoque_atual <= produto.estoque_minimo
}

export default function Dashboard() {
  const { usuario } = useAuth()
  const [dados, setDados] = useState<DashboardResponse>({ produtos: [], categorias: 0, fornecedores: 0 })
  const [busca, setBusca] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(true)

  const carregar = () => {
    setCarregando(true)
    api.dashboard()
      .then(setDados)
      .catch(e => setErro(e.message))
      .finally(() => setCarregando(false))
  }

  useEffect(() => {
    let ativo = true
    api.dashboard()
      .then(resultado => { if (ativo) setDados(resultado) })
      .catch(e => { if (ativo) setErro(e.message) })
      .finally(() => { if (ativo) setCarregando(false) })
    return () => { ativo = false }
  }, [])

  const filtrados = useMemo(
    () => dados.produtos.filter(p =>
      [p.sku, p.nome, p.fabricante, p.categoria, p.fornecedor]
        .join(' ')
        .toLowerCase()
        .includes(busca.toLowerCase()),
    ),
    [dados, busca],
  )

  const risco = useMemo(
    () => dados.produtos.filter(emRisco).sort(
      (a, b) => (a.estoque_atual - a.estoque_minimo) - (b.estoque_atual - b.estoque_minimo),
    ),
    [dados],
  )

  const ordenados = useMemo(
    () => [...filtrados].sort((a, b) => Number(emRisco(b)) - Number(emRisco(a))),
    [filtrados],
  )

  const valor = dados.produtos.reduce((soma, produto) => soma + produto.preco * produto.estoque_atual, 0)
  const licencas = dados.produtos.filter(produto => produto.tipo === 'Software').length

  return (
    <div className="dashboard-page overview-page">
      <header className="overview-heading">
        <div>
          <p className="eyebrow">TECHSTOCK <span aria-hidden="true">/</span> INVENTÁRIO</p>
          <h1>Visão geral</h1>
          <p className="overview-description">Uma leitura objetiva dos níveis e do valor do seu estoque.</p>
        </div>
        <div className="overview-actions">
          <Link className="secondary-button" to="/movimentacoes/nova">Registrar movimentação</Link>
          {usuario?.perfil === 'GERENTE' && (
            <Link className="primary-button" to="/produtos/novo"><span aria-hidden="true">＋</span> Novo produto</Link>
          )}
        </div>
      </header>

      <Aviso tipo="erro" mensagem={erro} />

      <section className="overview-focus" aria-label="Valor e reposição de estoque">
        <article className="inventory-value">
          <p className="overview-label">VALOR ESTIMADO EM ESTOQUE</p>
          <strong>{money.format(valor)}</strong>
          <p className="inventory-value-caption">
            Estimativa calculada com os preços cadastrados e os saldos atuais.
          </p>
          <div className="inventory-value-rule" />
          <div className="inventory-value-meta">
            <span>Posição atual</span>
            <span>{dados.produtos.length} {dados.produtos.length === 1 ? 'produto cadastrado' : 'produtos cadastrados'}</span>
          </div>
        </article>

        <aside className={`replenishment-panel${risco.length ? ' has-risk' : ''}`}>
          <div className="replenishment-heading">
            <div>
              <p className="overview-label">ACOMPANHAMENTO</p>
              <h2>Reposição</h2>
            </div>
            <strong className="replenishment-count">{risco.length}</strong>
          </div>
          <p className="replenishment-summary">
            {risco.length
              ? `${risco.length === 1 ? 'Produto chegou' : 'Produtos chegaram'} ao nível mínimo de estoque.`
              : 'Nenhum produto está abaixo do nível mínimo.'}
          </p>
          {risco.length > 0 && (
            <ul className="replenishment-list">
              {risco.slice(0, 3).map(produto => (
                <li key={produto.id}>
                  <span><strong>{produto.nome}</strong><small>{produto.sku}</small></span>
                  <span className="replenishment-balance">
                    {produto.estoque_atual}<small> mín. {produto.estoque_minimo}</small>
                  </span>
                </li>
              ))}
            </ul>
          )}
          {risco.length > 3 && (
            <p className="replenishment-more">e mais {risco.length - 3} {risco.length - 3 === 1 ? 'item' : 'itens'}</p>
          )}
          <Link className="text-link" to="/movimentacoes/nova">
            Registrar movimentação <span aria-hidden="true">↗</span>
          </Link>
        </aside>
      </section>

      <section className="overview-statistics" aria-label="Resumo de cadastros">
        <article>
          <span className="stat-label">Produtos</span>
          <strong>{dados.produtos.length}</strong>
          <small>{licencas} {licencas === 1 ? 'licença de software' : 'licenças de software'}</small>
        </article>
        <article>
          <span className="stat-label">Categorias</span>
          <strong>{dados.categorias}</strong>
          <small>Grupos de produtos</small>
        </article>
        <article>
          <span className="stat-label">Fornecedores</span>
          <strong>{dados.fornecedores}</strong>
          <small>Parceiros cadastrados</small>
        </article>
      </section>

      <section className="panel inventory-panel" id="inventario">
        <div className="panel-heading inventory-heading">
          <div>
            <p className="overview-label">DETALHAMENTO</p>
            <h2>Inventário completo</h2>
            <p>Produtos organizados por prioridade de reposição.</p>
          </div>
          <label className="search">
            <span aria-hidden="true">⌕</span>
            <input
              aria-label="Buscar produto ou fornecedor"
              value={busca}
              onChange={event => setBusca(event.target.value)}
              placeholder="Buscar por produto, SKU ou fornecedor"
            />
          </label>
        </div>
        {carregando ? (
          <div className="loading">Carregando inventário...</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Produto</th>
                  <th>Categoria</th>
                  <th>Fornecedor</th>
                  <th>Preço</th>
                  <th>Saldo atual</th>
                  <th>Situação</th>
                  <th><span className="visually-hidden">Ações</span></th>
                </tr>
              </thead>
              <tbody>
                {ordenados.map(produto => {
                  const alerta = emRisco(produto)
                  return (
                    <tr key={produto.id} className={alerta ? 'risk-row' : ''}>
                      <td>
                        <div className="product-cell">
                          <div>
                            <strong>{produto.nome}</strong>
                            <span>{produto.sku} · {produto.fabricante}</span>
                          </div>
                        </div>
                      </td>
                      <td>{produto.categoria}</td>
                      <td>{produto.fornecedor}</td>
                      <td>{money.format(produto.preco)}</td>
                      <td>
                        <strong>{produto.estoque_atual}</strong>
                        <span className="minimum"> / mín. {produto.estoque_minimo}</span>
                      </td>
                      <td>
                        {alerta
                          ? <span className="status risk">Reposição necessária</span>
                          : <span className="status ok">Dentro do nível</span>}
                      </td>
                      <td>
                        <button
                          className="more-button"
                          aria-label={`Descontinuar ${produto.nome}`}
                          title={`Descontinuar ${produto.nome}`}
                          onClick={async () => {
                            if (confirm('Descontinuar este produto?')) {
                              try {
                                await api.produtos.excluir(produto.id)
                                carregar()
                              } catch (e) {
                                setErro((e as Error).message)
                              }
                            }
                          }}
                        >⌫</button>
                      </td>
                    </tr>
                  )
                })}
                {!ordenados.length && (
                  <tr><td colSpan={7} className="empty">Nenhum produto encontrado.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
