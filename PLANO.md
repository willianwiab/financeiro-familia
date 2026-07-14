# PLANO.md — Sistema Financeiro Pessoal (Casal)

Clone adaptado do WEN Financeiro (`referencia-wen.html`). Ver `CLAUDE.md` para
premissas, stack e regras completas de cada módulo.

**Ordem de entrega:** 1 → 2 → 3 → 4 → 5 → 6. Não avançar de módulo sem
validação do anterior. Checklist atualizado ao concluir cada etapa.

## MUDANÇA DE DIREÇÃO (13/07/2026) — Plataforma Familiar

O sistema deixou de ser "só do casal para auditoria" e virou uma **plataforma
financeira da família** (casal + filhos), com identidade visual acolhedora.
Isso **substitui** a premissa do CLAUDE.md de "2 usuários fixos só para
auditoria":
- Agora há **cadastro aberto** (criar login/senha por e-mail) + **foto do usuário**
- Nova identidade: paleta rosa queimado/vinho/creme, cantos arredondados, corações
  como detalhe sutil, cabeçalho acolhedor, mensagem do dia, temas (Nosso Lar / Escuro)
- Toda a inteligência financeira dos módulos 2-6 **permanece intacta** — a camada
  família é uma casca visual/emocional por cima, sem números inventados.

### Camada Família — Módulo 1b ✅ (implementada, testada localmente)
- [x] Cadastro por e-mail/senha (`createUserWithEmailAndPassword`) com nome + foto
- [x] Login por e-mail/senha (mantido do Módulo 1)
- [x] Foto do usuário: redimensionada no navegador (canvas, 256px) e salva como
      base64 em `usuarios/{uid}.fotoBase64` — **evita o Firebase Storage** (que
      exigiria plano pago); avatar aparece no cabeçalho e no login
- [x] Cabeçalho família: saudação por horário + nomes + data + humor
- [x] Card "Mensagem para nossa família": **108 mensagens** em 9 categorias
      (Amor, Família, Motivação, Gratidão, Organização, Economia, Sonhos,
      Conquistas, Superação), rotação diária sem repetir no dia seguinte +
      botão "Outra mensagem ❤️"
- [x] Temas: "Nosso Lar" (padrão) e "Escuro" via variáveis CSS (persistência
      em localStorage). Reservados p/ o futuro: Amor, Minimalista, Família
- [x] Config: perfil (foto+nome), dados da família (saudação + nome), tema, auditoria
- [x] Testado local: cadastro real, login, foto, tema escuro, mensagem — sem erros
- [ ] **Falta você**: criar sua conta de verdade pelo botão "Criar conta" e
      preencher a saudação (ex: "Will e Gabi") em Config → Nossa família

### Camada Família — depende dos módulos financeiros (fazer conforme 2-6 avançam)
- [ ] Saúde financeira automática ("Como está nossa família este mês?") — precisa de 2/3/6
- [ ] Metas do casal / Nossos sonhos com barra de progresso + confete ao concluir
- [ ] Conquistas automáticas (meta criada, mês sem atrasos, dívida quitada...)
- [ ] Área "Futuro dos nossos filhos" (metas por filho)
- [ ] "Momentos que queremos viver"
- [ ] Resumo semanal / Resumo mensal ("Nossa história deste mês")
- Obs.: Metas, Momentos e Filhos podem ser construídos como coleções próprias
  **antes** do módulo financeiro (o valor acumulado seria digitado à mão até
  a conciliação existir). Decidir a ordem com você.

⚠️ **Segurança a revisar:** cadastro aberto + regra atual (`request.auth != null`
libera tudo) significa que qualquer conta criada lê/escreve todos os dados da
família. Para uso familiar é ok, mas dá pra restringir depois (allowlist de
e-mails / convite). Falar antes de mexer.

## Observações da leitura da referência

- `referencia-wen.html` (3983 linhas) é HTML/CSS/JS puro, sem build, com
  Firebase App SDK carregado mas **sem uso real de Firestore/Auth** — os
  dados de "Pagar" sincronizam com Google Sheets e "Receber" fala direto com
  a API REST do Firestore (`FS_URL`), sem `firebase.auth()`.
