#!/usr/bin/env python3
"""
Item do Dia — Concursos Públicos
---------------------------------
Um programa rápido para aprender, aos poucos, os temas mais comuns em
concursos públicos generalistas (Português, Direito Constitucional,
Direito Administrativo, Raciocínio Lógico, Informática e Ética).

A cada execução:
  1. Pergunta quantos minutos você tem disponíveis agora.
  2. Pergunta o nível do texto (fácil / médio / difícil).
  3. Escolhe um item novo (que você ainda não viu) que caiba nesse
     tempo, nesse nível, e mostra o conteúdo + um link para saber mais.

O progresso fica salvo em "estado_concurso.json", na mesma pasta do
script, então cada execução traz um item diferente, sem repetir até
você ter visto todos.
"""

import json
import math
import os
import random
import re
import unicodedata
from urllib.parse import quote_plus

ARQUIVO_ESTADO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estado_concurso.json")

# Palavras por minuto usadas para estimar o tempo de leitura em cada nível.
VELOCIDADE = {"facil": 200, "medio": 160, "dificil": 120}

# Banco de itens: adicione os seus à vontade, seguindo este formato.
ITEMS = [
    {
        "titulo": "Crase",
        "categoria": "Língua Portuguesa",
        "textos": {
            "facil": "Crase é a junção da preposição 'a' com o artigo 'a' (ou 'as'), marcada pelo acento grave: à. Aparece antes de palavras femininas que pedem artigo, como em 'Fui à padaria'. Truque rápido: troque a palavra feminina por uma masculina; se a frase ficar com 'ao', há crase — 'Fui ao mercado'.",
            "medio": "A crase indica a fusão da preposição 'a' (exigida por um verbo ou nome) com o artigo definido feminino 'a'/'as'. Ocorre diante de palavras femininas determinadas, como em 'Refiro-me à proposta enviada ontem'. Também aparece em locuções adverbiais femininas ('à noite', 'às pressas'), locuções prepositivas ('à espera de') e conjuntivas ('à medida que'). Não se usa crase antes de verbos, de palavras masculinas ou, em geral, antes de pronomes de tratamento como 'Vossa Senhoria'. O truque da substituição por palavra masculina continua sendo um bom teste rápido em provas.",
            "dificil": "A crase é a fusão da preposição 'a', regida por um termo anterior (verbo ou nome transitivo indireto), com o artigo definido feminino 'a(s)' ou com o 'a' inicial de pronomes demonstrativos (aquele, aquela, aquilo). Além dos casos clássicos, bancas cobram exceções: crase facultativa antes de nomes próprios femininos ('Escrevi a/à Ana') e antes de pronomes possessivos femininos ('Entreguei o livro a/à sua colega'); crase proibida antes de verbos, de palavras masculinas, de artigo indefinido e, em regra, antes de pronomes pessoais e de tratamento; e crase obrigatória em expressões como 'à moda de' (mesmo oculta: 'bife à Parmegiana') e diante de 'à distância', 'à vista'. Nos casos de 'a' + 'a' repetidos, o acento também se aplica: 'Refiro-me àquela reunião'."
        }
    },
    {
        "titulo": "Concordância Verbal e Nominal",
        "categoria": "Língua Portuguesa",
        "textos": {
            "facil": "Concordância é a regra que faz o verbo 'combinar' com o sujeito e o adjetivo 'combinar' com o substantivo. Exemplo: 'Os alunos chegaram cedo' (verbo no plural porque o sujeito está no plural) e 'Casas grandes' (adjetivo no plural porque o substantivo está no plural).",
            "medio": "A concordância verbal exige que o verbo se ajuste em número e pessoa ao sujeito da oração, mesmo em casos menos óbvios, como sujeitos compostos ('Eu e você iremos') ou coletivos ('A maioria dos alunos chegou' ou 'chegaram', ambas aceitas). A concordância nominal ajusta artigos, adjetivos, pronomes e numerais ao gênero e número do substantivo a que se referem, incluindo casos como 'anexo' e 'obrigado', que variam conforme o gênero de quem fala ou do documento citado.",
            "dificil": "Além da regra geral de ajuste entre verbo e sujeito, a concordância verbal traz casos especiais cobrados em provas: sujeito representado por expressões partitivas ('a maioria', 'grande parte') admite concordância com o núcleo ou com o adjunto no plural; verbos como 'haver' (no sentido de existir) e 'fazer' (tempo decorrido) são impessoais e ficam sempre na 3ª pessoa do singular; o verbo 'ser' pode concordar com o predicativo em frases como 'Vinte reais é pouco'. Na concordância nominal, destacam-se os casos de adjetivo anteposto a múltiplos substantivos (concorda com o mais próximo ou vai ao plural) e palavras como 'meio' (advérbio, invariável: 'meio cansada') versus 'meio' (numeral, variável: 'meia maçã')."
        }
    },
    {
        "titulo": "Interpretação de Texto",
        "categoria": "Língua Portuguesa",
        "textos": {
            "facil": "Interpretar um texto é entender exatamente o que ele diz, sem inventar informações que não estão escritas. Nas provas, a resposta certa quase sempre pode ser encontrada nas próprias ideias do texto — desconfie de opções que exagerem, generalizem ou contrariem o que foi lido.",
            "medio": "Questões de interpretação cobram a diferença entre informação explícita (dita diretamente no texto) e implícita (que exige inferência, mas ainda baseada no texto). Erros comuns de quem responde são: extrapolar (trazer conhecimento de fora do texto), contradizer o texto ou generalizar demais um caso específico. Preste atenção também em conectivos ('mas', 'portanto', 'embora'), pois eles indicam a lógica argumentativa do autor.",
            "dificil": "Bancas avançadas exploram nuances como pressuposição (ideia subentendida pela estrutura da frase; ex.: 'ainda' sugere continuidade), ironia, ambiguidade proposital e a diferença entre a opinião do autor e a de terceiros citados no texto. É importante identificar o tipo de texto (dissertativo, narrativo, argumentativo) e sua tese central, além de reconhecer recursos coesivos (anáfora, catáfora, elipse) que ligam as partes do texto sem repetição literal de palavras."
        }
    },
    {
        "titulo": "Regência Verbal e Nominal",
        "categoria": "Língua Portuguesa",
        "textos": {
            "facil": "Regência é a relação entre um verbo (ou nome) e o complemento que ele exige, com ou sem preposição. Exemplo: 'assistir', no sentido de ver, pede a preposição 'a' — 'Assisti ao jogo' (e não 'Assisti o jogo').",
            "medio": "Muitos verbos mudam de regência conforme o sentido: 'esquecer' pode ser 'esqueci o nome' (sem preposição) ou 'esqueci-me do nome' (com 'de', quando pronominal). Verbos como 'obedecer', 'aspirar' (no sentido de desejar) e 'visar' (no sentido de pretender) também exigem preposição. Na regência nominal, certos substantivos e adjetivos pedem preposições fixas, como 'favorável a' e 'necessidade de'.",
            "dificil": "Casos de regência cobrados em provas avançadas incluem verbos com duplo regime a depender do sentido — 'chamar' (chamar alguém de algo / chamar por alguém) e 'implicar' (implicar algo, sem preposição, no sentido de acarretar) — e a regência do pronome relativo 'cujo', que dispensa artigo depois de si e concorda em gênero e número com o substantivo que o segue. Também é cobrada a regência de nomes derivados de verbos ('preferência a', mesmo quando coloquialmente se usa 'que'), além da diferença entre a regência formal e usos já consagrados pela norma culta."
        }
    },
    {
        "titulo": "Direitos e Garantias Fundamentais",
        "categoria": "Direito Constitucional",
        "textos": {
            "facil": "A Constituição de 1988 garante direitos básicos a todas as pessoas, como direito à vida, à liberdade, à igualdade, à segurança e à propriedade. Esses direitos estão principalmente no Artigo 5º da Constituição e valem tanto para brasileiros quanto para estrangeiros que estejam no país.",
            "medio": "Os direitos fundamentais se dividem em gerações (ou dimensões): os de 1ª geração são individuais e políticos (liberdade, participação); os de 2ª geração são sociais (educação, saúde, trabalho); os de 3ª geração são coletivos e difusos (meio ambiente, paz). O Art. 5º da CF/88 traz dezenas de incisos com garantias como devido processo legal, inviolabilidade de domicílio e liberdade de expressão, sendo considerados cláusulas pétreas — não podem ser abolidos nem por emenda constitucional.",
            "dificil": "Além da classificação em gerações, a doutrina discute a eficácia dos direitos fundamentais: normas de eficácia plena (aplicação imediata, sem necessidade de lei regulamentadora), contida (aplicação imediata, mas passível de restrição por lei) e limitada (dependem de lei para produzir todos os efeitos). Alguns direitos, embora fora do Art. 5º, também são considerados fundamentais pelo STF em razão do conteúdo material. Discute-se ainda a colisão entre direitos fundamentais (ex.: liberdade de expressão x direito à honra), resolvida pelo princípio da proporcionalidade e pela técnica de ponderação, caso a caso."
        }
    },
    {
        "titulo": "Separação dos Poderes",
        "categoria": "Direito Constitucional",
        "textos": {
            "facil": "O Brasil é dividido em três Poderes independentes e harmônicos entre si: o Executivo (que administra e executa as leis, chefiado pelo Presidente), o Legislativo (que cria as leis, formado por Câmara dos Deputados e Senado) e o Judiciário (que julga e aplica a lei aos casos concretos).",
            "medio": "A separação dos Poderes segue o sistema de 'freios e contrapesos' (checks and balances): cada Poder tem função típica, mas também exerce funções atípicas de controle sobre os outros. Por exemplo, o Legislativo pode fiscalizar o Executivo (CPIs) e o Judiciário pode declarar uma lei inconstitucional. O Executivo, por sua vez, pode vetar projetos de lei e editar medidas provisórias, que têm força de lei.",
            "dificil": "O princípio da separação de Poderes (Art. 2º da CF/88) é cláusula pétrea, mas não impede o exercício de funções atípicas: o Legislativo julga o Presidente em crimes de responsabilidade (função atípica judicante); o Judiciário edita normas administrativas internas (função atípica legislativa/administrativa); o Executivo legisla por medida provisória em casos de relevância e urgência. O controle de constitucionalidade pode ser difuso (exercido por qualquer juiz, em caso concreto) ou concentrado (exercido pelo STF, em ação direta, com efeito erga omnes), sendo este último uma forma de o Judiciário controlar os demais Poderes."
        }
    },
    {
        "titulo": "Princípios Fundamentais da CF/88",
        "categoria": "Direito Constitucional",
        "textos": {
            "facil": "Os primeiros artigos da Constituição trazem os fundamentos do Brasil como república: soberania, cidadania, dignidade da pessoa humana, valores sociais do trabalho e livre iniciativa, e pluralismo político. Também definem que todo poder emana do povo, que o exerce por meio de representantes eleitos ou diretamente, como em plebiscitos e referendos.",
            "medio": "Os fundamentos da República (Art. 1º) formam a base de interpretação de toda a Constituição, com destaque para a dignidade da pessoa humana, considerada pela doutrina um 'superprincípio'. Já os objetivos fundamentais (Art. 3º) são metas a alcançar, como erradicar a pobreza e reduzir desigualdades — usados por bancas para diferenciar 'fundamento' (o que o Estado já é) de 'objetivo' (o que o Estado busca ser).",
            "dificil": "A distinção entre fundamentos (Art. 1º), objetivos (Art. 3º) e princípios das relações internacionais (Art. 4º) é frequentemente cobrada em pegadinhas de prova, pois os três artigos usam listas semelhantes, mas com finalidades distintas: fundamentos são características estruturantes do Estado; objetivos são metas programáticas a serem perseguidas; princípios internacionais são diretrizes de conduta do Brasil no cenário externo, como autodeterminação dos povos, defesa da paz e repúdio ao terrorismo e ao racismo. O parágrafo único do Art. 1º também consagra a soberania popular por meio de democracia representativa e participativa (plebiscito, referendo e iniciativa popular)."
        }
    },
    {
        "titulo": "Princípios da Administração Pública (LIMPE)",
        "categoria": "Direito Administrativo",
        "textos": {
            "facil": "LIMPE é um mnemônico para lembrar os principais princípios da Administração Pública, previstos no Art. 37 da Constituição: Legalidade (só fazer o que a lei permite), Impessoalidade (tratar todos igualmente, sem favorecimento), Moralidade (agir com ética), Publicidade (dar transparência aos atos) e Eficiência (buscar bons resultados com menos desperdício).",
            "medio": "Cada princípio do LIMPE tem desdobramentos cobrados em prova: a Legalidade, para o particular, permite fazer tudo que a lei não proíbe; para a Administração, permite fazer só o que a lei autoriza. A Impessoalidade proíbe que atos públicos sejam usados para promoção pessoal de agentes, por isso publicidade institucional não pode ter nomes ou símbolos que caracterizem promoção pessoal. A Publicidade tem exceções, como sigilo em investigações ou proteção à intimidade.",
            "dificil": "Além dos cinco princípios expressos, a doutrina reconhece princípios implícitos igualmente cobrados, como Supremacia do Interesse Público, Autotutela (a Administração pode anular seus próprios atos ilegais ou revogar os inconvenientes, conforme a Súmula 473 do STF), Continuidade do Serviço Público, Razoabilidade e Proporcionalidade. A Eficiência foi incluída no Art. 37 pela EC 19/1998 e é frequentemente associada à ideia de Administração Pública Gerencial, em contraposição ao modelo burocrático clássico, focado em procedimentos, e não em resultados."
        }
    },
    {
        "titulo": "Atos Administrativos",
        "categoria": "Direito Administrativo",
        "textos": {
            "facil": "Ato administrativo é toda manifestação da Administração Pública que cria, modifica ou extingue direitos, como uma multa de trânsito, uma nomeação de servidor ou uma licença de construção. Para ser válido, o ato precisa ter competência (quem pode praticá-lo), finalidade, forma, motivo e objeto.",
            "medio": "Os atos administrativos têm atributos próprios que os diferenciam dos atos privados: presunção de legitimidade (presume-se que o ato é legal até prova em contrário), autoexecutoriedade (a Administração pode executar o ato sem precisar de autorização judicial, em certos casos) e imperatividade (impõe-se ao particular independentemente de sua concordância). Quanto aos requisitos, o vício de competência ou de forma pode, em regra, ser corrigido; já o vício de finalidade ou de motivo geralmente leva à nulidade do ato.",
            "dificil": "A classificação dos elementos do ato administrativo (competência, finalidade, forma, motivo e objeto) é fundamental para entender vícios e suas consequências: elementos vinculados (competência, finalidade e forma) admitem, em geral, convalidação quando o vício for sanável e não causar prejuízo; já motivo e objeto, especialmente em atos discricionários, envolvem o chamado 'mérito administrativo' (juízo de conveniência e oportunidade), que o Judiciário não pode substituir, apenas controlar quanto à legalidade — daí a distinção entre controle de legalidade e controle de mérito."
        }
    },
    {
        "titulo": "Licitações",
        "categoria": "Direito Administrativo",
        "textos": {
            "facil": "Licitação é o processo que a Administração Pública usa para escolher, de forma justa e transparente, quem vai fornecer um produto, serviço ou obra para o governo. A regra geral é que o poder público não pode simplesmente escolher um fornecedor sem abrir esse processo, para garantir igualdade entre as empresas interessadas.",
            "medio": "A licitação busca equilibrar três objetivos: selecionar a proposta mais vantajosa, garantir isonomia entre os concorrentes e promover o desenvolvimento nacional sustentável. Existem diferentes modalidades (como pregão, concorrência e diálogo competitivo) e critérios de julgamento (menor preço, melhor técnica, técnica e preço, entre outros), escolhidos conforme o tipo e a complexidade da contratação. Em alguns casos, a lei permite dispensa ou inexigibilidade de licitação, quando o processo não é obrigatório ou é inviável.",
            "dificil": "A Lei 14.133/2021 reformulou o regime de licitações e contratos administrativos, unificando regras antes espalhadas em normas como a antiga Lei 8.666/93 e a Lei do Pregão. Entre as novidades estão o diálogo competitivo (nova modalidade para contratações complexas), o julgamento por maior desconto e maior retorno econômico, e o fortalecimento do planejamento por meio do Plano de Contratações Anual. A diferença entre dispensa (licitação não obrigatória por opção legal, mesmo sendo viável) e inexigibilidade (licitação impossível por inviabilidade de competição, como na contratação de artista consagrado) segue sendo tema recorrente em provas."
        }
    },
    {
        "titulo": "Improbidade Administrativa",
        "categoria": "Direito Administrativo",
        "textos": {
            "facil": "Improbidade administrativa é quando um agente público (ou até um particular que participa do ato) age de forma desonesta contra a Administração Pública, causando prejuízo aos cofres públicos, enriquecendo-se ilicitamente ou violando princípios como a legalidade e a moralidade. A Lei 8.429/92 prevê punições como perda da função, multa e proibição de contratar com o poder público.",
            "medio": "A Lei de Improbidade Administrativa classifica os atos ímprobos em três categorias: os que causam enriquecimento ilícito (o agente obtém vantagem indevida), os que causam prejuízo ao erário (dano financeiro aos cofres públicos) e os que violam princípios da Administração. Após a reforma da Lei 14.230/2021, passou a ser exigido dolo (intenção) para caracterizar improbidade, afastando-se a antiga possibilidade de punição por mera culpa (negligência).",
            "dificil": "Desde a reforma promovida pela Lei 14.230/2021, a caracterização de improbidade administrativa exige comprovação de dolo específico, tornando o tema mais próximo do Direito Penal em termos de exigência probatória. A lei também unificou o prazo prescricional em 8 anos e restringiu a legitimidade para propor a ação, entre outras mudanças. É importante não confundir improbidade administrativa (esfera cível, com sanções como perda de função e multa) com crimes contra a Administração Pública (esfera penal, como peculato e corrupção), embora um mesmo fato possa gerar responsabilização nas duas esferas, além da administrativa disciplinar."
        }
    },
    {
        "titulo": "Regra de Três",
        "categoria": "Raciocínio Lógico-Matemático",
        "textos": {
            "facil": "Regra de três simples serve para descobrir um valor desconhecido quando duas grandezas são proporcionais. Exemplo: se 2 kg de arroz custam R$ 10, quanto custam 5 kg? Basta montar a proporção e multiplicar cruzado: X = (5 × 10) ÷ 2 = 25.",
            "medio": "Antes de montar a regra de três, é preciso identificar se as grandezas são diretamente proporcionais (uma aumenta, a outra também aumenta, na mesma razão) ou inversamente proporcionais (uma aumenta, a outra diminui). No caso direto, multiplica-se em cruz normalmente; no caso inverso, inverte-se uma das colunas antes de multiplicar. Exemplo clássico de proporção inversa: mais operários terminam uma obra em menos tempo.",
            "dificil": "Questões de raciocínio lógico costumam exigir regra de três composta, quando mais de duas grandezas estão envolvidas simultaneamente (por exemplo: operários, horas por dia e dias para concluir uma obra). O método consiste em fixar a grandeza que se quer descobrir de um lado e comparar cada uma das outras grandezas individualmente com ela, identificando se a relação é direta ou inversa antes de montar a equação final, multiplicando todas as razões corretamente ajustadas (invertidas quando inversamente proporcionais)."
        }
    },
    {
        "titulo": "Proposições Lógicas e Conectivos",
        "categoria": "Raciocínio Lógico-Matemático",
        "textos": {
            "facil": "Em raciocínio lógico, uma proposição é uma frase que pode ser classificada como verdadeira ou falsa, nunca as duas ao mesmo tempo. Exemplo: 'Brasília é a capital do Brasil' é uma proposição verdadeira. Perguntas ou ordens não são proposições, porque não têm valor lógico de verdadeiro ou falso.",
            "medio": "Proposições simples podem ser combinadas por conectivos lógicos para formar proposições compostas: 'e' (conjunção, verdadeira só se ambas forem verdadeiras), 'ou' (disjunção, verdadeira se pelo menos uma for verdadeira), 'se...então' (condicional, falsa apenas quando o antecedente é verdadeiro e o consequente é falso) e 'se e somente se' (bicondicional, verdadeira quando as duas proposições têm o mesmo valor lógico). Tabelas-verdade organizam todas as combinações possíveis desses valores.",
            "dificil": "Um dos pontos mais cobrados em prova é a negação de proposições compostas, que segue as Leis de De Morgan: a negação de 'A e B' equivale a 'não A ou não B', e a negação de 'A ou B' equivale a 'não A e não B'. Já a negação de uma condicional ('se A, então B') não é outra condicional, mas sim 'A e não B'. Também são cobrados os conceitos de tautologia (proposição sempre verdadeira, independentemente dos valores das proposições simples), contradição (sempre falsa) e equivalência lógica entre proposições com tabelas-verdade idênticas."
        }
    },
    {
        "titulo": "Segurança da Informação",
        "categoria": "Informática",
        "textos": {
            "facil": "Segurança da informação busca proteger dados contra acesso indevido, perda ou alteração. Os três pilares mais cobrados em prova são: Confidencialidade (só quem é autorizado acessa a informação), Integridade (a informação não pode ser alterada indevidamente) e Disponibilidade (a informação deve estar acessível quando necessário).",
            "medio": "Além da tríade CID (Confidencialidade, Integridade, Disponibilidade), provas cobram também Autenticidade (garantir que a informação vem de quem realmente diz ser a origem) e Não repúdio (o autor de uma ação não pode negar que a praticou, geralmente garantido por assinatura digital). Ameaças comuns incluem malware (vírus, worms, trojans, ransomware), phishing (engenharia social para roubo de dados) e ataques de força bruta a senhas.",
            "dificil": "Mecanismos técnicos costumam aparecer associados a cada princípio: criptografia simétrica e assimétrica protegem a confidencialidade; funções hash (como SHA-256) garantem integridade, permitindo detectar qualquer alteração no conteúdo original; certificados digitais, emitidos por Autoridades Certificadoras dentro de uma Infraestrutura de Chaves Públicas (ICP-Brasil), garantem autenticidade e não repúdio em documentos eletrônicos. É comum a prova diferenciar backup completo, incremental e diferencial quanto ao tempo de execução e ao espaço de armazenamento necessário para cada estratégia."
        }
    },
    {
        "titulo": "Ética no Serviço Público",
        "categoria": "Ética e Administração Pública",
        "textos": {
            "facil": "Ética no serviço público significa que o servidor deve agir com honestidade, respeito e zelo pelo interesse coletivo, colocando o bem comum acima de interesses pessoais. O Decreto 1.171/94 instituiu o Código de Ética Profissional do Servidor Público Civil Federal, que serve de referência para o tema.",
            "medio": "O Código de Ética do Servidor Público Federal trata a ética não apenas como opção pessoal, mas como dever jurídico ligado à moralidade administrativa, um dos princípios do Art. 37 da CF. O código lista deveres (como ser probo, reto e leal) e vedações (como usar o cargo para obter vantagens pessoais), além de prever a criação de Comissões de Ética nos órgãos públicos para orientar e apurar condutas.",
            "dificil": "A distinção entre ética, moral e legalidade é frequentemente explorada em provas: um ato pode ser legal, mas antiético; a imoralidade administrativa, por sua vez, é reconhecida pelo STF como causa autônoma de invalidação de atos, independentemente de ilegalidade estrita, distinguindo-se da improbidade administrativa, que exige dolo e gera sanções mais severas, previstas em lei específica. O tema também dialoga com a Lei de Acesso à Informação e a Lei Geral de Proteção de Dados, na medida em que a transparência e a ética se relacionam com o uso adequado da informação pública."
        }
    },
]


