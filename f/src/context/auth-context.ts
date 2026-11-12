import { createContext } from 'react'
import type { Usuario } from '../types'

export interface AuthContextValue {
  usuario: Usuario | null
  carregando: boolean
  erroSessao: string
  entrar: (email: string, senha: string) => Promise<void>
  registrar: (dados: { nome: string; email: string; senha: string }) => Promise<void>
  sair: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