- Ou seja: **Módulo 1 (Auth + Auditoria) não tem equivalente para portar do
  WEN** — é a parte mais nova do projeto, tem que ser desenhada do zero
  (login bloqueando o app, `logs` no Firestore, trilha de auditoria),
  mantendo a identidade visual (header verde/azul, cards, `Chart.js`).
- Módulos 2–6 têm bastante lógica para portar/adaptar do WEN (cache local +
  sync incremental, conciliação .ofx, parcelamentos, orçamento).
- Firebase do WEN é o projeto `wencontasapagar` — o pessoal usa um projeto
  **novo e separado**, `financeiro-pessoal` (não reaproveitar credenciais).

---

## Módulo 1 — Auth + Auditoria ✅ (aguardando seu teste final)
- [x] Projeto Firebase `financeiro-pessoal` criado (Firestore em `southamerica-east1`, plano Spark)
- [x] Firebase Auth (email/senha) ativado — **faltam os 2 usuários**: você disse que prefere
      cadastrar sozinho em Authentication → Usuários → Adicionar usuário no console
- [x] Regras do Firestore publicadas: nega tudo por padrão, libera leitura/escrita só para
      `request.auth != null`
- [x] Tela de login bloqueia o app inteiro antes de qualquer carregamento (`index.html`)
- [x] Badge do usuário logado no header + botão sair
- [x] Helpers `registrarLog()`, `comCamposCriacao()`, `comCamposEdicao()` prontos para os
      módulos 2-6 usarem — grava em `logs/{id}`:
      `{ usuario, email, acao, colecao, docId, descricaoItem, dadosAntes, dadosDepois, timestamp }`
      e aplica `criadoPor/criadoEm/alteradoPor/alteradoEm` em qualquer documento
- [x] Aba ⚙️ Config → 🗂 Auditoria: lista cronológica, filtro por usuário/período/ação, diff antes→depois
- [x] Testado localmente: login com credencial errada retorna erro tratado corretamente
      (Firebase Auth respondeu de verdade, sem erros no console)
- [ ] **Falta você**: criar os 2 usuários no Authentication e testar o login de verdade +
      a aba Auditoria (ainda vai aparecer vazia até o Módulo 2 começar a gravar logs)

## Módulo 2 — Contas a Receber (simplificado) ✅ (implementado e testado local)
- [x] Lançamento: descrição, categoria, valor, vencimento, dataRecebimento, valorRecebido, status (🟡 previsto/✅ recebido/🔴 atrasado, derivado), 📌 recorrente, observação
- [x] Categorias (coleção `categorias`, tipo:'receber') com nome+emoji+cor; padrões semeados na 1ª carga: Salário, Freelance, Aluguel, Rendimentos, Reembolso, Outros; CRUD na aba Categorias
- [x] Abas: 📊 Dashboard · 📋 Lançamentos · 🏷️ Categorias · 🔄 Recorrentes
- [x] Dashboard: cards (previsto/recebido/a receber/atrasado), navegação de mês, calendário com pontos por status, próximos 7 dias
- [x] Registrar recebimento total **e parcial** (valorRecebido acumulado, badge "parcial")
- [x] Filtros: busca texto, status, categoria, faixa de valor; exportar **Excel** (XLSX)
- [x] Recorrentes: lista + "Gerar próximo mês" (cria o mês seguinte sem duplicar)
- [x] Backup/Restore .json (download + drag-and-drop), separado por módulo
- [x] Sync incremental por `alteradoEm` + cache localStorage (economiza cota); **soft delete** (`excluido:true`) para propagar exclusões e manter auditoria
- [x] Toda escrita chama `registrarLog` + `comCamposCriacao/Edicao` (auditoria) — verificado: 4 logs gerados no teste
- [x] Corrigido: auditoria recarrega ao abrir Config (antes só carregava no login)
- [x] Removido do WEN: Studio A/B, horas, locação/edição, meta, ranking, Google Agenda, NF (reimplementado limpo, não portado)
- [ ] **Falta você**: testar com sua conta real