def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def salvar_estado(estado):
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def novo_ciclo():
    indices = list(range(len(ITEMS)))
    random.shuffle(indices)
    return indices


def remover_acentos(texto):
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalizar_nivel(bruto):
    limpo = remover_acentos(bruto.strip().lower())
    if limpo.startswith("f") or limpo.startswith("1"):
        return "facil"
    if limpo.startswith("d") or limpo.startswith("3"):
        return "dificil"
    return "medio"


def estimar_minutos(texto, nivel):
    palavras = len(texto.split())
    minutos = math.ceil(palavras / VELOCIDADE[nivel])
    return max(1, minutos)


def pedir_tempo():
    bruto = input("⏱️  Quantos minutos você tem disponíveis agora? ").strip()
    numeros = re.findall(r"\d+", bruto)
    if numeros and int(numeros[0]) > 0:
        return int(numeros[0])
    print("Não entendi, vou usar 5 minutos.")
    return 5


def pedir_nivel():
    bruto = input("📚 Nível do texto? (fácil / médio / difícil): ")
    return normalizar_nivel(bruto)


def main():
    estado = carregar_estado()
    if estado is None:
        estado = {"pendentes": novo_ciclo(), "historico": []}

    print("=== Item do Dia: Concursos Públicos ===\n")
    tempo_total = pedir_tempo()
    nivel = pedir_nivel()

    if not estado["pendentes"]:
        print("\n🔁 Você já viu todos os itens da lista! Recomeçando com uma nova ordem.")
        estado["pendentes"] = novo_ciclo()

    opcoes = [(idx, estimar_minutos(ITEMS[idx]["textos"][nivel], nivel)) for idx in estado["pendentes"]]
    cabem = [op for op in opcoes if op[1] <= tempo_total]

    if cabem:
        idx_escolhido, minutos = max(cabem, key=lambda op: op[1])
    else:
        idx_escolhido, minutos = min(opcoes, key=lambda op: op[1])
        print(f"\n(A leitura de hoje leva ~{minutos} min — um pouco mais do que os {tempo_total} min pedidos, mas vale a pena!)")

    estado["pendentes"].remove(idx_escolhido)
    item = ITEMS[idx_escolhido]
    texto = item["textos"][nivel]

    print(f"\n📂 {item['categoria']}")
    print(f"📖 {item['titulo']}\n")
    print(texto)
    print(f"\n🕒 Tempo estimado de leitura: ~{minutos} min (nível {nivel})")

    consulta = f"{item['titulo']} concurso público"
    link = f"https://www.google.com/search?q={quote_plus(consulta)}"
    print(f"🔗 Mais informações: {link}")

    estado["historico"].append({"titulo": item["titulo"], "nivel": nivel})
    salvar_estado(estado)

    print(f"\n📊 Total de itens estudados até agora: {len(estado['historico'])}")
    print(f"   Faltam {len(estado['pendentes'])} item(ns) para a lista reiniciar.")
    print("💡 Dica: conforme a concentração for aumentando, é só pedir mais minutos na próxima vez!")


if __name__ == "__main__":
    main()
