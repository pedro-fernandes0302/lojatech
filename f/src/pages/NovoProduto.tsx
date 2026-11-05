import { useEffect, useState, type ChangeEvent, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import Aviso from '../components/Aviso'
import PageHeader from '../components/PageHeader'
import { api } from '../services/api'
import type { ProdutoOpcoes } from '../types'

const inicial={sku:'',nome:'',fabricante:'',tipo:'Hardware',especificacao:'',modalidade_licenca:'',preco:'',estoque_atual:'0',estoque_minimo:'0',localizacao:'',categoria_id:'',fornecedor_id:''}
export default function NovoProduto(){
 const [opcoes,setOpcoes]=useState<ProdutoOpcoes>({categorias:[],fornecedores:[],produtos:[]}); const [dados,setDados]=useState(inicial);const [mensagem,setMensagem]=useState('');const [erro,setErro]=useState('');const navegar=useNavigate()
 useEffect(()=>{api.produtos.opcoes().then(setOpcoes).catch(e=>setErro(e.message))},[])
 const alterar=(e:ChangeEvent<HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement>)=>setDados({...dados,[e.target.name]:e.target.value})
 async function enviar(e:FormEvent){e.preventDefault();setErro('');try{const r=await api.produtos.criar({...dados,categoria_id:Number(dados.categoria_id),fornecedor_id:Number(dados.fornecedor_id)});setMensagem(r.mensagem);setTimeout(()=>navegar('/'),900)}catch(e){setErro((e as Error).message)}}
 return <><PageHeader titulo="Novo produto" subtitulo="Cadastre hardware, periféricos ou licenças"/><Aviso mensagem={mensagem}/><Aviso tipo="erro" mensagem={erro}/><form className="form-panel" onSubmit={enviar}><div className="form-grid">
 <label>SKU *<input name="sku" value={dados.sku} onChange={alterar} required/></label><label>Nome *<input name="nome" value={dados.nome} onChange={alterar} required/></label><label>Fabricante *<input name="fabricante" value={dados.fabricante} onChange={alterar} required/></label>
 <label>Tipo *<select name="tipo" value={dados.tipo} onChange={alterar}><option value="Hardware">Hardware</option><option value="Software">Software</option><option value="Periferico">Periférico</option></select></label><label>Modalidade<select name="modalidade_licenca" value={dados.modalidade_licenca} onChange={alterar}><option value="">Não se aplica</option><option>Assinatura Anual</option><option>Perpétua/ESD</option><option>OEM</option></select></label><label>Preço (R$) *<input inputMode="decimal" name="preco" value={dados.preco} onChange={alterar} required/></label>
 <label>Estoque atual<input type="number" min="0" name="estoque_atual" value={dados.estoque_atual} onChange={alterar}/></label><label>Estoque mínimo<input type="number" min="0" name="estoque_minimo" value={dados.estoque_minimo} onChange={alterar}/></label><label>Localização *<input name="localizacao" value={dados.localizacao} onChange={alterar} required/></label>
 <label>Categoria *<select name="categoria_id" value={dados.categoria_id} onChange={alterar} required><option value="">Selecione</option>{opcoes.categorias.map(c=><option key={c.id} value={c.id}>{c.nome}</option>)}</select></label><label>Fornecedor *<select name="fornecedor_id" value={dados.fornecedor_id} onChange={alterar} required><option value="">Selecione</option>{opcoes.fornecedores.map(f=><option key={f.id} value={f.id}>{f.razao_social}</option>)}</select></label><label className="span-2">Especificação<textarea name="especificacao" value={dados.especificacao} onChange={alterar}/></label>
 </div><div className="form-actions"><button className="primary-button" type="submit">Salvar produto</button></div></form></>
}
