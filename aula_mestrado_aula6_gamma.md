<!--
AULA 6 — MESTRADO · "Segurança em LLMs II: dados, defesa em camadas e avaliação de risco"

O que é este arquivo: segunda das duas aulas de mestrado derivadas do curso "LLM Security". A Aula 5 cobriu o modelo
por dentro, o OWASP Top 10 para LLMs 2025 e as superfícies de ataque por arquitetura. Esta aula cobre dados, privacidade
e LGPD (Bloco 4), mitigações em camadas (Bloco 5) e o método de avaliação de risco (Bloco 6), com três laboratórios.
O conteúdo programático é o mesmo do curso; títulos e ganchos (cenários) são próprios, todos no universo fictício
"Campus Aurora" (Aurora Assist, Acervo Aurora, Agenda Lab, Comitê de Bolsas, Notebook do grupo, API do Histórico),
com dados 100% sintéticos.

Tempo total: ~3h15 (abertura 10 + Bloco 4 30 + Bloco 5 30 + intervalo 15 + Bloco 6 35 + laboratórios 60 + encerramento 15).

Laboratórios (pasta exemplos_aula_mestrado/, somente biblioteca padrão do Python 3, sem rede, ferramentas simuladas):
  Laboratório 5 — python3 exemplos_aula_mestrado/aula6/lab5_dados_na_fronteira.py (e com --defesa)
  Laboratório 6 — python3 exemplos_aula_mestrado/aula6/lab6_queijo_suico.py (e com --defesa)
  Laboratório 7 — python3 exemplos_aula_mestrado/aula6/lab7_avaliacao.py (lê aula6/sistema_exemplo.json; e com --defesa)

Padrão dos bullets: prosa corrida, 3 a 4 por slide, com a implicação de segurança embutida na frase.
Mantidos: PT-BR, sem matemática pesada, segurança defensiva (todo ataque com mitigação), OWASP sempre 2025, diagramas
nativos do Gamma (nunca ASCII), sem emoji.

Como usar no Gamma: Create new → Paste in text, modo "preservar texto", imagens = None.
Os comentários LAYOUT/ROTEIRO são notas para quem apresenta — o Gamma os ignora na importação.
-->

---

# Segurança em LLMs II: dados, defesa em camadas e avaliação de risco

<!--
LAYOUT: capa com título grande, subtítulo "Cyber Security & Governance — Cloud DevOps Security", autor abaixo; preserve o canto inferior direito para a facecam, se a aula for gravada.
ROTEIRO: abra a segunda aula. Apresente-se brevemente e diga que hoje a pergunta muda: da aula anterior ("onde o sistema quebra") para "como conter o estrago e como avaliar qualquer sistema com LLM".
-->

- Tharles Freire — gerente de DevSecOps e SRE; professor de Cloud Security e DevSecOps na FIAP; mestre em Computação Aplicada pelo Mackenzie.
- tharles.freire@heyupcharly.com.br
- Aula 6 · 2026

---

## Objetivos de aprendizagem
_introdução_

<!--
LAYOUT: lista de objetivos como verbos no infinitivo, um por linha.
ROTEIRO: gancho do slide: o que o aluno consegue fazer ao sair. Leia os cinco objetivos como um contrato e diga que dois deles serão medidos nos laboratórios, onde cada defesa é ligada e desligada para ver o efeito.
-->

- Distinguir os dois caminhos por onde um dado escapa de um sistema com LLM, memorização nos pesos e exfiltração pelo contexto, e escolher a defesa certa para cada um.
- Relacionar finalidade, minimização e direitos do titular da LGPD a decisões concretas de projeto de um assistente.
- Montar uma defesa em camadas e demonstrar, com experimento, que nenhuma camada sozinha contém todos os ataques.
- Aplicar o método de quatro passos, com STRIDE e fronteiras de confiança, a um sistema novo.
- Redigir um achado e comunicá-lo a quem decide em linguagem de consequência, não de sigla.

---

## Roteiro da aula (~3h15, com intervalo)
_introdução_

<!--
LAYOUT: tabela ou timeline nativa do Gamma com blocos e horários: abertura 0:00–0:10; Bloco 4 0:10–0:40; Bloco 5 0:40–1:10; intervalo 1:10–1:25; Bloco 6 1:25–2:00; laboratórios 2:00–3:00; encerramento 3:00–3:15.
ROTEIRO: gancho do slide: o contrato de tempo. Os blocos teóricos somam 95 minutos e os laboratórios 60; com abertura (10), intervalo (15) e encerramento (15) a aula fecha em exatamente 3h15, sem folga embutida. Se os laboratórios atrasarem, encurte a discussão do encerramento, que é o bloco mais elástico. Avise que há leitura complementar e um exercício opcional.
-->

- Abertura, 10 minutos: recapitulação do mapa de ataque da aula anterior.
- Bloco 4, 30 minutos, dados, privacidade e LGPD; Bloco 5, 30 minutos, mitigações e controles em camadas.
- Intervalo de 15 minutos. Em seguida, Bloco 6, 35 minutos, o método de avaliação de risco.
- Laboratórios 5, 6 e 7, cerca de 20 minutos cada, totalizando 60 minutos.
- Encerramento, 15 minutos: síntese, leitura complementar e exercício opcional extraclasse. Total aproximado de 3h15.

---

## Onde paramos: o mapa de ataque da aula anterior
_introdução_

