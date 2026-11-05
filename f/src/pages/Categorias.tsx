import { useEffect, useState, type FormEvent } from 'react'
import Aviso from '../components/Aviso'
import PageHeader from '../components/PageHeader'
import { api } from '../services/api'
import type { Categoria } from '../types'

export default function Categorias(){const [lista,setLista]=useState<Categoria[]>([]);const[nome,setNome]=useState('');const[erro,setErro]=useState('');const[mensagem,setMensagem]=useState('')
 const carregar=()=>api.categorias.listar().then(setLista).catch(e=>setErro(e.message));useEffect(()=>{carregar()},[])
 async function enviar(e:FormEvent){e.preventDefault();setErro('');setMensagem('');try{const r=await api.categorias.criar(nome);setMensagem(r.mensagem);setNome('');carregar()}catch(e){setErro((e as Error).message)}}
 return <><PageHeader titulo="Categorias"/><Aviso mensagem={mensagem}/><Aviso tipo="erro" mensagem={erro}/><div className="two-column"><form className="compact-panel" onSubmit={enviar}><h2>Nova categoria</h2><label>Nome *<input required value={nome} onChange={e=>setNome(e.target.value)}/></label><button className="primary-button">Cadastrar</button></form><section className="panel"><div className="table-wrap"><table><thead><tr><th>Nome</th><th></th></tr></thead><tbody>{lista.map(c=><tr key={c.id}><td>{c.nome}</td><td><button className="danger-button" onClick={async()=>{if(confirm('Excluir esta categoria?'))try{await api.categorias.excluir(c.id);carregar()}catch(e){setErro((e as Error).message)}}}>Excluir</button></td></tr>)}{!lista.length&&<tr><td colSpan={2} className="empty">Nenhuma categoria.</td></tr>}</tbody></table></div></section></div></>
}