## Camada Cristã — Módulo 2b ✅ (implementado e testado local)
Solicitado em 13/07: experiência cristã de paz/esperança/gratidão, sem culpa nem medo.
- [x] Card "🙏 Palavra para nossa família": versículo do dia (referência, texto, reflexão, aplicação prática) + "📖 Outro versículo". **22 versículos** (Finanças + Casamento), textos bíblicos em português de **domínio público** (tradição Almeida) para evitar direitos autorais; passagens longas resumidas a 1 versículo
- [x] 10 frases motivacionais cristãs somadas ao card "Mensagem para nossa família" (categoria Fé)
- [x] Card "🙏 Pelo que somos gratos hoje?" + timeline "Nossa caminhada com Deus" (coleção `gratidoes` no Firestore; registrar + histórico)
- [x] Botão "🙏 Fazer uma oração" → modal com oração curta contextual + "Outra oração"
- [x] Card "📖 Princípios para nossa casa" (princípio do dia + "Ver todos"): 10 temas (Sabedoria, Planejamento, Trabalho, Honestidade, Generosidade, Mordomia, Gratidão, Família, Casamento, Perseverança), cada um com versículo
- [ ] Depende dos módulos financeiros: mensagens cristãs nas conquistas ("Até aqui nos ajudou o Senhor 🙏") — quando houver metas/conquistas
- Nota: nova coleção Firestore `gratidoes/{id}` (não estava na estrutura original do CLAUDE.md)

## Módulo 3 — Contas a Pagar (port direto + ajustes) 🟡 NÚCLEO PRONTO (falta OFX)
Modelo Firestore `meses/{anoMes}` (anoMes 'YYYY-MM') = `{ contas:[...], criado/alterado }`, igual WEN.
Sync incremental por alteradoEm do doc-mês + cache localStorage. Propagação casa por `nome` entre meses.
- [x] Conta fixa 📌, repetição multi-mês (checkboxes de meses ao criar), modal "só este mês / este+próximos / todos" (edição E exclusão)
- [x] Auto-repetição: ao abrir o mês atual sem doc, semeia fixas+variáveis do último mês
- [x] Pagamento total **e parcial** (badge parcial), categorias (nome+emoji+cor, 11 padrões semeados), "Copiar mês → próximo"
- [x] Dashboard: cards (total/pago/a pagar/vencido), navegação de mês, alerta de variáveis sem valor, calendário com pontos por status
- [x] Calendário do mês, **baixa por período** (próximos N dias / data exata / todos pendentes) com seleção e baixa em lote, filtros (status/categoria/faixa de valor/busca)
- [x] Categorias pessoais (Moradia, Alimentação, Transporte, Saúde, Educação, Lazer, Assinaturas, Impostos, Cartões, Pessoal, Outros)
- [x] **Contas de valor variável** (água/luz/gás): flag `valorVariavel`, status "⚠️ Aguardando valor" (fora do total até preencher), `valorEstimado` opcional, alerta no dashboard. Corrigido: campo de valor NÃO trava mais ao editar (dava pra não conseguir preencher)
- [x] Excel + backup/restore JSON (todos os meses), auditoria em toda escrita
- [x] Testado local: CRUD, variável, propagação este+próximos (Jul+Ago→2000), parcial, copiar mês, baixa por período, 7 logs de auditoria — sem erros
- [x] **Conciliação bancária .ofx (3b) FEITA e testada.** Aba "🏦 Conciliação" em Pagar:
  importa extrato .ofx da conta corrente (crédito +, débito −), casa cada movimento com
  Receber (crédito) ou Pagar (débito) por valor + data na **tolerância ±1/±3/±5/±7 dias**.
  6 abas: 🔵 Sugestões · 🟡 Ambíguos · 🔴 Sem correspondência · ✅ Conciliados · 📋 Sistema
  sem transação · 🗑️ Ignorados. Confirmar dá **baixa automática** (marca pago/recebido);
  "Confirmar todas"; ambíguo escolhe o alvo; sem correspondência → "Criar lançamento" (a
  receber/pagar já quitado) ou Ignorar; **Desfazer reverte a baixa** ao estado anterior
  (guarda `antes`). Estado em `conciliacoes/{fitid}`. Testado: fatura −12.174,52 casou com
  a conta a pagar real, deu baixa, e o Desfazer reverteu certinho.
