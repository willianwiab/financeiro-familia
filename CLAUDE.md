# CLAUDE.md — Boa Semente (Sistema Financeiro da Família)

> Guia permanente do projeto. Para o estado atual detalhado (o que está pronto,
> pendências, próximos passos), veja **PROJECT_STATUS.md**.

## O que é
App financeiro de casal/família, marca **"Boa Semente — Fé · Família · Finanças"**.
Clone adaptado do sistema WEN Financeiro (`referencia-wen.html` na raiz é só
referência de código/UX — **NÃO deployar** nem versionar em repo público: tem
credenciais de OUTRO Firebase). App **single-file** em `index.html`.

## Premissas da família (permanentes)
- **Finanças 100% JUNTAS.** NÃO existe rateio por pessoa, "quem deve pra quem",
  nem saldo entre os dois. Toda visão é consolidada. O rateio é **por categoria**.
- Logins servem para **auditoria** (quem lançou/alterou o quê) e para personalizar
  a experiência (nome, foto, saudação). Cadastro é aberto (casal + filhos).
- **NUNCA usar números financeiros falsos** — só reais ou marcados como demonstração.
- **Eu (assistente) NÃO crio conta/senha de ninguém** nem faço login com senha de
  usuário — o casal cria os próprios logins.

## Stack (não mudar sem perguntar)
- **HTML/CSS/JS puro, single-file `index.html`, SEM build, SEM framework.** Não
  inventar componentes React. Código e comentários em **português**.
- **Firebase** (Web SDK 12.x via CDN): Auth (email/senha) + Firestore. Config
  inline no `index.html`. **Sem Firebase Storage** (fotos vão como base64 em
  `usuarios/{uid}.fotoBase64`, redimensionadas via canvas 256px).
- CDN também: Chart.js 4.4 e XLSX. Imagens/logos embutidas como base64/data-URI.
- Regra Firestore atual (ambos os projetos): `allow read, write: if request.auth != null`.

## Duas instâncias (bancos separados = famílias isoladas)
Cada família = **projeto Firebase + projeto Vercel + repo GitHub próprios**. A
instância inteira É a família; "o parceiro" = o outro usuário em `usuarios`.
- **Família (Will+Gabi):** Firebase `financeiro-pessoal-bda5d` · Vercel
  `financeiro-familia` → https://financeiro-familia-ten.vercel.app · GitHub
  `willianwiab/financeiro-familia` (Pages: willianwiab.github.io/financeiro-familia).
  Fonte de verdade = `index.html` na raiz do projeto.
- **Manfrin (irmã+cunhado, cobaia):** Firebase `financeiro-manfrin` · Vercel
  `financeiro-manfrin` → https://financeiro-manfrin.vercel.app · GitHub
  `willianwiab/financeiro-manfrin` (Pages: willianwiab.github.io/financeiro-manfrin).
  Gerada a partir do principal por script (só troca o `firebaseConfig`).

## Fluxo de publicação (SEMPRE nos DOIS sistemas)
Toda alteração é aplicada às duas instâncias:
1. Editar `index.html` (fonte única).
2. **Família:** `cp index.html _deploy/index.html`; `git add index.html && git commit && git push`
   (atualiza GitHub Pages); `cd _deploy && npx vercel --prod --yes` (via subagente `deploy`).
3. **Manfrin:** `python3 gerar-manfrin.py` (regenera `_deploy-manfrin/index.html` com a
   config do manfrin); `cd _deploy-manfrin && git add -A && git commit && git push`; `npx vercel --prod --yes`.
- `_deploy/` e `_deploy-manfrin/` estão no `.gitignore` do repo família (são deploys
  próprios; `_deploy-manfrin` tem git próprio → repo do manfrin).
- Fim de mensagem de commit: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## Convenções de código
- Prefixos por módulo: `R_` (Receber), `P_` (Pagar), `C_` (Cartões), `B_` (conciliação
  bancária), `O_` (Orçamento), `D_` (Dashboard), `N_` (Novidades), `CASAL_` (Nosso Espaço).
