export interface Produto {
  id: number; sku: string; nome: string; fabricante: string; tipo: string;
  categoria: string; fornecedor: string; preco: number; estoque_atual: number;
  estoque_minimo: number; localizacao: string; modalidade_licenca: string | null;
  tipo_catalogo: 'Hardware Físico' | 'Licença Digital'; quantidade_fisica: number; chaves_disponiveis: number;
}
export interface DashboardResponse { produtos: Produto[]; categorias: number; fornecedores: number }
export interface Categoria { id: number; nome: string }
export interface Fornecedor { id: number; razao_social: string; cnpj: string; telefone?: string; email?: string }
export interface OpcaoProduto { id: number; sku: string; nome: string; estoque_atual: number }
export interface ProdutoOpcoes { categorias: Array<{id:number;nome:string}>; fornecedores: Array<{id:number;razao_social:string}>; produtos: Array<OpcaoProduto & {tipo:string;preco:number}>; clientes: Cliente[] }
export interface Movimentacao { id:number; sku:string; produto_nome:string; tipo:'ENTRADA'|'SAIDA'; quantidade:number; data_hora:string; observacao?:string }
export interface Cliente { id:number; nome:string; cnpj:string; email?:string }
export interface Sessao { id_usuario:number; nome:string; email:string; perfil:'GERENTE'|'OPERADOR' }
export interface ItemRecibo { sku:string; produto:string; quantidade:number; preco_unitario_centavos:number; subtotal_centavos:number }
export interface Recibo { id_venda:number; numero_pedido:string; data_venda:string; valor_total_centavos:number; cliente_nome:string; cliente_cnpj:string; cliente_email:string; operador:string; operador_email:string; itens:ItemRecibo[] }
export interface LinhaRazao { id:number; data_hora:string; tipo:string; quantidade:number; observacao?:string; sku:string; produto:string; numero_pedido?:string; id_venda?:number; cliente?:string; cnpj?:string; usuario?:string; perfil?:string }
