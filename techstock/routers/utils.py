def converter_preco(valor):
    return float(str(valor).strip().replace(".", "").replace(",", "."))


def normalizar_cnpj(cnpj):
    return "".join(caractere for caractere in str(cnpj) if caractere.isdigit())


def validar_categoria_produto(tipo, modalidade):
    tipos_validos = {"Hardware", "Software", "Periférico"}
    modalidades_validas = {"Assinatura Anual", "Perpétua/ESD", "OEM"}
    return tipo in tipos_validos and (not modalidade or modalidade in modalidades_validas)
