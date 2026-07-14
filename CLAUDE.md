# CLAUDE.md — Sistema Financeiro Pessoal

## Contexto
Sistema financeiro pessoal de um casal (eu e minha esposa).
É um CLONE ADAPTADO do sistema WEN Financeiro (arquivo `referencia-wen.html`
na raiz — LEIA ANTES DE CODAR). Manter a mesma identidade visual, o mesmo
padrão de código e a mesma arquitetura de dados.

## PREMISSAS DA FAMÍLIA (atualizado 13/07/2026)
- Finanças 100% JUNTAS. NÃO existe rateio por pessoa, NÃO existe
  "quem deve pra quem", NÃO existe saldo entre os dois.
- Os logins servem para auditoria (saber quem lançou/alterou o quê) E para
  personalizar a experiência família (nome, foto, saudação).
- Toda visão financeira é consolidada, sem filtro por pessoa.
- EVOLUÇÃO: deixou de ser "só do casal" e virou plataforma da FAMÍLIA
  (casal + filhos), com cadastro aberto de contas, foto de usuário e uma
  camada visual/emocional acolhedora (ver PLANO.md → "Camada Família").
  A premissa antiga de "2 usuários fixos só para auditoria" foi substituída.
- A inteligência financeira (módulos 2-6) permanece intacta; a camada família
  é uma casca por cima. NUNCA usar números financeiros falsos — só dados reais
  ou claramente marcados como demonstração.
- Identidade visual atual: paleta rosa queimado/vinho/creme, cantos
  arredondados, corações como detalhe sutil, temas (Nosso Lar / Escuro).
  (O sistema NÃO usa mais o visual verde/azul do WEN no app.)

## Stack (não mudar sem me perguntar)
- HTML/CSS/JS puro, single-page app, SEM build step, SEM framework
- Firebase Firestore (projeto novo: financeiro-pessoal)
- Firebase Authentication (email/senha)
- Deploy: GitHub Pages
- Gráficos: mesma lib usada no referencia-wen.html

## Regras de arquitetura
- Cache local no navegador + sync incremental (só busca o que mudou desde o
  último load) — obrigatório, pra não estourar cota do Firebase
- Backup/Restore .json por drag-and-drop, separado por módulo
- Código e comentários em PORTUGUÊS
- Nomes de variáveis/funções em português, seguindo o padrão do WEN

## Estrutura Firestore
usuarios/{uid}
lancamentos/{id}                    → contas a receber (simplificado)
meses/{anoMes}                      → contas a pagar (igual WEN)
cartoes/{id}
faturas/{cartaoId_anoMes}/itens/{id}
parcelamentos/{id}
regras_categorizacao/{id}
orcamentos/{anoMes_categoriaId}
fechamentos/{anoMes}
categorias/{id}
logs/{id}

---

## MÓDULO 1 — Auth + Auditoria
- Login bloqueia o app inteiro antes do carregamento
- 2 usuários fixos (email/senha)
- TODO create/update/delete grava em `logs`:
  { usuario, email, acao, colecao, docId, descricaoItem,
    dadosAntes, dadosDepois, timestamp }
- Todo documento carrega: criadoPor, criadoEm, alteradoPor, alteradoEm
- Aba ⚙️ Config → 🗂 Auditoria: lista cronológica, filtro por usuário/período/
  ação, mostrar diff (antes → depois)
- Badge do usuário logado no header + botão sair

## MÓDULO 2 — Contas a Receber (SIMPLIFICADO)
REMOVER do WEN: data de gravação, Studio A/B/Externo, horas, locação, edição,
valor reserva, meta de horas, ranking/top 20 clientes, clientes sumidos,
ticket/h, Google Agenda, aba Fechamento, texto para NF, comparativo por cliente.

Lançamento: descricao* | categoria | valor | vencimento | dataRecebimento |
status (🟡 Previsto / ✅ Recebido / 🔴 Atrasado) | 📌 recorrente | observacao
Categorias: Salário, Freelance, Aluguel, Rendimentos, Reembolso, Outros
Abas: 📊 Dashboard · 📋 Lançamentos · 🏷️ Categorias · 🔄 Recorrentes
Manter do WEN: registrar recebimento (total/parcial), filtros, calendário, Excel

## MÓDULO 3 — Contas a Pagar (PORT DIRETO do WEN + ajustes)
Manter: conta fixa 📌, repetição multi-mês, modal "O que deseja atualizar?"
(só este mês / este + próximos / todos), mesmo modal na exclusão, pagamento
total ou parcial, gerenciar categorias (nome + emoji + cor), "Copiar Mês para
Próximo", calendário do mês, consulta e baixa por período (por dias / data
exata / todos pendentes), filtros (Todos/Pagos/Pendentes/Vencidos/categoria/
faixa de valor), conciliação bancária .ofx com tolerância ±1/±3/±5/±7 dias e
as abas 🔵 Sugestões · 🟡 Ambíguos · 🔴 Sem Correspondência · ✅ Conciliados ·
📋 Sistema sem Transação · 🗑️ Ignorados

