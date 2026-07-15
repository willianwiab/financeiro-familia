# PROJECT_STATUS.md — Boa Semente

_Snapshot do estado atual do projeto (para uma nova sessão continuar exatamente daqui)._
_Última atualização: 14/07/2026._

---

## 1. Objetivo geral do sistema
App financeiro **de casal/família** que junta **Fé · Família · Finanças** (marca
"Boa Semente"). Vai além de lançar/consultar valores: além da gestão financeira
completa (receber, pagar, cartões, orçamento, dashboard), tem uma camada de
**interação leve do casal** ("Nosso Espaço") e uma **camada cristã/acolhedora**.
Finanças são 100% consolidadas (sem rateio por pessoa). A ideia é distribuir para
vários casais — cada família tem sua própria instância isolada.

## 2. Estrutura e arquitetura atual
- **Single-file** `index.html` (~6000 linhas, ~680 KB) — HTML + CSS + JS puro, sem
  build/framework. Toda a lógica em `<script type="module">` no fim do arquivo.
- **Firebase** (Web SDK 12.x via CDN): Auth (email/senha) + Firestore. Config inline.
- Sem backend próprio. Sem Firebase Storage (fotos = base64 em `usuarios`).
- Módulos por prefixo de função: `R_` Receber · `P_` Pagar · `C_` Cartões ·
  `B_` Conciliação bancária · `O_` Orçamento · `D_` Dashboard · `N_` Novidades ·
  `CASAL_` Nosso Espaço. Auth/sessão/tema/mensagens no topo do script.
