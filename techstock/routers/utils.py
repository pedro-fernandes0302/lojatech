from decimal import Decimal, InvalidOperation


def converter_preco(valor):
    return converter_centavos(valor) / 100


def converter_centavos(valor):
    texto = str(valor).strip().replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        quantizado = Decimal(texto).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ValueError("Preço inválido.") from exc
    return int(quantizado * 100)


def normalizar_cnpj(cnpj):
    return "".join(caractere for caractere in str(cnpj) if caractere.isdigit())


def validar_categoria_produto(tipo, modalidade):
    tipos_validos = {"Hardware", "Software", "Periferico"}
    modalidades_validas = {"Assinatura Anual", "Perpétua/ESD", "OEM"}
    tipo_normalizado = "Periferico" if tipo == "Periférico" else tipo
    return tipo_normalizado in tipos_validos and (not modalidade or modalidade in modalidades_validas)