Categorias pessoais: 🏠 Moradia · 🍽️ Alimentação · 🚗 Transporte · 🏥 Saúde ·
🎓 Educação · 🎬 Lazer · 📱 Assinaturas · 📋 Impostos · 💳 Cartões ·
👤 Pessoal · 📦 Outros

### NOVO — Contas de VALOR VARIÁVEL (água, luz, gás)
- Flag `valorVariavel: true` no cadastro da conta
- A conta é criada todo mês (como conta fixa), mas com valor ZERADO e status
  "⚠️ Aguardando valor" — não entra no total de "a pagar" enquanto não for
  preenchida
- Opcional: campo `valorEstimado` (média dos últimos 3 meses) só pra projeção
- Alerta no Dashboard: "3 contas variáveis sem valor este mês"
- Ao preencher o valor, vira 🟡 Pendente normal

---

## MÓDULO 4 — Cartão de Crédito (aba 💳 Cartões)

### DUAS VISÕES — não confundir
1. **CAIXA (a fatura)** — é o que sai da conta. O valor da fatura é SEMPRE o
   total importado do .ofx. NUNCA digitado à mão, NUNCA recalculado.
   É esse valor que vira o lançamento em Contas a Pagar.
2. **COMPETÊNCIA (a compra)** — cada item guarda a `dataCompra` real, extraída
   do .ofx. Serve só pra ANÁLISE no Dashboard ("quanto gastei em julho").
   NÃO altera o valor da fatura.

**Regra de ouro:** a data da compra reorganiza a ANÁLISE, nunca o VALOR do
lançamento. Fatura de agosto = soma dos itens do .ofx de agosto, ponto.

### Cadastro de cartões
nome, bandeira, final 4 dígitos, dia de vencimento, limite.
(dia de fechamento é opcional, apenas informativo)

### Importação
- SEMPRE via .ofx. A fatura só é importada QUANDO JÁ ESTÁ FECHADA.
- Valor total da fatura = total do arquivo .ofx. Imutável, não editável.
- Ao importar, informar o mês da FATURA (mês de vencimento/pagamento).
- Cada item grava: fitid | dataCompra (do .ofx) | mesFatura | descricao |
  valor | parcela (x/y) | categoria

**⚠️ IDEMPOTÊNCIA (crítico — bug mais provável do projeto):**
- Usar o `FITID` do .ofx como ID único do item no Firestore
- Reimportar o mesmo arquivo NÃO pode duplicar nada
- Se a fatura do mês já existe: perguntar "Substituir importação anterior?" e
  mostrar quantos itens são novos / duplicados / removidos
- Nunca fazer append cego

**⚠️ ESTORNOS E CRÉDITOS:**
- .ofx traz valores NEGATIVOS (devolução, cashback, anuidade estornada,
  pagamento de fatura anterior)
- Tratar corretamente no parser — o total DEVE bater exatamente com o total
  do arquivo
- Itens negativos entram na categoria "💚 Estornos/Créditos"
- Validação obrigatória após importar: soma dos itens === total do .ofx.
  Se divergir, ABORTAR e avisar.

### MOTOR DE CATEGORIZAÇÃO AUTOMÁTICA (parte mais importante)
- `regras_categorizacao`: { descricaoNormalizada, categoria, ocorrencias,
  ultimoUso }
- Normalização: minúsculas, sem acento, remove números, remove sufixo de
  parcela ("*PARC 03/10", "3/12"), remove códigos de estabelecimento
- Ao importar: varre o histórico de faturas anteriores e aplica a categoria já
  usada. Match exato = confiança alta. Similaridade (Levenshtein/includes
  normalizado) = confiança média, marca pra revisão.
- Sem match → 🔴 Não categorizado
- Ao categorizar manualmente, GRAVA A REGRA → aprende pro mês seguinte
- Permitir cadastrar regras manualmente na mão (pré-carregar o motor antes da
  primeira importação)
- Tela de conciliação (mesmo visual da conciliação bancária):
  ✅ Categorizado · 🟡 Sugestão (revisar) · 🔴 Não categorizado
  Colunas: Descrição | Data compra | Valor | Categoria sugerida | Confiança | Ação
  Botão "✅ Aceitar todas as sugestões" + ajuste individual
- SEM campo responsável, SEM rateio por pessoa. O rateio é POR CATEGORIA.

### RATEIO POR CATEGORIA
Distribuição do valor da fatura entre as categorias.
Soma dos itens por categoria = valor total da fatura (SEMPRE bate).
Item sem categoria → entra como 📦 Outros. O total NUNCA pode divergir do .ofx.

### PARCELAMENTOS FUTUROS
- Parser identifica a parcela: "03/10", "*PARC 03/10", "PARC 3 DE 12", etc.
- Ao importar, PROJETA as parcelas restantes nos meses seguintes:
  `parcelamentos/{id}`: { descricao, descricaoNormalizada, categoria, cartaoId,
    valorParcela, parcelaAtual, totalParcelas, mesInicio, mesFim, ativo }