<!--
LAYOUT: três cartões lado a lado (duas raízes · Top 10 2025 · seis arquiteturas), cada um com uma frase; seta apontando para "hoje: o que fazer a respeito".
ROTEIRO: gancho do slide: recapitulação em dois minutos. Pergunte à turma, antes de mostrar o slide, qual a arquitetura do Aurora Assist e do Comitê de Bolsas. Feche dizendo que a aula anterior terminou em diagnóstico e esta termina em tratamento.
-->

- Duas raízes explicam quase tudo: instrução e dado dividem o mesmo texto, e o comportamento do modelo é probabilístico, então nenhum conserto dentro do modelo resolve.
- O OWASP Top 10 para LLMs 2025, um documento de conscientização e não uma norma, deu nome e ordem aos riscos, com LLM07 e LLM08 novos.
- Vimos seis arquiteturas, do chat à API exposta, e cada uma acende uma camada nova de risco: perguntar "qual arquitetura eu tenho?" vem antes de qualquer controle.
- Hoje o foco é o que acontece com o dado, como conter o estrago quando o modelo falha e como avaliar um sistema de ponta a ponta.

---

<!-- ═══ BLOCO 4 · Dados, privacidade e LGPD · ~30 min (0:10–0:40) ═══
Objetivo: fixar a distinção entre memorização (pesos) e exfiltração (contexto) e as obrigações legais e contratuais que cercam qualquer sistema com LLM que toque dado pessoal.
-->

## Dois caminhos por onde o dado escapa
_introdução_

<!--
LAYOUT: diagrama nativo do Gamma com dois caminhos paralelos saindo do modelo: "pesos (treino, memória longa)" e "contexto vivo (sessão atual)", cada um com causa e defesa.
ROTEIRO: gancho do slide: dois vazamentos de natureza oposta no mesmo sistema. Peça à turma um exemplo de cada no Campus Aurora e deixe claro que causas e defesas diferem; misturar os dois leva a comprar a defesa errada.
-->

- O primeiro caminho passa pelos pesos: o que o treino ou o ajuste fino gravou pode reaparecer meses depois, e apagar isso depois de pronto é caro ou parcial.
- O segundo passa pelo contexto vivo: o prompt do sistema, os trechos recuperados e as saídas de ferramentas estão na sessão agora, e uma injeção pode mandá-los para fora.
- Defender os pesos pede cuidado com os dados de treino; defender o contexto pede controle de acesso, menos dado na janela e filtro do que sai.

---

## O que o treino decorou: as atas que o modelo ajustado completa
_conteúdo_

<!--
LAYOUT: linha do tempo em três passos: "ajuste fino com atas de colegiado" → "prompt que provoca repetição" → "nomes de processo disciplinar reaparecem"; abaixo, faixa com mitigações parciais.
ROTEIRO: gancho do slide: um modelo ajustado com atas internas de colegiado do Campus Aurora passa a completar nomes de envolvidos em processos disciplinares. Cite Nasr et al. (Google DeepMind, 2023) e o ataque de divergência contra o ChatGPT. Conduza o debate: como atender um pedido de exclusão do art. 18 se o dado está nos pesos?
-->

- Sequências raras ou repetidas, como nomes, e-mails e chaves, podem ficar gravadas nos pesos; um modelo ajustado com atas internas de colegiado pode completá-las a quem souber provocá-lo.
- Nasr et al. (Google DeepMind, 2023) mostraram, com o ataque de divergência contra o ChatGPT, que dados de treino reais podem ser extraídos de um modelo em produção.
- O direito de eliminação do art. 18 da LGPD colide com isso: apagar de dentro dos pesos significa, na prática, retreinar.
- As mitigações são parciais: deduplicar o corpus, remover PII antes do treino, usar privacidade diferencial quando viável e filtrar a saída; a mais segura é não treinar com o dado.

---

## Exfiltração pelo contexto: o aviso que levou a lista de bolsistas
_conteúdo_

<!--
LAYOUT: fluxo em quatro passos: "chamado com instrução oculta" → "agente da Agenda Lab chama enviar_aviso" → "destino externo no campo para" → "lista de bolsistas no corpo do e-mail"; faixa lateral "mesmo princípio: link ou imagem renderizados".
ROTEIRO: gancho do slide: ninguém roubou a lista de bolsistas; o próprio agente a enviou. Explique o confused deputy: o atacante não tem acesso, mas o modelo tem, e obedece. Mostre que o mesmo vale para uma URL de imagem ou link renderizado na resposta. Antecipe o Laboratório 5.
-->

- Um chamado com instrução escondida leva o agente da Agenda Lab a chamar enviar_aviso para um endereço de fora, com a lista de bolsistas no corpo da mensagem.
- É o problema do delegado confuso: o atacante não tem acesso a nada, mas o modelo tem, e a injeção só precisa convencê-lo a usar o que já pode.
- O mesmo princípio vale para uma imagem ou um link na resposta, cuja URL carrega o dado quando o navegador a busca ao renderizar.
- A defesa combina lista de destinos permitidos para tudo que sai (egress), menos dado exposto na janela de contexto e monitoramento de envios fora do padrão.

---

## Permissão antes da busca: as teses embargadas
_conteúdo_

