import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Aviso from '../components/Aviso'
import PageHeader from '../components/PageHeader'
import { api } from '../services/api'
import type { Movimentacao } from '../types'

export default function Movimentacoes(){
 const [lista,setLista]=useState<Movimentacao[]>([]);const [erro,setErro]=useState('')
 useEffect(()=>{api.movimentacoes.listar().then(setLista).catch(e=>setErro(e.message))},[])
 function formatar(valor:string){try{return new Date(valor.replace(' ','T')+'Z').toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})}catch{return valor}}
 return <><PageHeader titulo="Histórico de movimentações" acao={<Link className="primary-button" to="/movimentacoes/nova">＋ Nova movimentação</Link>}/><Aviso tipo="erro" mensagem={erro}/><section className="panel"><div className="table-wrap"><table><thead><tr><th>Data / hora</th><th>Produto</th><th>Tipo</th><th>Quantidade</th><th>Observação</th></tr></thead><tbody>{lista.map(m=><tr key={m.id}><td>{formatar(m.data_hora)}</td><td><strong>{m.sku}</strong><br/><span>{m.produto_nome}</span></td><td><span className={`status ${m.tipo==='ENTRADA'?'ok':'risk'}`}>{m.tipo}</span></td><td>{m.quantidade}</td><td>{m.observacao||'-'}</td></tr>)}{!lista.length&&<tr><td colSpan={5} className="empty">Nenhuma movimentação registrada.</td></tr>}</tbody></table></div></section></>
}
