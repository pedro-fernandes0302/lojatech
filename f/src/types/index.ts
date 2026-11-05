export interface Produto {
  id: number; sku: string; nome: string; fabricante: string; tipo: string;
  categoria: string; fornecedor: string; preco: number; estoque_atual: number;
  estoque_minimo: number; localizacao: string; modalidade_licenca: string | null;
}
export interface DashboardResponse { produtos: Produto[]; categorias: number; fornecedores: number }
export interface Categoria { id: number; nome: string }
export interface Fornecedor { id: number; razao_social: string; cnpj: string; telefone?: string; email?: string }
export interface OpcaoProduto { id: number; sku: string; nome: string; estoque_atual: number }
export interface ProdutoOpcoes { categorias: Array<{id:number;nome:string}>; fornecedores: Array<{id:number;razao_social:string}>; produtos: OpcaoProduto[] }
export interface Movimentacao { id:number; sku:string; produto_nome:string; tipo:'ENTRADA'|'SAIDA'; quantidade:number; data_hora:string; observacao?:string }
