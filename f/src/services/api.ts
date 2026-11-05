const base = '/api'

async function requisicao<T>(rota: string, opcoes?: RequestInit): Promise<T> {
  const resposta = await fetch(`${base}${rota}`, opcoes)
  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) throw new Error(dados.erro || 'Não foi possível concluir a operação.')
  return dados as T
}

export const api = {
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