<!--
LAYOUT: diagrama com dois alunos de programas diferentes consultando o mesmo índice; num lado o filtro de permissão está depois da busca (vaza), no outro está antes (barra).
ROTEIRO: gancho do slide: o Acervo Aurora devolve trecho de uma tese sob embargo a um aluno de outro programa. Reforce: busca vetorial mede similaridade, não autorização. Conecte com LLM08 da aula anterior e com a inversão de embedding.
-->

- A busca semântica ordena por semelhança, não por permissão, então uma pergunta bem formulada pode trazer um trecho de tese embargada do PPG-Saúde para um aluno do PPG-Computação.
- O filtro de permissão precisa entrar na própria consulta ao índice; aplicá-lo depois, sobre os trechos já recuperados, deixa o dado passar pelo contexto do modelo.
- Guardar apenas o vetor não anonimiza: técnicas de inversão de embedding conseguem reconstruir parte do texto de origem.
- Controle também quem pode indexar, pois um índice sem dono de cada documento mistura permissões e dificulta qualquer auditoria.

---

## Quando o prompt cruza a fronteira: atas coladas num chatbot gratuito
_conteúdo_

<!--
LAYOUT: diagrama "infraestrutura do Campus Aurora" → fronteira → "provedor externo", com a ata cruzando a linha; ao lado, três cartas: retenção, treino, país.
ROTEIRO: gancho do slide: a coordenação de um programa cola atas com dados de alunos num chatbot gratuito para ganhar tempo. Caso real: o Garante italiano suspendeu temporariamente o ChatGPT em março de 2023 por questões de proteção de dados. Discuta controles além da proibição: o que a política deve oferecer no lugar.
-->

- A coordenação cola atas com nomes e matrículas num chatbot gratuito para resumi-las; o provedor pode reter o texto, usá-lo para treino e processá-lo fora do país.
- O caso real mais citado é a decisão do Garante italiano, que suspendeu temporariamente o ChatGPT no país em março de 2023 por questões de proteção de dados.
- Reduzir o risco começa por minimizar e redigir dados pessoais antes do envio, depois escolher planos corporativos com cláusulas de não treino e retenção limitada.
- Para dados muito sensíveis, combine prevenção de perda de dados (DLP), política com treinamento e, se necessário, hospedagem própria do modelo.

---

## LGPD aplicada ao assistente: finalidade, minimização e direitos
_conteúdo_

<!--
LAYOUT: três colunas nativas: "finalidade e base legal", "direitos do titular", "transferência internacional e RIPD", com uma nota "PL 2338/2023 — conferir o status na data da aula" no rodapé.
ROTEIRO: gancho do slide: a segunda via de declaração precisa de nome e matrícula, não do histórico completo. Use o exemplo para mostrar minimização como decisão de projeto e não como burocracia. Sobre o PL 2338/2023, diga que foi aprovado no Senado em dezembro de 2024 e tramita na Câmara, e que é preciso conferir o status na data da aula.
-->

- Uma segunda via de declaração exige nome e matrícula, não o histórico completo: a finalidade define o dado necessário, e enviar mais ao modelo do que isso fere a minimização.
- Todo tratamento precisa de base legal, inclusive o envio de dado pessoal a um LLM; documente qual é antes de colocar o assistente em produção.
- Os direitos do art. 18, como acesso, correção e eliminação, convivem mal com a memorização, o que reforça manter dado pessoal fora do treino.
- Enviar dados a um provedor no exterior aciona o Capítulo V da LGPD, e o RIPD é o registro adequado para operações de maior risco.
- O PL 2338/2023, o Marco Legal da IA, foi aprovado no Senado em dezembro de 2024 e tramita na Câmara: conferir o status na data da aula.

---

## Três perguntas ao fornecedor
_conteúdo_

<!--
LAYOUT: tabela comparando "plano gratuito" e "plano corporativo" nas três perguntas: treina com meus dados? quanto retém e com quem? em que região processa?
ROTEIRO: gancho do slide: a Aurora compara o plano gratuito com o corporativo de um provedor. Peça que a turma preencha a tabela com o que esperaria de cada coluna e lembre que os termos mudam, então sempre se lê a versão vigente.
-->

- A Aurora precisa de três respostas por escrito antes de contratar: o provedor treina com os meus dados, por quanto tempo e com quais subprocessadores ele os retém, e em que região processa e armazena.
- Planos gratuitos costumam ter condições de treino e retenção mais amplas, por isso dado institucional nunca deve passar por conta pessoal ou plano de consumo.
- Termos de uso e políticas mudam: leia a versão vigente, guarde a evidência da data e reavalie quando houver atualização.

---

## Pesos e contexto, lei e fornecedor: o resumo do bloco
_conclusão_

<!--
LAYOUT: síntese em duas linhas: canais (pesos × contexto) e camadas (lei × política do provedor), com a frase "minimizar" destacada.
ROTEIRO: gancho do slide: fechar o bloco com uma regra que cabe numa frase. Pergunte qual dos dois canais a turma considera mais difícil de remediar depois do fato e por quê.
-->

- Memorização e exfiltração têm causas e defesas diferentes: uma nasce no treino e é difícil de desfazer, a outra acontece na sessão e se contém com controle de acesso e filtro de saída.
- A lei define o que a instituição pode fazer com o dado; a política do provedor define o que acontece com ele depois que sai.
- Minimizar o que entra no treino, no contexto e no prompt é a defesa mais barata e a única que vale para os dois canais.

