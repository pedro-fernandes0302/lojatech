import { useEffect, useState, type ReactNode } from 'react'
import { ApiError, api } from '../services/api'
import type { Usuario } from '../types'
import { AuthContext } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [erroSessao, setErroSessao] = useState('')

  useEffect(() => {
    let ativo = true
    api.auth.atual()
      .then(({ usuario: atual }) => { if (ativo) setUsuario(atual) })
      .catch((erro: unknown) => {
        if (!ativo || (erro instanceof ApiError && erro.status === 401)) return
        if (ativo) setErroSessao(erro instanceof Error ? erro.message : 'Não foi possível verificar sua sessão.')
      })
      .finally(() => { if (ativo) setCarregando(false) })

    return () => { ativo = false }
  }, [])

  async function entrar(email: string, senha: string) {
    const resposta = await api.auth.entrar(email, senha)
    setErroSessao('')
    setUsuario(resposta.usuario)
  }

  async function registrar(dados: { nome: string; email: string; senha: string }) {
    await api.auth.registrar(dados)
    await entrar(dados.email, dados.senha)
  }

  async function sair() {
    try {
      await api.auth.sair()
    } finally {
      setUsuario(null)
    }
  }

  return (
    <AuthContext.Provider value={{ usuario, carregando, erroSessao, entrar, registrar, sair }}>
      {children}
    </AuthContext.Provider>
  )
}
