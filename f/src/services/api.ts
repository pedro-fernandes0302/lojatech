const base = '/api'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function requisicao<T>(rota: string, opcoes?: RequestInit): Promise<T> {
  const resposta = await fetch(`${base}${rota}`, {
    ...opcoes,
    credentials: 'same-origin',
  })
  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) {
    const mensagem = dados.erro
      || (resposta.status === 404
        ? 'Rota da API não encontrada. Reinicie o backend Flask para carregar as rotas atualizadas.'
        : 'Não foi possível concluir a operação.')
    throw new ApiError(mensagem, resposta.status)
  }
  return dados as T
}

export const api = {
  auth: {
    entrar: (email: string, senha: string) => requisicao<{ usuario: import('../types').Usuario }>('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha }),
    }),
    registrar: (dados: { nome: string; email: string; senha: string }) => requisicao<{ mensagem: string }>('/auth/registrar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados),
    }),
    atual: () => requisicao<{ usuario: import('../types').Usuario }>('/auth/me'),
    sair: () => requisicao<{ mensagem: string }>('/auth/logout', { method: 'POST' }),
  },
  dashboard: () => requisicao<import('../types').DashboardResponse>('/dashboard'),
  categorias: {
    listar: () => requisicao<import('../types').Categoria[]>('/categorias'),
    criar: (nome: string) => requisicao<{mensagem:string}>('/categorias', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({nome})}),
    excluir: (id: number) => requisicao<{mensagem:string}>(`/categorias/${id}`, {method:'DELETE'}),
  },
  fornecedores: {
    listar: () => requisicao<import('../types').Fornecedor[]>('/fornecedores'),
    criar: (dados: {razao_social:string;cnpj:string;telefone:string;email:string}) => requisicao<{mensagem:string}>('/fornecedores', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(dados)}),
    excluir: (id: number) => requisicao<{mensagem:string}>(`/fornecedores/${id}`, {method:'DELETE'}),
  },
  produtos: {
    opcoes: () => requisicao<import('../types').ProdutoOpcoes>('/produtos/opcoes'),
    criar: (dados: Record<string, string | number>) => requisicao<{mensagem:string}>('/produtos', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(dados)}),
    excluir: (id: number) => requisicao<{mensagem:string}>(`/produtos/${id}`, {method:'DELETE'}),
  },
  movimentacoes: {
    listar: () => requisicao<import('../types').Movimentacao[]>('/movimentacoes'),
    criar: (dados: {produto_id:number;tipo:string;quantidade:number;observacao:string}) => requisicao<{mensagem:string;aviso_estoque:boolean}>('/movimentacoes', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(dados)}),
  },
}