---

<!-- ═══ BLOCO 5 · Mitigações e controles · ~30 min (0:40–1:10) ═══
Objetivo: virar a chave de ataque para defesa: as camadas que contêm o estrago quando o modelo falha, e ele vai falhar.
-->

## Queijo suíço: camadas imperfeitas que se sobrepõem
_introdução_

<!--
LAYOUT: diagrama nativo de fatias de queijo suíço alinhadas, com furos em posições diferentes e uma seta atravessando só onde os furos coincidem.
ROTEIRO: gancho do slide: a metáfora do queijo suíço. Cada fatia tem furos; o dano só chega ao fim quando os furos se alinham. Prepare o Laboratório 6, onde a turma verá isso em números.
-->

- Nenhum controle isolado barra a injeção de prompt, e a causa está nas duas raízes do modelo, não numa falha de implementação que um patch resolva.
- Cada camada tem furos, mas furos em lugares diferentes: o dano só atravessa quando todos se alinham, por isso a segurança vem de sobrepor controles imperfeitos.
- Projetar para a falha significa assumir que o modelo será enganado e limitar o raio de ação do estrago, em vez de tentar torná-lo infalível.

---

## Validar a entrada: o formulário da ouvidoria
_conteúdo_

<!--
LAYOUT: fluxo "texto do aluno" → "separação de papéis + sanitização" → "modelo", com uma observação em destaque: "sozinho, é burlável".
ROTEIRO: gancho do slide: a ouvidoria do Campus Aurora recebe texto livre que alimenta o assistente. Mostre o que a camada de entrada faz bem (reduz o ruído) e o que não faz (não entende intenção). Lembre que o filtro de palavras foi burlado na aula anterior.
-->

- Separe os papéis: instruções do sistema num canal e o texto do usuário em outro, e peça ao modelo que trate o que vem do aluno como dado a analisar, nunca como ordem.
- Sanitize antes de enviar: normalize Unicode, remova HTML e marcação suspeitos, limite o tamanho e delimite claramente o conteúdo não confiável.
- Aplique o mesmo cuidado ao que entra no índice do RAG, porque um documento envenenado indexado vira entrada de todo mundo.
- Um filtro de palavras sozinho é burlável por grafia, idioma ou paráfrase; a validação de entrada é uma fatia do queijo, nunca a defesa principal.

---

## Validar a saída: nada que o modelo escreveu vai direto a um sistema
_conteúdo_

<!--
LAYOUT: fluxo "saída do modelo" → "schema · codificação · parametrização · lista de destinos" → "sistema que consome".
ROTEIRO: gancho do slide: a regra "nenhum texto gerado vai direto a um shell, uma query ou um navegador". Explique por que a saída é mais fácil de validar: o formato esperado é conhecido, ao contrário da intenção do usuário. Conecte com o Laboratório 5 (egress e PII).
-->

- Trate a saída como entrada não confiável: valide contra um schema esperado, codifique antes de renderizar no navegador e parametrize qualquer consulta ou comando.
- Nunca passe texto gerado a eval ou a uma chamada de shell: o nome de arquivo sugerido pelo modelo e a query montada a partir de texto livre são injeção de comando à espera.
- Restrinja os destinos de e-mail e de URL por lista de permissão, e varra a saída em busca de segredos e dados pessoais antes de entregá-la.
- Validar a saída costuma ser mais confiável do que validar a entrada, porque confere um formato conhecido em vez de tentar adivinhar intenção.

---

## Menor privilégio: da Agenda Lab que cancelava tudo ao pedido de confirmação
_conteúdo_

<!--
LAYOUT: escada de três degraus: "somente leitura" → "credenciais efêmeras com escopo estreito + sandbox" → "aprovação humana para o irreversível"; ao lado, o antes (cancelar_reserva aberto) e o depois.
ROTEIRO: gancho do slide: voltar à Agenda Lab da aula anterior, que podia cancelar qualquer reserva. Mostre que, com a ferramenta restrita, uma injeção obedecida não tem poder de execução. É o controle de maior retorno.
-->

- Dê ao agente da Agenda Lab ferramentas somente de leitura por padrão, credenciais efêmeras com escopo estreito e um ambiente isolado para o que precisa executar.
- Exija aprovação humana nas ações irreversíveis ou de alto impacto, como cancelar a reserva de uma banca ou alterar a situação de matrícula.
- É a defesa primária contra agência excessiva e também contém uma injeção bem-sucedida: o modelo obedece ao atacante, mas não tem permissão para fazer o estrago.
- Revise as permissões a cada nova ferramenta, porque o privilégio tende a crescer por conveniência e raramente é revisto.

---

## Guardrails: um classificador que também erra
_conteúdo_

<!--
LAYOUT: diagrama com uma camada de política envolvendo o modelo, checando entrada e saída; abaixo, três exemplos de produto (Azure AI Content Safety, Amazon Bedrock Guardrails, Guardrails AI) e uma nota "contornável".
ROTEIRO: gancho do slide: a mesma intenção, reescrita em outro idioma ou como tradução, passa pelo classificador. Diga que os exemplos são produtos reais e que os termos e capacidades mudam, então a turma deve consultar a documentação vigente. Mensagem: útil, mas nunca única.
-->