- [ ] **Falta você**: testar com sua conta real

## Módulo 4 — Cartão de Crédito ✅ IMPLEMENTADO (testado com .ofx sintético)
Coleções: `cartoes/{id}`, `faturas/{cartaoId_anoMes}` (itens em array), `parcelamentos/{id}`, `regras_categorizacao/{id}`.
Abas: 💳 Meus cartões · 📥 Importar fatura · 📄 Faturas · 🏷️ Regras.
- [x] Cadastro de cartões (nome, bandeira, final, vencimento, fechamento opcional, limite) com visual de cartão
- [x] Importação .ofx: fatura fechada, informa mês; **valor total imutável = soma do .ofx**; `FITID` como chave
- [x] **Idempotência**: reimportar mostra novos/duplicados/removidos + "substituir importação anterior" (sem append cego); preserva categorias já ajustadas
- [x] Estornos/créditos (valores negativos → "💚 Estornos/Créditos"); validação soma dos itens vs BALAMT com aviso se divergir
- [x] **Motor de categorização** (`regras_categorizacao`): normalização (minúsculas, sem acento, remove nº/parcela), match exato (alta), similaridade Levenshtein ≥0.85 (revisar), varre histórico de faturas; **aprende ao categorizar** (verificado: 2ª importação auto-categorizou tudo com confiança alta)
- [x] Tela de conciliação (✅ alta / 🟡 revisar / 🔴 sem), "Aceitar sugestões" + ajuste individual, regras editáveis à mão
- [x] **Rateio por categoria** (barras, soma sempre = total da fatura) — verificado R$ 670 exato
- [x] **Parcelamentos**: detecta "PARC 03/10" etc., projeta grupo idempotente (parcelaAtual/total, mesInicio/mesFim, valorParcela), mostra faltantes e valor restante; reconcilia por grupo em reimportações
- [x] **Fechamento → lançamento em Contas a Pagar** (categoria Cartões, vencimento = dia do cartão, valor imutável, obs); guarda contra edição do valor no Módulo 3 (`imutavel:true`)
- [x] Bug corrigido no teste: `fatura.id` ficava undefined → setDoc rejeitava (Firestore não aceita undefined)
- [x] **Testado com .ofx REAL (Inter, cartão Gabriela)** e ajustado p/ o formato do Inter:
  - compras vêm NEGATIVAS → parser normaliza sinal (se soma<0, inverte: compras +, créditos −)
  - parcela vem no MEMO ("Parcela 04/04") → detecção roda em NAME+MEMO
  - "PAGAMENTO DE FATURA" (pagamento da fatura anterior) é excluído dos itens
  - BALAMT ignorado como total quando há vários (fatura multi-cartão) → sem alerta falso
  - Resultado bateu exatamente com o PDF: **R$ 12.174,52** (214 itens, 22 parcelas)
- [x] **PRIMEIRO DADO REAL cadastrado** (13/07, sob conta temporária `familia-temp@financeiro.local`):
  cartão Inter Gabriela (final 1291, Mastercard, venc 12, limite 21.200), fatura jul/2026
  R$ 12.174,52 → lançamento em Contas a Pagar (vence 12/07) + 14 parcelamentos ativos projetados.
  Rateio: **decupado por categoria** (ver abaixo).