- Parcelas futuras aparecem como PREVISTAS (não confirmadas) até a fatura
  daquele mês ser importada de fato
- Ao importar a fatura do mês seguinte, RECONCILIA: item que bate com uma
  parcela projetada → confirma, NÃO duplica
- Todas as parcelas confirmadas → ativo = false

### Fechamento da fatura
Gera automaticamente 1 lançamento em Contas a Pagar com o valor total do .ofx,
categoria 💳 Cartões, vencimento = dia de vencimento do cartão, com link pro
detalhamento. Esse valor é IMUTÁVEL e não editável manualmente.

---

## MÓDULO 5 — Orçamento por Categoria (aba 🎯 Orçamento)
- `orcamentos/{anoMes_categoriaId}`: { categoriaId, anoMes, valorTeto }
- Cadastro: lista todas as categorias de despesa, digito o teto mensal de cada
  uma. Botão "copiar orçamento do mês anterior".
- Visualização principal — BARRA DE PROGRESSO por categoria:
  Alimentação   R$ 1.240 / R$ 1.500   [████████░░] 83%
- Cores da barra:
  🟢 verde   até 79%
  🟡 amarelo 80–99%
  🔴 vermelho ≥ 100% (estourou — mostrar quanto passou)
- Gasto considerado = Contas a Pagar do mês + itens da fatura de cartão do mês,
  agrupados por categoria (usar a mesma regra anti-duplicação do Rateio Geral)
- Card resumo no topo: Total orçado · Total gasto · Saldo · % consumido
- Categoria sem orçamento definido → não mostra barra, mostra só o gasto

---

## MÓDULO 6 — Dashboard consolidado (por último — depende de todos)

### Seletor de visão (no topo do Dashboard)
Toggle global: **💰 Caixa** (padrão) · **📅 Competência**
- Caixa: gasto = quando a fatura foi paga
- Competência: gasto = quando a compra foi feita (usa dataCompra dos itens)
Afeta os gráficos de gasto por categoria e a evolução mensal.
NÃO afeta o valor da fatura nem o saldo bancário.

### Cards principais
- Saldo do mês (recebido − pago)
- Previsto x Realizado
- Total em atraso (destaque visual)
- ⚠️ Contas variáveis sem valor preenchido
- Próximos vencimentos (7 e 30 dias)
- Evolução 12 meses
- Calendário unificado (▉ receitas / ▉ despesas)

### Card "💳 Parcelado — Próximo Mês" (destaque, fonte grande)
Valor total das parcelas que caem no próximo mês.
Logo abaixo, em fonte MENOR, lista dos meses seguintes:
  Ago/26 ....... R$ 1.240,00
  Set/26 ....... R$   980,00
  Out/26 ....... R$   980,00
  Nov/26 ....... R$   410,00
Clicar no card abre detalhamento: quais compras compõem cada mês
(descrição, cartão, parcela x/y, valor).

### Card "📅 Gasto por Mês de Compra" (visão competência)
Quanto foi comprado em cada mês, independente de qual fatura caiu.
  Jul/26 ....... R$ 3.480,00
  Jun/26 ....... R$ 2.910,00
  Mai/26 ....... R$ 4.120,00

### RATEIO — duas visões
1. **Rateio do Cartão** (por cartão / por fatura)
   Pizza + tabela: distribuição do valor da fatura entre as categorias.
   Filtro por cartão e por mês. Total sempre = valor do .ofx.
2. **Rateio Geral** (todas as contas do mês)
   Pizza + tabela: Contas a Pagar + itens da fatura de cartão, por categoria.
   ⚠️ ANTI-DUPLICAÇÃO: o lançamento "💳 Cartões" em Contas a Pagar é apenas o
   espelho de caixa. Na visão de rateio geral ele é SUBSTITUÍDO pelos itens
   detalhados da fatura. Nunca somar os dois.

### Mini-widget de orçamento
As 3 categorias mais próximas de estourar (ou já estouradas), com barra.

### SNAPSHOT MENSAL (performance)
- Ao fechar o mês, gravar `fechamentos/{anoMes}` com os totais consolidados:
  { totalReceita, totalDespesa, saldo, gastoPorCategoria, totalCartao,
    totalParcelado, fechadoEm, fechadoPor }
- O histórico de 12 meses lê o SNAPSHOT, não recalcula tudo do zero.
  Economiza cota do Firebase e o histórico não muda retroativamente.
- Botão "🔄 Recalcular mês" para forçar atualização de um snapshot antigo.

---

## Como trabalhar comigo
- Sempre atualizar o checklist do PLANO.md ao concluir uma etapa
- Não pular pro próximo módulo sem eu validar o anterior
- Nunca reescrever o CSS base do WEN sem me avisar
- Entregar na ordem: 1 → 2 → 3 → 4 → 5 → 6