- Guardrails são uma camada de política que avalia entrada e saída contra regras; Azure AI Content Safety, Amazon Bedrock Guardrails e Guardrails AI são exemplos de produtos nessa categoria.
- São classificadores e, portanto, erram: a mesma intenção reescrita em outro idioma, em tradução ou em forma de história pode passar ao largo da política.
- Brilham contra ataques de baixo esforço e ajudam a padronizar uma política entre equipes, mas só têm valor dentro da defesa em camadas.
- Consulte a documentação vigente de cada produto, e teste a camada com os seus próprios ataques em vez de confiar em taxas de acerto genéricas.

---

## Monitorar e responder: alertas que não criam outro problema
_conteúdo_

<!--
LAYOUT: diagrama de sinais (custo por sessão, chamadas de ferramenta fora do padrão, assinaturas de jailbreak) convergindo para um alerta e um playbook de resposta.
ROTEIRO: gancho do slide: o monitoramento é o que avisa quando as outras camadas falham. Chame atenção para o paradoxo: logs de conversa são dado pessoal e precisam de cuidado próprio.
-->

- Como nenhum controle é infalível, monitorar é o que permite saber quando uma camada falhou: acompanhe custo agregado por sessão e por usuário, não só por requisição.
- Observe chamadas de ferramenta fora do padrão, como envios para destinos novos, e assinaturas conhecidas de jailbreak nos registros.
- Pseudonimize os logs: a conversa traz dado pessoal, e resolver um problema de segurança não deve criar um de privacidade.
- Feche o ciclo com red-teaming periódico e um playbook de incidente que diga quem aciona o quê quando o alerta disparar.

---

## Camadas, privilégio e detecção
_conclusão_

<!--
LAYOUT: três blocos em sequência formando a fórmula: "camadas imperfeitas" + "menor privilégio" + "detecção".
ROTEIRO: gancho do slide: a fórmula do bloco em uma frase. Diga que é postura de engenharia, não receita, e que desconfiar do que se vende como definitivo faz parte do ofício.
-->

- A fórmula do bloco é sobrepor camadas imperfeitas, limitar o poder que o modelo tem e detectar o que escapar.
- Conter o estrago pesa mais do que prevenir toda tentativa, porque o modelo vai ser enganado em algum momento.
- Desconfie de qualquer produto ou prática vendido como solução definitiva para injeção de prompt; o que existe é redução de risco medida.

---

## Intervalo de 15 minutos
_introdução_

<!--
LAYOUT: slide limpo, com a hora de retorno em destaque.
ROTEIRO: avise o horário de volta. Deixe uma pergunta para pensar durante o intervalo: se você só pudesse manter uma camada de defesa no Aurora Assist, qual seria e o que ficaria exposto?
-->

- Retornamos em 15 minutos para o método de avaliação, o Bloco 6.
- Para pensar no intervalo: se só uma camada de defesa pudesse ficar no Aurora Assist, qual seria, e o que ficaria exposto sem as outras?

---

<!-- ═══ BLOCO 6 · Método de avaliação de risco · ~35 min (1:25–2:00) ═══
Objetivo: juntar os cinco blocos anteriores num processo repetível para avaliar qualquer sistema com LLM e comunicar o resultado a quem decide.
-->

## Quatro passos para avaliar qualquer sistema com LLM
_introdução_

<!--
LAYOUT: diagrama de quatro passos em sequência: entender → levantar ameaças → avaliar controles → priorizar.
ROTEIRO: gancho do slide: um roteiro que serve para o Aurora Assist, para o Comitê de Bolsas e para o sistema que a turma encontrar no trabalho. Relacione cada passo ao bloco anterior em que o conteúdo foi visto.
-->

- Entender vem primeiro: mapear a cadeia de componentes e identificar a arquitetura, chat, RAG, agente ou multi-agente, antes de falar em risco.
- Levantar ameaças combina o Top 10 2025 como vocabulário com a modelagem de ameaças, para não depender só da memória da lista.
- Avaliar controles é perguntar, para cada ameaça, qual camada do Bloco 5 a cobre, e registrar onde nenhuma cobre.
- Priorizar pela combinação de impacto e probabilidade define a ordem de correção, porque nem todo achado merece o mesmo esforço.

---

## STRIDE emprestado do software tradicional
_conteúdo_

<!--
LAYOUT: tabela com as seis letras do STRIDE e, ao lado, os riscos do Top 10 2025 que mais aderem a cada uma.
ROTEIRO: gancho do slide: reaproveitar um método que o aluno já conhece da engenharia de software. Mostre o mapeamento e diga que Spoofing e Repudiation atravessam o sistema inteiro, e por isso são tratados por autenticação e registro, não por um controle específico de LLM. Um mesmo risco pode cair em mais de uma letra (a injeção aparece em Tampering e em Elevation), e a desinformação (LLM09) não cabe bem em nenhuma: é um problema de veracidade, tratado com grounding e revisão.
-->

- Adulteração (Tampering) aproxima-se da injeção de prompt (LLM01), que altera a instrução, do envenenamento de dados e modelos (LLM04), das fraquezas de vetores e embeddings (LLM08) e da cadeia de suprimentos (LLM03), pois todos alteram o que o modelo usa para decidir.
- Divulgação de informação (Information Disclosure) corresponde à informação sensível (LLM02) e ao vazamento do prompt do sistema (LLM07); negação de serviço (DoS) encontra o consumo ilimitado (LLM10).
- Elevação de privilégio (Elevation of Privilege) encontra a agência excessiva (LLM06), a injeção que faz o modelo agir em nome de quem não podia (LLM01) e a saída tratada como comando (LLM05).
- Spoofing e Repudiation são transversais: dependem de autenticação forte e de logs confiáveis em todo o sistema. A desinformação (LLM09) fica fora do STRIDE: é um problema de veracidade, não de segurança clássica.