- Cache local (localStorage) + sync incremental por `alteradoEm`.
- **Duas instâncias** (bancos e deploys separados):
  - **Família:** Firebase `financeiro-pessoal-bda5d`, Vercel `financeiro-familia`
    (https://financeiro-familia-ten.vercel.app), GitHub `willianwiab/financeiro-familia`
    (Pages: willianwiab.github.io/financeiro-familia). Fonte = `index.html` da raiz.
  - **Manfrin (cobaia da irmã):** Firebase `financeiro-manfrin`, Vercel
    `financeiro-manfrin` (https://financeiro-manfrin.vercel.app), GitHub
    `willianwiab/financeiro-manfrin`. Gerada por `gerar-manfrin.py` (troca só o config).

## 3. Funcionalidades já concluídas
**Financeiro (núcleo):**
- Auth + Auditoria (logs de toda escrita, aba 📜 Histórico com diff).
- Receber (M2): lançamentos, recebimento total/parcial, categorias, recorrentes, Excel.
- Pagar (M3): modelo `meses/{anoMes}`, conta fixa 📌, valor variável 💧, propagação
  este/próximos/todos, copiar mês, baixa total/parcial e por período, categorias.
- Conciliação bancária OFX (M3b, `B_*`): casa extrato com Receber/Pagar por valor+data.
- Cartões (M4): importação `.ofx`, categorização automática (regras + Levenshtein),
  rateio por categoria, parcelamentos, fechamento → conta imutável em Pagar.
- Orçamento (M5): tetos por categoria + **Adicionar teto** (cria categorias novas),
  barras 🟢🟡🔴, copiar do mês anterior.
- Dashboard (M6): toggle Caixa/Competência, cards, gráficos (Chart.js), parcelado,
  fechamento mensal.
- **Barra de quitação do mês** no Painel (Previsto × Realizado + % + "falta para quitar").
- **Fatura PRÉVIA das parcelas:** cada mês futuro com parcelas vira conta real em Pagar
  (idempotente por `faturaId`, substituída ao importar o `.ofx` real).
- Aba **Faturas — layout mestre-detalhe** (repaginada): lista das faturas à esquerda
  (importadas + prévias) e **painel de detalhe** à direita; no celular empilha com
  auto-scroll até o detalhe. Detalhe traz **gráfico de pizza (donut) por fatura** com o
  total no centro, **chips por categoria** (valor + %) **clicáveis para filtrar/somar**
  (chip ou fatia da pizza → filtra os itens + mostra subtotal; "Todas" limpa) e a lista de
  itens; vale para **importada e prévia**. Parcelamentos em aberto no detalhe da importada.
  Datas no formato **AGO26**. (Substituiu os antigos cards separados de rateio/parcelas.)
- **Refino de categoria por item** (na tela de detalhe): cada item da fatura importada tem
  um ✎ na categoria → modal com as categorias; ao trocar, re-salva a fatura (total intacto),
  pizza/rateio recalculam ao vivo, registra no Histórico, opção "aplicar às próximas faturas"
  (aprende regra) marcada por padrão, e sincroniza o parcelamento se for parcela. ⚠️ Grava no
  Firestore ao usar — testado só no harness (stub); **Will deve fazer backup antes** de usar na fatura real.
- **Pizza inclui parcelas projetadas** por categoria (meses futuros).
- **Importar extrato** também pelo cabeçalho.
- **Backup & Restauração** reunido só na aba ⚙️ Config.
- **"Esqueci minha senha"** no login (Firebase `sendPasswordResetEmail`, sem backend).
- Aba **✨ Novidades** (changelog) + **💡 Sugerir melhoria** (abre e-mail p/
  wenprodutora@gmail.com via mailto + salva em `sugestoes`).

**Marca / visual:**
- Rebrand **"Boa Semente"**: tema padrão verde escuro/verde claro/bege; nome no
  `<title>` e login; **logo PNG** (serif) embutida no login e no cabeçalho (selo branco).
- Temas: 🌱 Boa Semente (padrão), 🌙 Escuro, 🎀 Hello Kitty (fundo com banner + carinha
  como ícone). Seletor de tema no cabeçalho (🎨) e na Config.
- Painel "clean": mensagem da família virou texto pequeno no cabeçalho (adaptado ao
  tema); ícone 💌 ao lado do sininho abre "escrever pro meu amor".
- Seletor de mês **fixo no topo** da aba Pagar (vale p/ Contas e Baixa por período).

**Camada Cristã:** versículos, gratidão (`gratidoes` + timeline), oração, princípios,
frases cristãs (aba 🏆 Metas & Conquistas, ex-"Início").

**Nosso Espaço ❤️ (camada casal) — COMPLETO (10 etapas):**
1. Fundação: sininho 🔔 (badge de novidades), aba dedicada, "parceiro" = outro usuário.
2. Mensagens de amor (`casal_mensagens`): fundos, tipo, agendamento, reações ❤️🙏😊, respostas.
3. Recados financeiros (`casal_recados`): tipo + status pendente/visto/resolvido.
4. Humor do dia (`casal_humor`): 7 humores, motivo se "preocupado", enviar carinho.
5. Vamos conversar? ☕ (`casal_convites`): assunto + quando + respostas.
6. Desafios em equipe 🎯 (`casal_desafios`): colaborativos, progresso, concluir juntos.
7. Sequência 🔥 (streak): dias com ação financeira (recomeço sem culpa).
8. Medalhas 🏅 (`casal_medalhas`): 12 conquistas por critérios reais + animação.
9. Usuariômetro 👀 + Sintonia do casal ❤️ (score de colaboração + detalhes + modelo).
10. Notificações discretas (config por tipo em `casal_config`).
- Sininho agrega mensagens + recados + convites recebidos pendentes.

## 4. Funcionalidades em desenvolvimento
- Nenhuma em andamento no momento. Últimos itens fechados: fatura prévia, faturas
  previstas expansíveis, pizza com parcelas projetadas, formato de data AGO26.

## 5. Decisões importantes tomadas (nesta sessão)
- **Rebrand "Boa Semente"** (tema verde/bege padrão + logo). Tirou o viés pessoal
  ("Nossa Família") porque vai ser compartilhado com outros casais.
- **Fatura prévia = conta REAL** (não "previsão informativa"): decisão explícita do
  Will. Idempotência por `faturaId` (mesmo id da fatura real → substituição automática).
- **Modelo compartilhado mantido** (casal vê tudo). NÃO implementar matriz de
  permissões granular por enquanto (seria mudança grande de segurança).
- **"Esqueci senha" via Firebase nativo**, não Resend (chave ficaria exposta no app estático).
- **App desktop / localStorage: PAUSADO** — perderia o compartilhamento do casal e o
  Nosso Espaço (cada aparelho ficaria isolado). Se um dia for feito, é reescrita da
  camada de dados; melhor caminho = PWA mantendo o Firebase.
- **De-personalizar URL/GitHub: PAUSADO** — `willianwiab.github.io` tem o username;
  removê-lo de vez exige organização GitHub (criação de conta = o Will faz). Os links
  da Vercel já não têm o nome dele. Mantido como está.

## 6. Regras de negócio
- Finanças 100% juntas; rateio é **por categoria**, nunca por pessoa.
- Cartão: fatura = total do `.ofx`, imutável; duas visões (Caixa/Competência); a data
  da compra reorganiza a análise, nunca o valor.
- **Idempotência do `.ofx` por FITID**; reimportar substitui, não duplica; checkbox
  obrigatório quando há parcelas.
- **Anti-duplicação no pizza/rateio:** o espelho "💳 Cartões" (`faturaId`) é excluído;
  entram os itens da fatura por categoria. Fatura prévia também tem `faturaId` → excluída
  do total do rateio; as parcelas entram pela categoria do parcelamento.
- Contas de valor variável (água/luz/gás): status "aguardando", não contam até preencher.
- Nunca registrar o **conteúdo** das mensagens do casal em logs (só ações técnicas).
- Assistente não cria login/senha; não usa dados financeiros falsos.

## 7. Banco de dados e integrações
- **Firebase Firestore** (2 projetos: `financeiro-pessoal-bda5d`, `financeiro-manfrin`),
  região southamerica-east1, plano Spark. Regra: `if request.auth != null`.
- **Firebase Auth** (email/senha) + `sendPasswordResetEmail`.
- **Vercel** (deploy estático, projetos `financeiro-familia` e `financeiro-manfrin`,
  time `essencial`).
- **GitHub** (repos públicos `willianwiab/financeiro-familia` e `.../financeiro-manfrin`,
  + GitHub Pages).
- **mailto** para wenprodutora@gmail.com (sugestões) — sem servidor.
- CDNs: Firebase SDK 12.x, Chart.js 4.4, XLSX.
- Coleções: usuarios, lancamentos, meses, categorias, cartoes, faturas, parcelamentos,
  regras_categorizacao, orcamentos, conciliacoes, fechamentos, gratidoes, logs, sugestoes,
  familia, casal_mensagens, casal_recados, casal_humor, casal_convites, casal_desafios,
  casal_medalhas, casal_config.

## 8. Arquivos principais
- `index.html` — o app inteiro (fonte única de verdade).
- `gerar-manfrin.py` — gera `_deploy-manfrin/index.html` trocando só o `firebaseConfig`.
- `_deploy/index.html` — cópia linkada ao Vercel `financeiro-familia`.
- `_deploy-manfrin/index.html` — cópia + git próprio (repo/Vercel do manfrin).
- `CLAUDE.md` — guia permanente. `PLANO.md` — checklist original dos 6 módulos (histórico).
- `referencia-wen.html` — referência do WEN (⚠️ credenciais de outro Firebase; NÃO deployar).
- `.gitignore` — exclui `referencia-wen.html`, `_deploy/`, `_deploy-manfrin/`, `.vercel/`.
- `assets/` — artes do calendário de IG (não faz parte do app).

## 9. Problemas conhecidos / riscos
- **Módulo de Cartão é o mais frágil** (idempotência de fatura/parcela). Já houve um
  incidente de **perda de dados em teste** (JUL/2026 zerado, recuperado por backup).
- **Fatura prévia (nova)**: grava contas reais em meses futuros. Foi testada só na
  renderização/parse; o caminho de **escrita no Firestore não foi validado com dados
  reais** (o assistente não loga com senha). Precisa Will testar com **backup feito**.
- **Segurança do cadastro aberto:** qualquer usuário autenticado lê/escreve tudo da
  instância (regra `if request.auth != null`). Aceitável p/ casal; revisar se abrir mais.
- **localStorage stale:** se docs forem hard-deleted no console (sem soft-delete), o cache
  pode manter lançamento fantasma; limpar via `localStorage.removeItem`.
- Modo simulação do WEN original não isola dados em memória (origem do incidente). Aqui
  não há "modo simulação", mas testar direto no Firebase real polui dados.

## 10. Tarefas pendentes
- **Will:** testar a fatura prévia + pizza dos meses futuros com dados reais (backup antes).
- **Will:** testar o **refino de categoria por item** na fatura real (backup antes) — validar que
  re-salva a fatura sem alterar o total, a pizza recalcula, e a regra aprendida vale na próxima importação.
- **Will:** criar/consolidar logins reais do casal; definir tetos reais do orçamento.
- Revisar segurança das regras Firestore (se for abrir para mais pessoas/filhos).
- (Opcional, discutido) usar formato AGO26 em outros lugares (ex.: nome "Fatura (prévia)"
  na lista de Contas a Pagar); mini-resumo por categoria dentro da prévia expandida.
- (Pausado) app desktop/PWA; de-personalizar URL/GitHub (organização).
- **(Arquivado p/ quando o sistema estiver redondo) Tour narrado do app:** vídeo
  explicando cada tela/campo, da tela de login até a última aba. Plano acordado:
  montar um **demo local com dados fake e sem login** (arquivo separado, nunca deployado),
  eu dirijo e entrego **storyboard de prints + roteiro cronometrado**; narração via
  **TTS do CapCut** (PT-BR). Abrangência escolhida: **núcleo financeiro + Nosso Espaço**
  (login → Painel → Receber → Pagar → Cartões c/ sub-abas → Orçamento → Nosso Espaço).
  Limite: o assistente não tem voz/áudio ao vivo — entrega demo + roteiro + prints.

## 11. Próximos passos recomendados
1. Validar o ciclo de cartão ponta a ponta com os dados reais da Gabriela (fatura JUL
   importada, prévias AGO+, pizza por categoria) — com backup.
2. Se estiver ok, considerar polir detalhes visuais (tamanho da logo no login). ✅ Favicon
   "Boa Semente" (broto SVG inline) + theme-color verde já no ar nos dois deploys (14/07/2026).
3. Só então avançar para novas ideias (PWA, personalizar tetos, etc.).
4. Manter SEMPRE o fluxo dos dois deploys (família + manfrin) a cada mudança.

## 12. Detalhes importantes que não podem ser esquecidos
- **Toda alteração vai nos DOIS sistemas** (família e manfrin) — editar `index.html`,
  rodar `gerar-manfrin.py`, commitar/pushar e deployar as duas pastas.
- **"O parceiro" = o outro usuário da mesma instância** (cada família tem banco próprio,
  então já há isolamento entre famílias).
- **Idempotência do cartão por `faturaId`** é o que evita duplicar parcela/fatura — não
  quebrar. Prévia e fatura real usam o MESMO `faturaId` de propósito.
- **Não deployar** `referencia-wen.html` (credenciais de outro Firebase).
- **Não crio login/senha** do casal nem faço login com senha real; não uso números falsos.
- Datas de fatura na aba Faturas usam `C_mesCurto()` → formato **AGO26**.
- Login do Will (real): williamwiab81@gmail.com; Gabi: gn2gabriella@gmail.com.
- Firebase authorized domains já incluem os `*.vercel.app` e `willianwiab.github.io`.
