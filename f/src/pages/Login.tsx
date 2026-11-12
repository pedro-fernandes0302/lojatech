import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import AuthShell from '../components/AuthShell'
import { useAuth } from '../context/useAuth'

export default function Login() {
  const { entrar, erroSessao } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)
  const destino = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || '/'

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setErro('')
    setEnviando(true)
    try {
      await entrar(email.trim(), senha)
      navigate(destino, { replace: true })
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : 'Não foi possível entrar. Tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <AuthShell
      titulo="Boas-vindas"
      descricao="Entre com seus dados para acessar o painel de inventário."
      alternativa="Ainda não tem acesso?"
      linkAlternativa="/registrar"
      textoLink="Criar conta"
    >
      <form className="auth-form" onSubmit={enviar}>
        {(erro || erroSessao) && <div className="auth-error" role="alert">{erro || erroSessao}</div>}
        <label htmlFor="login-email">E-mail</label>
        <input
          id="login-email"
          type="email"
          name="email"
          autoComplete="email"
          placeholder="voce@empresa.com.br"
          value={email}
          onChange={evento => setEmail(evento.target.value)}
          required
        />
        <div className="auth-label-row">
          <label htmlFor="login-senha">Senha</label>
        </div>
        <input
          id="login-senha"
          type="password"
          name="senha"
          autoComplete="current-password"
          placeholder="Sua senha"
          value={senha}
          onChange={evento => setSenha(evento.target.value)}
          required
        />
        <button className="auth-submit" type="submit" disabled={enviando}>
          {enviando ? 'Entrando...' : 'Entrar no painel'}
          {!enviando && <span aria-hidden="true">↗</span>}
        </button>
      </form>
    </AuthShell>
  )
}