- Toda escrita passa por `registrarLog` + `comCamposCriacao`/`comCamposEdicao` (nunca
  enviar `undefined` ao Firestore). Cache local + sync incremental por `alteradoEm`.
- Modais: `.modal-bg` + `.modal`, abre com `.classList.add('open')`.
- Temas: atributo `data-tema` no `<html>` + `localStorage.tema`. Padrão = `lar` (rótulo
  "🌱 Boa Semente", verde/bege). Outros: `escuro`, `hellokitty`.

## Estrutura Firestore (coleções)
Financeiras: `usuarios/{uid}` · `lancamentos/{id}` (receber, soft-delete `excluido:true`)
· `meses/{anoMes}` (pagar, doc = `{contas:[...]}`) · `categorias` · `cartoes` ·
`faturas/{cartaoId_anoMes}` (itens em array) · `parcelamentos/{grupoId}` ·
`regras_categorizacao` · `orcamentos/{anoMes__slug}` · `conciliacoes/{fitid}` ·
`fechamentos/{anoMes}` · `gratidoes` · `logs`.
Casal (Nosso Espaço): `casal_mensagens` · `casal_recados` · `casal_humor/{uid_data}` ·
`casal_convites` · `casal_desafios` · `casal_medalhas/{slug}` · `casal_config/geral`.
Outros: `sugestoes` · `familia/{...}` (config da família).

## REGRAS DE NEGÓCIO CRÍTICAS (cartão) — onde mora o maior risco de bug
1. **Duas visões:** *CAIXA* (a fatura = total do `.ofx`, IMUTÁVEL, vira lançamento em
   Pagar) e *COMPETÊNCIA* (cada item tem `dataCompra` real, só p/ análise). A data da
   compra reorganiza a ANÁLISE, nunca o VALOR do lançamento.
2. **Importação só via `.ofx` de fatura JÁ FECHADA.** Valor total = soma do arquivo.
   Validar: soma dos itens === total do `.ofx` (senão avisar).
3. **IDEMPOTÊNCIA:** item identificado por `FITID`. Reimportar o mesmo arquivo NÃO
   duplica — mostra tela de conferência (novos/duplicados/removidos) e **substitui** a
   fatura anterior (`contas.filter(c => c.faturaId !== fatura.id)` antes de inserir).
   Nunca append cego. Quando a fatura tem parcelas, checkbox obrigatório antes de confirmar.
4. **ANTI-DUPLICAÇÃO no rateio/pizza:** o lançamento espelho "💳 Cartões" (que tem
   `faturaId`) é EXCLUÍDO do rateio; no lugar entram os **itens detalhados** da fatura,
   por categoria. Nunca somar os dois.
5. **Parcelamentos:** parser lê "x/y"; projeta as parcelas restantes em `parcelamentos`
   (`parcelaAtual = max`). **Fatura PRÉVIA:** cada mês futuro com parcelas vira uma conta
   REAL em Contas a Pagar (`{previa:true, faturaId:cartaoId_mes}`) — mesmo `faturaId` da
   fatura real, então ao importar o `.ofx` do mês a prévia é **substituída** (sem duplicar).
   A categoria escolhida na importação (guardada no parcelamento) alimenta o pizza dos
   meses futuros.

## Como trabalhar
- Preservar TODA a inteligência financeira (módulos R/P/C/B/O/D). A camada família e o
  Nosso Espaço são cascas por cima.
- No módulo de **Cartões**, mudanças que gravam dados são de ALTO RISCO (já houve
  incidente de perda de dados em teste — ver PROJECT_STATUS.md). Preferir soluções
  idempotentes por `faturaId`; recomendar backup antes de testar com dados reais.
- Não deployar `referencia-wen.html` nem os `.md`.
- Testar localmente: `python3 -m http.server 8901 --directory <projeto>` + navegador.
  (Não consigo logar com senha real, então o caminho de escrita no Firestore é testado
  pelo Will com dados reais + backup.)