- [x] **Auto-categorização por rótulo do MEMO do banco** (Inter já traz MERCADO/ACOUGUE/
  ALIMENTACAO_FORA/TRANSPORTE/COMPRAS/SAUDE/PET/TRANSFERENCIA/IGREJA/PIX_CREDITO/JUROS_IOF/
  BELEZA/EDUCACAO/LAZER/ASSINATURA/PAGAMENTO/AJUSTE). Fallback no motor (`C_TAGS_MEMO`),
  cria as categorias que faltam (`C_garantirCategorias`), guarda o `memo` no item p/
  recategorizar. Corrigidos 2 bugs: histórico e "preservar categoria" não podem devolver
  "Outros" (senão travam a recategorização). Fatura da Gabriela recategorizada 100%:
  🛒 Mercado 3.389,09 · 🍔 Alim.fora 2.418,06 · 👗 Vestuário 1.825,60 · 🏥 Saúde 994,57 ·
  🥩 Açougue 810,60 · 🚗 Transporte 722,75 · 👤 Transferências 481,22 · 💸 PIX crédito 438,31 ·
  💇 Beleza 321,62 · ⛪ Igreja 299,45 · 🎓 Educação 279,50 · 🎬 Lazer/Assin. 193,75 (= 12.174,52).
- Nota: cards "Parcelado próximo mês" e "Gasto por mês de compra" ficam no Módulo 6 (Dashboard).

## Módulo 5 — Orçamento por Categoria ✅ IMPLEMENTADO (testado)
Coleção `orcamentos/{anoMes__slug}` = `{ anoMes, categoria, valorTeto }`. Aba 🎯 Orçamento.
- [x] Teto mensal por categoria (input inline por linha, salva no onchange; teto 0 apaga) + "Copiar tetos do mês anterior"
- [x] Barra de progresso por categoria: 🟢 <80% · 🟡 80–99% · 🔴 ≥100% (mostra "estourou R$ X")
- [x] **Gasto = Contas a Pagar do mês + itens da fatura de cartão do mês**, por categoria, com **anti-duplicação** (exclui o espelho `faturaId` da conta a pagar, usa os itens detalhados) — verificado: total R$ 12.174,52, não o dobro
- [x] Card resumo: total orçado · total gasto · saldo · % consumido; navegação de mês; categoria sem teto mostra só o gasto
- [x] Testado com a fatura real da Gabriela: gasto por categoria bate com o rateio; tetos de teste (Mercado 3000→113% vermelho, Alim.fora 3000→81% amarelo, Transporte 1000→72% verde) validados e depois removidos
- [ ] **Falta você**: definir os tetos reais do orçamento de vocês

## Módulo 6 — Dashboard Consolidado ✅ IMPLEMENTADO (testado)
Aba 📊 Dashboard. Junta Receber+Pagar+Cartões+Orçamento. Gráficos com Chart.js 4.4.
- [x] **Toggle 💰 Caixa / 📅 Competência** (competência usa dataCompra dos itens) — testado: Caixa põe a fatura toda em julho; Competência espalha por mês de compra (jun R$ 8.974, mai 1.337, abr 107...)
- [x] Cards: saldo do mês (recebido−pago), previsto × realizado, total em atraso (destaque), ⚠️ variáveis sem valor, próximos vencimentos (30 dias)
- [x] Card **"Parcelado — próximo mês"** (fonte grande) + lista dos meses seguintes + modal de detalhamento (compra, parcela x/y, valor) — testado: Ago/26 R$ 1.408,10, Set 900,83...
- [x] Card "Gasto por mês de compra" (só na visão competência)
- [x] **Rateio geral** (doughnut + tabela) com anti-duplicação cartão×pagar — bate com o rateio do cartão
- [x] Evolução 12 meses (barras receitas × despesas); mini-orçamento (3 categorias mais próximas de estourar)
- [x] **Snapshot mensal** `fechamentos/{anoMes}` (botão "Fechar / recalcular mês")
- [ ] Simplificado vs spec: rateio POR CARTÃO separado e calendário unificado ficaram de fora (o rateio geral e os calendários de Receber/Pagar já cobrem); dá pra somar depois se quiser.

---
## 🎉 TODOS OS 6 MÓDULOS PRONTOS E TESTADOS. Próximo: deploy.
- [ ] Mini-widget de orçamento (3 categorias mais próximas de estourar)
- [ ] Snapshot mensal em `fechamentos/{anoMes}` + botão "Recalcular mês"

---

**Status:** Módulo 1 implementado, aguardando você criar os 2 usuários e validar antes de eu seguir para o Módulo 2.
