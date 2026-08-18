#!/usr/bin/env python3
"""
Palavra do Dia
--------------
Toda vez que você roda este programa, ele te mostra uma palavra nova.
Se você já conhece, ele passa para a próxima. Se não conhece, mostra
o significado e um link para você ler mais sobre ela.

O progresso fica salvo em "estado_palavras.json", na mesma pasta do
script, então cada execução mostra uma palavra diferente da anterior.
"""

import json
import random
import os

ARQUIVO_ESTADO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estado_palavras.json")

# Banco de palavras: adicione as suas à vontade!
PALAVRAS = [
    {"palavra": "Serendipidade", "significado": "Capacidade de fazer descobertas felizes e inesperadas por acaso."},
    {"palavra": "Efêmero", "significado": "Que dura pouco tempo; passageiro, transitório."},
    {"palavra": "Sicofanta", "significado": "Pessoa bajuladora, que age com falsidade para agradar alguém poderoso."},
    {"palavra": "Lapidar", "significado": "Que é perfeito, digno de nota; ou o ato de burilar, aperfeiçoar algo."},
    {"palavra": "Idiossincrasia", "significado": "Modo de ser, de reagir ou de pensar próprio de uma pessoa ou grupo."},
    {"palavra": "Perene", "significado": "Que dura por muito tempo, contínuo, permanente."},
    {"palavra": "Anacrônico", "significado": "Que está fora de seu tempo; que não condiz com a época atual."},
    {"palavra": "Verossímil", "significado": "Que parece verdadeiro; que tem aparência de ser real ou possível."},
    {"palavra": "Ubíquo", "significado": "Que está presente em todos os lugares ao mesmo tempo."},
    {"palavra": "Volúvel", "significado": "Que muda de opinião ou de comportamento com facilidade; inconstante."},
    {"palavra": "Pletora", "significado": "Grande quantidade, abundância excessiva de algo."},
    {"palavra": "Inefável", "significado": "Que não pode ser expresso em palavras; indescritível."},
    {"palavra": "Cognato", "significado": "Palavra que tem a mesma origem ou raiz que outra."},
    {"palavra": "Diáfano", "significado": "Transparente, translúcido; que deixa passar a luz quase totalmente."},
    {"palavra": "Recôndito", "significado": "Que está escondido, oculto, de difícil acesso."},
    {"palavra": "Sagaz", "significado": "Que tem perspicácia, esperteza para perceber e entender rapidamente."},
    {"palavra": "Efusivo", "significado": "Que expressa sentimentos de forma intensa e calorosa."},
    {"palavra": "Prosaico", "significado": "Comum, sem originalidade ou emoção; relativo ao dia a dia."},
    {"palavra": "Quimera", "significado": "Ideia ou desejo irrealizável; fantasia, ilusão."},
    {"palavra": "Taciturno", "significado": "Que fala pouco, calado, de temperamento melancólico."},
]


def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def salvar_estado(estado):
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def gerar_ordem_embaralhada(tamanho):
    ordem = list(range(tamanho))
    random.shuffle(ordem)
    return ordem


def main():
    estado = carregar_estado()

    if estado is None or estado.get("indice", 0) >= len(estado.get("ordem", [])):
        ordem = gerar_ordem_embaralhada(len(PALAVRAS))
        estado = {"ordem": ordem, "indice": 0, "ja_conhecidas": [], "aprendidas_hoje": []}
        if estado["indice"] == 0 and os.path.exists(ARQUIVO_ESTADO):
            print("Você viu todas as palavras da lista! Recomeçando com uma nova ordem.\n")

    idx_palavra = estado["ordem"][estado["indice"]]
    item = PALAVRAS[idx_palavra]
    palavra = item["palavra"]

    print(f"📖 Palavra do dia: {palavra}")
    resposta = input("Você já conhece essa palavra? (s/n): ").strip().lower()

    if resposta.startswith("s"):
        print("Ótimo, mandando bem! 🎉")
        estado["ja_conhecidas"].append(palavra)
    else:
        link = f"https://www.dicio.com.br/{palavra.lower()}/"
        print(f"\n📚 Significado: {item['significado']}")
        print(f"🔗 Saiba mais em: {link}")
        estado["aprendidas_hoje"].append(palavra)

    estado["indice"] += 1
    salvar_estado(estado)

    restantes = len(estado["ordem"]) - estado["indice"]
    print(f"\nFaltam {restantes} palavra(s) até a lista recomeçar.")


if __name__ == "__main__":
    main()
