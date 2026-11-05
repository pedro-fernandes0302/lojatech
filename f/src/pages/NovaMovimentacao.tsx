import { useEffect, useState, type FormEvent } from 'react'
import Aviso from '../components/Aviso'
import PageHeader from '../components/PageHeader'
import { api } from '../services/api'
import type { ProdutoOpcoes } from '../types'

export default function NovaMovimentacao(){
 const [opcoes,setOpcoes]=useState<ProdutoOpcoes>({categorias:[],fornecedores:[],produtos:[]});const [dados,setDados]=useState({produto_id:'',tipo:'ENTRADA',quantidade:'1',observacao:''});const [erro,setErro]=useState('');const [sucesso,setSucesso]=useState('')
 useEffect(()=>{api.produtos.opcoes().then(setOpcoes).catch(e=>setErro(e.message))},[])
 async function enviar(e:FormEvent){e.preventDefault();setErro('');setSucesso('');try{const r=await api.movimentacoes.criar({produto_id:Number(dados.produto_id),tipo:dados.tipo,quantidade:Number(dados.quantidade),observacao:dados.observacao});setSucesso(r.mensagem+(r.aviso_estoque?' Atenção: o saldo atingiu o nível mínimo.':''));const novas=await api.produtos.opcoes();setOpcoes(novas)}catch(e){setErro((e as Error).message)}}
 return <><PageHeader titulo="Movimentar estoque" subtitulo="Registre entradas e saídas"/><Aviso mensagem={sucesso}/><Aviso tipo="erro" mensagem={erro}/><form className="form-panel movement-form" onSubmit={enviar}><div className="form-grid"><label className="span-2">Produto *<select required value={dados.produto_id} onChange={e=>setDados({...dados,produto_id:e.target.value})}><option value="">Selecione</option>{opcoes.produtos.map(p=><option key={p.id} value={p.id}>{p.sku} - {p.nome} - saldo atual: {p.estoque_atual}</option>)}</select></label><label>Tipo *<select value={dados.tipo} onChange={e=>setDados({...dados,tipo:e.target.value})}><option value="ENTRADA">ENTRADA</option><option value="SAIDA">SAÍDA</option></select></label><label>Quantidade *<input type="number" min="1" step="1" required value={dados.quantidade} onChange={e=>setDados({...dados,quantidade:e.target.value})}/></label><label className="span-2">Observação<textarea value={dados.observacao} onChange={e=>setDados({...dados,observacao:e.target.value})}/></label></div><div className="form-actions"><button className="primary-button">Registrar movimentação</button></div></form></>
}