---

## Onde termina a confiança: as fronteiras do sistema
_conteúdo_

<!--
LAYOUT: diagrama de fluxo de dados do Comitê de Bolsas, com linhas pontilhadas marcando as fronteiras: usuário, PDF da proposta, saída de ferramenta e mensagem entre o Agente Leitor e o Agente Pontuador.
ROTEIRO: gancho do slide: o Agente Pontuador recebe texto de "um colega" e por isso confia. Peça à turma para marcar as fronteiras no diagrama e, em cada uma, dizer qual letra do STRIDE pode se materializar.
-->

- Toda entrada que o sistema não controla é fronteira de confiança: o texto do usuário, o documento recuperado pelo RAG, o retorno de uma ferramenta e a mensagem de outro agente.
- O que parece interno merece a mesma desconfiança, porque um documento indexado ou o resumo de um agente colega pode ter nascido de uma fonte hostil.
- Para operacionalizar, desenhe o fluxo de dados, marque cada fronteira e pergunte, em cada uma, qual letra do STRIDE poderia se materializar ali.

---

## Método em ação: o portal de orientação acadêmica
_conteúdo_

<!--
LAYOUT: quatro mini-cartões em sequência, um por passo do método, cada um com uma frase sobre o portal.
ROTEIRO: gancho do slide: um caso novo para exercitar o método, o portal de orientação acadêmica do Campus Aurora, onde um índice único guarda o histórico de disciplinas de todos os alunos de todos os departamentos. Conduza os quatro passos em voz alta e peça que a turma antecipe o achado antes de revelá-lo.
-->

- Ao entender o sistema, o portal de orientação consulta, via RAG, um índice único com o histórico de disciplinas de todos os alunos de todos os departamentos.
- Ao levantar ameaças, o risco mais evidente são as fraquezas de vetores e embeddings (LLM08): a busca não separa por aluno nem por departamento.
- Ao avaliar controles, constata-se que não há filtro de permissão antes da recuperação, um controle ausente, confirmado e não hipotético.
- Ao priorizar, o achado nasce com prioridade alta: o histórico de outra pessoa é dado pessoal e qualquer busca ampla o suficiente o traz à tona.

---

## Inventário de controles: onde a célula está vazia
_conteúdo_

<!--
LAYOUT: tabela com colunas "componente", "risco", "controle", e uma célula de controle vazia destacada em cor de alerta.
ROTEIRO: gancho do slide: percorrer o checklist transforma intuição em evidência. Diga que a célula vazia não é suspeita, é afirmação verificável: ou há o controle ou não há. Conecte com o Laboratório 7, que faz exatamente isso por script.
-->

- Para entrada, prompt do sistema e modelo, pergunte se há separação de papéis e sanitização (LLM01), autenticação e limite de taxa (LLM10), se há segredo no prompt (LLM07) e se a origem do modelo foi verificada (LLM03).
- Para saída, ferramentas e RAG, pergunte se a saída é tratada antes de uso (LLM05), se há menor privilégio e confirmação humana (LLM06) e se o índice isola quem pode ver o quê (LLM08).
- Para monitoramento, verifique se existem registros, detecção de anomalia e red-teaming periódico.
- Cada linha cruza componente, risco e controle; marque cada célula como presente, ausente ou parcial (um controle que existe só em parte, como uma API que autentica mas não autoriza por objeto). Célula vazia ou parcial é um achado, não uma hipótese.

---

## Anatomia de um achado
_conteúdo_

<!--
LAYOUT: cartão de achado com seis campos preenchidos como exemplo; ao lado, matriz 3×3 de impacto por probabilidade com a posição do achado destacada.
ROTEIRO: gancho do slide: um achado bem escrito é aquele que o desenvolvedor executa sem voltar a perguntar. Use o portal de orientação como exemplo e mostre uma recomendação ruim ("melhorar a segurança") ao lado de uma boa ("aplicar filtro de programa antes da busca no índice"). A matriz é a mesma do Laboratório 7: impacto e probabilidade de 1 a 3, multiplicados; 6 ou 9 é Alta, 3 ou 4 é Média, 1 ou 2 é Baixa.
-->

- Todo achado traz seis campos: descrição, componente afetado, categoria do OWASP 2025, cenário de exploração concreto com evidência (a entrada usada, a saída obtida e um print ou trecho de código), severidade e recomendação. Se o problema não é do modelo, a categoria vem de outro documento OWASP, como o API1:2023 do API Security Top 10.
- A severidade vem da matriz 3×3 de impacto por probabilidade: alto com médio ou alto (e médio com alto) é prioridade alta; alto com baixo, baixo com alto e médio com médio ficam em média; o que sobra é baixa, vai para o backlog e tem o risco residual aceito formalmente.
- A recomendação precisa ser específica, ligada ao risco e executável por quem lê, sem exigir que o desenvolvedor volte a perguntar o que fazer.

---

## Do jargão à decisão: relatar o risco à gestão
_conteúdo_

