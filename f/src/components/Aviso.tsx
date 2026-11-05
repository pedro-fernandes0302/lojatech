export default function Aviso({tipo='sucesso', mensagem}: {tipo?: 'sucesso'|'erro'|'aviso'; mensagem:string}) {
  if (!mensagem) return null
  return <div className={`alert ${tipo}`}>{mensagem}</div>
}
