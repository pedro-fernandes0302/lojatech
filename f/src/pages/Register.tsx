import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import AuthShell from '../components/AuthShell'
import { useAuth } from '../context/useAuth'

export default function Register() {
  const { registrar, erroSessao } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [confirmacao, setConfirmacao] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)
  const destino = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || '/'

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setErro('')
    if (senha !== confirmacao) {
      setErro('As senhas não conferem.')
      return
    }

    setEnviando(true)
    try {
      await registrar({ nome: nome.trim(), email: email.trim(), senha })
      navigate(destino, { replace: true })
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : 'Não foi possível criar sua conta. Tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <AuthShell
      titulo="Crie seu acesso"
      descricao="Cadastre-se para acompanhar o inventário e as movimentações da operação."
      alternativa="Já possui uma conta?"
      linkAlternativa="/login"
      textoLink="Fazer login"
    >
      <form className="auth-form auth-register-form" onSubmit={enviar}>
        {(erro || erroSessao) && <div className="auth-error" role="alert">{erro || erroSessao}</div>}
        <label htmlFor="register-nome">Nome completo</label>
        <input
          id="register-nome"
          type="text"
          name="nome"
          autoComplete="name"
          maxLength={100}
          placeholder="Como podemos chamar você?"
          value={nome}
          onChange={evento => setNome(evento.target.value)}
          required
        />
        <label htmlFor="register-email">E-mail corporativo</label>
        <input
          id="register-email"
          type="email"
          name="email"
          autoComplete="email"
          placeholder="voce@empresa.com.br"
          value={email}
          onChange={evento => setEmail(evento.target.value)}
          required
        />
        <label htmlFor="register-senha">Senha</label>
        <input
          id="register-senha"
          type="password"
          name="senha"
          autoComplete="new-password"
          minLength={8}
          maxLength={128}
          placeholder="Mínimo de 8 caracteres"
          value={senha}
          onChange={evento => setSenha(evento.target.value)}
          required
        />
        <label htmlFor="register-confirmacao">Confirme a senha</label>
        <input
          id="register-confirmacao"
          type="password"
          name="confirmacao"
          autoComplete="new-password"
          minLength={8}
          maxLength={128}
          placeholder="Digite a senha novamente"
          value={confirmacao}
          onChange={evento => setConfirmacao(evento.target.value)}
          required
        />
        <p className="auth-role-note">Novas contas recebem acesso de operador.</p>
        <button className="auth-submit" type="submit" disabled={enviando}>
          {enviando ? 'Criando conta...' : 'Criar conta'}
          {!enviando && <span aria-hidden="true">↗</span>}
        </button>
      </form>
    </AuthShell>
  )
}
