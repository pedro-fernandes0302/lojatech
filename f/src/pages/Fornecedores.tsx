import { useEffect, useState, type FormEvent } from 'react'
import Aviso from '../components/Aviso'
import PageHeader from '../components/PageHeader'
import { api } from '../services/api'
import type { Fornecedor } from '../types'

const inicial={razao_social:'',cnpj:'',telefone:'',email:''}
export default function Fornecedores(){const[lista,setLista]=useState<Fornecedor[]>([]);const[dados,setDados]=useState(inicial);const[erro,setErro]=useState('');const[mensagem,setMensagem]=useState('')
 const carregar=()=>api.fornecedores.listar().then(setLista).catch(e=>setErro(e.message));useEffect(()=>{carregar()},[])
 async function enviar(e:FormEvent){e.preventDefault();setErro('');setMensagem('');try{const r=await api.fornecedores.criar(dados);setMensagem(r.mensagem);setDados(inicial);carregar()}catch(e){setErro((e as Error).message)}}
 return <><PageHeader titulo="Fornecedores"/><Aviso mensagem={mensagem}/><Aviso tipo="erro" mensagem={erro}/><div className="two-column"><form className="compact-panel" onSubmit={enviar}><h2>Novo fornecedor</h2><label>Razão social *<input required value={dados.razao_social} onChange={e=>setDados({...dados,razao_social:e.target.value})}/></label><label>CNPJ *<input required placeholder="00.000.000/0000-00" value={dados.cnpj} onChange={e=>setDados({...dados,cnpj:e.target.value})}/></label><label>Telefone<input value={dados.telefone} onChange={e=>setDados({...dados,telefone:e.target.value})}/></label><label>E-mail<input type="email" value={dados.email} onChange={e=>setDados({...dados,email:e.target.value})}/></label><button className="primary-button">Cadastrar</button></form><section className="panel"><div className="table-wrap"><table><thead><tr><th>Razão social</th><th>CNPJ</th><th>Contato</th><th></th></tr></thead><tbody>{lista.map(f=><tr key={f.id}><td>{f.razao_social}</td><td>{f.cnpj}</td><td>{f.telefone||'-'}<br/><small>{f.email||'-'}</small></td><td><button className="danger-button" onClick={async()=>{if(confirm('Excluir este fornecedor?'))try{await api.fornecedores.excluir(f.id);carregar()}catch(e){setErro((e as Error).message)}}}>Excluir</button></td></tr>)}{!lista.length&&<tr><td colSpan={4} className="empty">Nenhum fornecedor.</td></tr>}</tbody></table></div></section></div></>
}