<!--
LAYOUT: duas colunas "sigla técnica" e "consequência para a instituição", e ao lado o esqueleto de um resumo executivo de uma página.
ROTEIRO: gancho do slide: "LLM08 no índice do portal" vira "um aluno pode ver o histórico de outro". Peça à turma para traduzir mais dois achados do Campus Aurora em consequências, sem exagero.
-->

- Quem decide não age sobre siglas: "LLM08 no índice do portal" precisa virar "um aluno pode ver o histórico de outro", com a consequência de privacidade e de reputação que isso carrega.
- O resumo executivo cabe em uma página: a postura geral, os dois ou três riscos mais críticos em linguagem de negócio e as próximas ações recomendadas.
- Descreva o risco com exatidão e sem alarmismo; clareza, priorização e linguagem do negócio é o que faz um achado ser corrigido, e não apenas arquivado.

---

## O método, não a lista
_conclusão_

<!--
LAYOUT: sequência horizontal "entender → modelar → checar → priorizar → comunicar", sob uma faixa com o arco das duas aulas.
ROTEIRO: gancho do slide: o que fica depois de duas aulas. Recapitule o arco: duas raízes, vocabulário do OWASP 2025, arquiteturas, dados e LGPD, camadas de defesa e método. Anuncie que agora vêm os três laboratórios, onde cada ideia vira experimento.
-->

- O que a turma leva é um processo repetível, entender, modelar, checar, priorizar e comunicar, que escala do chat simples ao sistema multi-agente.
- O arco das duas aulas foi das duas raízes ao vocabulário do OWASP 2025, às arquiteturas, aos dados e à LGPD, às camadas de defesa e, por fim, ao método.
- Agora os laboratórios: cada ideia deste bloco vira um experimento que a turma executa, mede e discute.

---

## Laboratório 5 — Dados que cruzam a fronteira
_prática_

<!--
LAYOUT: três cartões verticais: "Objetivo", "Passos", "O que observar", com o comando em destaque no rodapé. Tempo: ~20 min.
ROTEIRO: gancho do slide: o aviso que levou a lista de bolsistas, agora em código. Peça que a turma rode primeiro sem defesa, anote o que saiu e para onde, depois rode com --defesa e compare. Não antecipe o resultado; a graça é a turma descrevê-lo.
-->

- Objetivo: vivenciar dois problemas do Bloco 4, o dado pessoal que sai para uma API externa simulada e a exfiltração por uma ferramenta de envio, e testar minimização, lista de destinos permitidos e filtro de PII na saída. Execução: python3 exemplos_aula_mestrado/aula6/lab5_dados_na_fronteira.py.
- Passos: rode o script sem opções e leia a narração; identifique quais dados pessoais seguiram para fora e por qual caminho; rode de novo com --defesa e compare as duas execuções.
- O que observar: o que mudou no conteúdo enviado ao provedor externo, se o destino de fora do campus continuou possível e se algum dado pessoal ainda escapou mesmo com a defesa ligada.
- Discussão: quais controles atuaram antes do modelo e quais atuaram depois dele, e por que ele precisou ficar de fora da decisão.

---

## Laboratório 6 — Queijo suíço
_prática_

<!--
LAYOUT: três cartões verticais ("Objetivo", "Passos", "O que observar"), com uma matriz ataque por configuração desenhada ao lado como tabela nativa. Tempo: ~20 min.
ROTEIRO: gancho do slide: a metáfora do queijo suíço vira número. Peça que a turma preveja, antes de rodar, quais ataques cada configuração vai conter e depois compare com o resultado. Dê atenção à diferença entre "mais defesa" e "defesa certa".
-->

- Objetivo: medir o que cada camada contém. Uma suíte de ataques roda contra configurações de defesa, nenhuma, só entrada, só saída, só privilégio e todas, e imprime uma matriz ataque por configuração. Execução: python3 exemplos_aula_mestrado/aula6/lab6_queijo_suico.py.
- Passos: antes de rodar, preveja numa folha quais ataques cada configuração conterá; execute o script, e depois rode com --defesa, conforme a orientação impressa, para comparar com a sua previsão.
- O que observar: quais ataques cada camada deixa passar, se alguma configuração isolada contém tudo e o que muda quando as camadas são combinadas.
- Discussão: o que esse experimento diz sobre o investimento em uma única camada e sobre quais furos sobram na combinação.

---

## Laboratório 7 — Avaliação de ponta a ponta
_prática_

<!--
LAYOUT: três cartões verticais ("Objetivo", "Passos", "O que observar"), com um trecho do inventário em destaque como exemplo de entrada. Tempo: ~20 min.
ROTEIRO: gancho do slide: a avaliação do portal, agora automatizada: o script lê o inventário do sistema, aponta células vazias do checklist e redige o resumo executivo. Convide a turma a editar o inventário e ver o relatório mudar.
-->

- Objetivo: aplicar o Bloco 6 sobre um inventário em arquivo, apontando as células vazias do checklist, atribuindo severidade pela matriz e produzindo um resumo executivo em linguagem de negócio. Execução: python3 exemplos_aula_mestrado/aula6/lab7_avaliacao.py, que lê aula6/sistema_exemplo.json.
- Passos: abra o sistema_exemplo.json e leia os componentes e controles declarados; rode o script, depois com --defesa, e leia os achados e o resumo; por fim, edite o inventário e rode de novo.
- O que observar: quais controles ausentes viraram achados, como a severidade acompanha impacto e probabilidade e se o resumo seria compreensível por quem não conhece o vocabulário do OWASP.
- Discussão: o que um script consegue e o que não consegue avaliar, e por que a revisão humana do inventário continua necessária.

