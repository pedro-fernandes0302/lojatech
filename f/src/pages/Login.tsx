import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [cadastro, setCadastro] = useState(false)
  const [nome, setNome] = useState('')
  const navegar = useNavigate()
  async function entrar(evento: FormEvent) {
    evento.preventDefault()
    setErro('')
    try {
      if (cadastro) await api.cadastro({ nome, email, senha })
      await api.login(email, senha)
      navegar('/')
    }
    catch (e) { setErro((e as Error).message) }
  }
  return <main className="login-page"><form className="form-panel" onSubmit={entrar}>
    <h1>TechStore</h1><p>{cadastro ? 'Cadastro de operador' : 'Acesse o sistema B2B'}</p>
    {erro && <div className="error-banner">{erro}</div>}
    {cadastro && <label>Nome<input required value={nome} onChange={e => setNome(e.target.value)} /></label>}
    <label>E-mail<input type="email" required value={email} onChange={e => setEmail(e.target.value)} /></label>
    <label>Senha<input type="password" required value={senha} onChange={e => setSenha(e.target.value)} /></label>
    <button className="primary-button">Entrar</button>
    <button type="button" className="primary-button" onClick={() => { setCadastro(!cadastro); setErro('') }}>{cadastro ? 'Voltar ao login' : 'Criar conta de operador'}</button>
  </form></main>
}