---

## Os dois trabalhos: aplicar as Aulas 5 e 6 num sistema de verdade
_conclusão_

<!--
LAYOUT: dois cartões lado a lado, "Trabalho 1 — atacar e documentar (Aula 5)" e "Trabalho 2 — avaliar e propor defesa (Aula 6)", e embaixo uma faixa com o app Campus Aurora e suas seis superfícies.
ROTEIRO: gancho do slide: tudo o que os trabalhos pedem foi visto nas duas aulas; este slide só liga cada trabalho à aula de onde ele vem. Gaste uns 3 minutos aqui, tirados do encerramento. Mostre o app rodando, se der tempo, e reforce que lá o modelo é real: o mesmo ataque pode passar numa tentativa e falhar na outra, então registrar cada tentativa é parte do trabalho.
-->

- O Trabalho 1 aplica a Aula 5: construir um agente com uma função específica e tentar reproduzir contra ele os dez riscos do Top 10 2025, registrando a entrada, a saída e um print de cada tentativa, ou justificando tecnicamente por que um risco não se aplica àquela arquitetura.
- O Trabalho 2 aplica a Aula 6: mapear as fronteiras de confiança, aplicar o STRIDE, preencher o inventário de controles (presente, ausente ou parcial) e redigir ao menos três achados com os seis campos e um guardrail localizado na arquitetura.
- A base dos dois é o app Campus Aurora em trabalho_ollama/: as mesmas seis arquiteturas da Aula 5 (Aurora Assist, Acervo Aurora, Agenda Lab, Comitê de Bolsas, Notebook do grupo e API do Histórico), sem nenhuma defesa, falando com um modelo aberto hospedado localmente no Ollama.
- A diferença para os laboratórios: lá o modelo era o SimLLM, previsível; nos trabalhos ele é real, então o mesmo ataque pode funcionar numa tentativa e falhar na outra (gerar é sortear), e é por isso que cada tentativa precisa ser registrada.

---

## Leitura complementar
_conclusão_

<!--
LAYOUT: lista de referências nativa do Gamma, uma por linha.
ROTEIRO: gancho do slide: onde está a fonte de cada afirmação das duas aulas. Diga que os documentos legais e os produtos mudam, e que o status do PL 2338/2023 e as páginas de guardrails devem ser conferidos na data da leitura.
-->

- OWASP Top 10 for LLM Applications 2025 (genai.owasp.org), o documento de conscientização usado nas duas aulas.
- Greshake et al. (2023), "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"; Wei et al. (NeurIPS 2023), "Jailbroken: How Does LLM Safety Training Fail?".
- Nasr et al. (Google DeepMind, 2023), "Scalable Extraction of Training Data from (Production) Language Models"; Moffatt v. Air Canada (2024); decisão do Garante italiano sobre o ChatGPT (março de 2023).
- LGPD (Lei 13.709/2018), arts. 18 e Capítulo V; PL 2338/2023 (Marco Legal da IA), conferir o status; documentação vigente dos provedores sobre guardrails.

---

## Exercício opcional extraclasse
_conclusão_

<!--
LAYOUT: checklist nativa dos passos do método, um item por linha.
ROTEIRO: gancho do slide: tirar o método da sala. Peça um sistema real que o aluno use ou conheça, diferente de todos os exemplos da aula, e esclareça o formato de entrega esperado.
-->

- Escolha um sistema com LLM que você conheça ou use: um assistente de produtividade, um chatbot de atendimento, um copiloto de código.
- Aplique os quatro passos: mapeie a cadeia e a arquitetura, levante ameaças com o Top 10 2025 e o STRIDE e percorra o checklist por componente.
- Entregue de três a cinco achados completos, com os seis campos, e feche com um resumo executivo de uma página em linguagem de negócio.

---

## Encerramento
_conclusão_

<!--
LAYOUT: slide limpo com uma frase central e o espaço para perguntas.
ROTEIRO: gancho do slide: a mensagem final das duas aulas. Feche dizendo que avaliar com estrutura substitui o medo genérico do LLM por um processo, e abra para perguntas e discussão dos laboratórios (cerca de 15 minutos).
-->

- Quem avalia com método troca o medo genérico do LLM por um processo repetível, em que cada risco tem nome, dono e controle.
- Os laboratórios mostraram que a defesa está em volta do modelo e que nenhuma camada basta sozinha.
- Fica aberto para perguntas, para a discussão dos laboratórios e para dúvidas sobre o exercício.

---

## Material Didático — Uso Restrito
_conclusão_

<!--
LAYOUT: slide final de copyright, com três caixas nativas do Gamma (e-mail, LinkedIn, disciplina).
-->

- Copyright © 2026 — **Prof. Tharles Maicon Freire dos Santos**. Todos os direitos reservados; a reprodução ou divulgação total ou parcial deste material é proibida sem o consentimento formal e por escrito do autor.
- E-mail — tharles.freire@heyupcharly.com.br
- LinkedIn — linkedin.com/in/tharles-freire
- Disciplina — Cyber Security & Governance — Cloud DevOps Security — 2026
