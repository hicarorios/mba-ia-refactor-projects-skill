# Skill de Auditoria e Refatoração Arquitetural — `refactor-arch`

Uma **Agent Skill** do Claude Code que audita qualquer projeto web/API e o refatora para o padrão **MVC**, de forma **agnóstica de tecnologia**. A skill executa três fases sequenciais — **Análise → Auditoria → Refatoração** — pausando para confirmação humana antes de modificar qualquer arquivo, e validando ao final que a aplicação continua subindo e respondendo.

Este repositório aplica a skill em três projetos legados de stacks diferentes:

| Projeto | Stack | Ponto de partida |
|---|---|---|
| `code-smells-project` | Python / Flask (SQLite cru) | Monólito plano (4 arquivos) — API de e-commerce |
| `ecommerce-api-legacy` | Node.js / Express (SQLite) | God Class única — LMS com checkout |
| `task-manager-api` | Python / Flask (SQLAlchemy) | Parcialmente em camadas — Task Manager |

---

## A) Análise Manual

Antes de criar a skill, cada projeto foi lido manualmente para entender os problemas que ela precisaria detectar. Abaixo, os achados por projeto, com severidade e justificativa. (A saída completa da skill está em `reports/audit-project-{1,2,3}.md`.)

### Projeto 1 — `code-smells-project` (Python/Flask, ~780 linhas, 4 arquivos)

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | SQL Injection por concatenação de strings em **todas** as queries | `models.py` (várias: 28, 47-50, 109-111, 140, 148-166, 289-299) | Permite roubo de dados, bypass de login e destruição de dados |
| CRITICAL | `/admin/query` executa SQL arbitrário do cliente; `/admin/reset-db` sem auth | `app.py:59-78`, `47-57` | Takeover total do banco por qualquer requisição |
| CRITICAL | `SECRET_KEY` hardcoded **e** vazado no `/health` | `app.py:7`, `controllers.py:289` | Segredo não rotacionável e exposto a qualquer chamador |
| CRITICAL | Senhas em texto puro (armazenadas, comparadas e retornadas no payload) | `database.py:75-83`, `models.py:105-120` | Um vazamento do DB expõe todas as credenciais |
| HIGH | Lógica de negócio + notificações (email/sms/push) dentro do controller | `controllers.py:208-210,247-250` | Regras não testáveis/reutilizáveis sem HTTP |
| HIGH | Conexão de banco como singleton global mutável | `database.py:4-10` | Acoplamento oculto, risco de concorrência, estado vazando entre requisições |
| HIGH | `DEBUG=True` + `host=0.0.0.0` anunciando-se como "produção" | `app.py:8,88` | Debugger do Werkzeug permite execução de código; vaza internals |
| MEDIUM | Query N+1 ao montar pedidos | `models.py:171-233` | O(N) round-trips ao DB |
| MEDIUM | Validação duplicada/espalhada nos controllers | `controllers.py:28-54,72-90` | Regras divergem entre cópias |
| MEDIUM | `except Exception` engolindo erros, sem handler central | `controllers.py` (vários) | Mascara falhas e vaza internals |
| LOW | `print()` como logging | `controllers.py` (vários) | Sem níveis/estrutura |
| LOW | Magic numbers nas faixas de desconto | `models.py:256-262` | Intenção escondida |
| LOW | Imports não usados | `models.py:2`, `database.py:2` | Ruído e dependências falsas |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, ~180 linhas, 3 arquivos)

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | Credenciais e chave de pagamento `pk_live_...` hardcoded | `src/utils.js:1-7` | Chave de pagamento real e credenciais expostas no fonte |
| CRITICAL | God Class `AppManager` (DB + rotas + pagamento + auditoria + relatório) | `src/AppManager.js` (todo) | Impossível testar; qualquer mudança afeta tudo |
| CRITICAL | Hash de senha caseiro (`badCrypto`) + senha plaintext no seed | `src/utils.js:17-23`, `AppManager.js:18,68` | Esquema trivialmente reversível |
| HIGH | Estado global mutável (`globalCache`, `totalRevenue`) | `src/utils.js:9-10` | Estado vaza entre requisições; não testável |
| HIGH | Callback hell / lógica de negócio aninhada no handler de rota | `src/AppManager.js:28-78` | Ilegível, error handling inconsistente |
| HIGH | Número de cartão e chave de pagamento gravados em log | `src/AppManager.js:45` | Vazamento de dado sensível (PCI) e de segredo |
| MEDIUM | Query N+1 no relatório financeiro | `src/AppManager.js:80-129` | O(cursos × matrículas) round-trips |
| MEDIUM | Validação fraca / senha default "123456" | `src/AppManager.js:35,46,68` | Credenciais fracas criadas silenciosamente |
| MEDIUM | Delete sem integridade referencial (registros órfãos) | `src/AppManager.js:131-137` | Dados inconsistentes |
| LOW | Nomes de variáveis ruins (`u`, `e`, `p`, `cid`, `cc`) | `src/AppManager.js:29-33` | Difícil de ler |
| LOW | `console.log` como logging | `src/utils.js:13`, `AppManager.js:45,59` | Sem estrutura/níveis |

### Projeto 3 — `task-manager-api` (Python/Flask + SQLAlchemy, ~1158 linhas)

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | `SECRET_KEY` hardcoded | `app.py:13` | Segredo não rotacionável, exposto no repo |
| HIGH | Hash de senha em **MD5** | `models/user.py:27-32` | MD5 é rápido e quebrado |
| HIGH | Senha exposta no `to_dict()` (e em vários endpoints) | `models/user.py:16-25` | Material de credencial vaza na API |
| HIGH | Credenciais SMTP hardcoded | `services/notification_service.py:7-10` | Credenciais de email no fonte |
| HIGH | Lógica de negócio pesada nas rotas; sem controllers/services usados | `routes/*.py` | Lógica não testável/reutilizável |
| MEDIUM | Cálculo de "overdue"/stats duplicado em 6 lugares (`Task.is_overdue()` existe e não é usado) | `task_routes.py`, `report_routes.py`, `user_routes.py` | Risco de divergência |
| MEDIUM | `except:` genérico engolindo erros | `task_routes.py`, `user_routes.py`, `report_routes.py` | Mascara falhas reais |
| MEDIUM | **API deprecated:** `datetime.utcnow()` (Python 3.12) | models, routes, services, helpers | Deprecada; remoção futura; bugs tz-naive |
| LOW | Imports não usados (`os, sys, json, time, math, hashlib`) | `app.py:7`, `task_routes.py:7`, `utils/helpers.py:3-7` | Ruído |
| LOW | Serialização de task duplicada inline | `task_routes.py:17-28`, `user_routes.py:162-169` | Shapes divergem |
| LOW | Magic numbers / constantes não reaproveitadas | `task_routes.py`, `report_routes.py` | Intenção escondida |

---

## B) Construção da Skill

### Estrutura e decisões de design

A skill vive em `.claude/skills/refactor-arch/` e segue **progressive disclosure**: o `SKILL.md` é enxuto e apenas **orquestra** as 3 fases; todo o conhecimento de domínio fica em `references/`, carregado sob demanda por fase.

```
.claude/skills/refactor-arch/
├── SKILL.md                          # orquestra as 3 fases (é o "prompt")
└── references/
    ├── project-analysis.md           # heurísticas de detecção de stack/DB/arquitetura (Fase 1)
    ├── anti-patterns-catalog.md      # 17 anti-patterns + detecção de APIs deprecated (Fase 2)
    ├── report-template.md            # formato padronizado do relatório (Fase 2)
    ├── mvc-guidelines.md             # regras do MVC alvo e adaptação ao contexto (Fase 3)
    └── refactoring-playbook.md       # 11 transformações antes/depois (Fase 3)
```

Decisões principais:

- **Prompt puro + referências, sem scripts.** A detecção e a validação são feitas pelo agente com ferramentas genéricas (ler manifestos, `grep`, subir o app, `curl`), nunca com código acoplado a uma linguagem. Isso maximiza o agnosticismo.
- **Gate humano obrigatório.** A Fase 2 termina imprimindo `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e **não escreve nenhum arquivo de projeto** até a confirmação. O único arquivo escrito antes da confirmação é o próprio relatório em `reports/`.
- **Validação real com baseline antes/depois.** Antes de refatorar, a skill sobe o app original e registra as respostas dos endpoints-chave; depois, sobe o refatorado e compara status + shape. Isso prova diretamente que "os endpoints originais continuam respondendo".
- **Output determinístico.** As fases imprimem blocos de formato fixo, o que facilita a verificação dos critérios de aceite.
- **Path do relatório desacoplado.** A skill grava em `./reports/audit.md` relativo ao projeto atual, mantendo-a **idêntica** nos 3 projetos; a cópia para `reports/audit-project-N.md` na raiz do repositório é um passo de entrega.

### Catálogo de anti-patterns (17 tipos, com severidade distribuída)

Hardcoded Credentials/Secrets, SQL Injection, Arbitrary Code/SQL Execution, God Class/Method, Insecure Password Storage (CRITICAL); Business Logic in Controller, Global Mutable State/Singleton, Debug Mode/Insecure Defaults, Tight Coupling/No DI (HIGH); N+1 Query, Missing/Duplicated Validation, Generic Exception Swallowing, **Deprecated API Usage** (MEDIUM); `print`/`console.log` Logging, Magic Numbers, Poor Naming, Dead/Unused Imports (LOW).

Cada anti-pattern tem **sinais de detecção acionáveis** (ex.: "SQL montado com concatenação de input", "loop que emite uma query por iteração", "`datetime.utcnow()` em Python ≥3.12"), não descrições vagas. O catálogo inclui obrigatoriamente a **detecção de APIs deprecated** (AP-13), com uma tabela de equivalentes modernos por stack (Flask, Python 3.12, Express/Node) — usada na prática no projeto 3 (`datetime.utcnow()`).

### Como o agnosticismo foi garantido

- Detecção baseada em **evidência** (manifestos `requirements.txt`/`package.json`, depois imports no código), nunca assumindo a linguagem.
- O **playbook traz exemplos em Python e em Node** lado a lado para cada transformação.
- As **guidelines de MVC adaptam o formato ao contexto**: monólitos planos viram `src/` completo; projetos já em camadas recebem *deepening in-place* (sem mover tudo para um `src/` novo), preservando o contrato dos endpoints.
- A mesma skill, byte a byte, foi copiada para os 3 projetos e executou as 3 fases em todos.

### Desafios encontrados e como foram resolvidos

- **Segurança × "o app precisa subir".** Trocar senhas para hash forte quebraria o login dos dados já semeados. Resolvido **re-semeando** com as senhas já hasheadas (werkzeug/bcrypt), mantendo o login funcionando. Segredos passaram a vir de env (config estrito + `.env.example`).
- **Endpoints perigosos × contrato.** `/admin/query` (SQL arbitrário) não foi removido — a rota continua registrada e **responde** (agora 403), eliminando a vulnerabilidade sem quebrar o critério "endpoints originais continuam respondendo".
- **API deprecated com armadilha de timezone.** Trocar `datetime.utcnow()` por `datetime.now(UTC)` (tz-aware) quebraria as comparações com datas *naive* já no banco. Resolvido com um helper `now_utc()` que retorna UTC **naive**, removendo a deprecação sem alterar o comportamento.
- **Preservar shapes exatos de resposta.** No projeto 3, endpoints de listagem, detalhe e busca tinham shapes ligeiramente diferentes; a refatoração centralizou a serialização preservando cada shape (validado pelo baseline).

---

## C) Resultados

### Resumo das auditorias

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Deprecated API |
|---|---|---|---|---|---|---|
| code-smells-project | 4 | 3 | 3 | 4 | **14** | nenhuma detectada |
| ecommerce-api-legacy | 3 | 3 | 3 | 2 | **11** | nenhuma detectada |
| task-manager-api | 1 | 4 | 3 | 3 | **11** | `datetime.utcnow()` (Python 3.12) |

### Antes / Depois da estrutura

**Projeto 1 — monólito → `src/` MVC**
```
ANTES                          DEPOIS
app.py                         app.py (entry fino)
controllers.py                 src/config/{settings,constants}.py
models.py                      src/models/{connection,produto,usuario,pedido}_model.py
database.py                    src/services/{notification,pedido,relatorio}_service.py
                               src/controllers/{produto,usuario,pedido,relatorio,admin,health}_controller.py
                               src/views/routes.py
                               src/validators/produto_validator.py
                               src/middlewares/error_handler.py
                               src/app.py (composition root)
```

**Projeto 2 — God Class → `src/` MVC**
```
ANTES                          DEPOIS
src/app.js                     src/app.js (composition root)
src/AppManager.js              src/config/settings.js
src/utils.js                   src/models/{database,user,course,enrollment,payment,audit,report}Repository.js
                               src/services/{cache,password,payment,checkout,report,user}Service.js
                               src/controllers/{checkout,report,user}Controller.js
                               src/routes/index.js
                               src/middlewares/errorHandler.js
                               src/utils/logger.js
```

**Projeto 3 — deepening in-place (sem `src/`)**
```
ANTES                          DEPOIS (mantém models/ e routes/, adiciona camadas)
app.py                         app.py + config/settings.py
models/                        controllers/{task,user,report,category}_controller.py
routes/                        services/{task,user,report,category,notification}_service.py
services/                      validators/{task,user}_validator.py
utils/                         middlewares/error_handler.py
                               shared/{serializers,time}.py
```

### Checklist de Validação (preenchido nos 3 projetos)

| Item | P1 | P2 | P3 |
|---|---|---|---|
| **Fase 1** — Linguagem detectada | ✅ Python | ✅ Node.js | ✅ Python |
| Framework detectado | ✅ Flask 3.1.1 | ✅ Express 4.18 | ✅ Flask + SQLAlchemy |
| Domínio descrito | ✅ E-commerce | ✅ LMS/checkout | ✅ Task Manager |
| Nº de arquivos confere | ✅ 4 | ✅ 3 | ✅ 14 |
| **Fase 2** — Segue o template | ✅ | ✅ | ✅ |
| Cada finding com arquivo+linha | ✅ | ✅ | ✅ |
| Ordenado por severidade | ✅ | ✅ | ✅ |
| ≥ 5 findings | ✅ 14 | ✅ 11 | ✅ 11 |
| Detecção de deprecated API | n/a | n/a | ✅ |
| Pausa pedindo confirmação | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura MVC | ✅ | ✅ | ✅ |
| Config sem hardcoded | ✅ | ✅ | ✅ |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| App inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints respondem | ✅ | ✅ | ✅ |

### Evidência de execução (logs reais, antes × depois)

**Projeto 1** — login e endpoints (depois da refatoração):
```
[GET /health]            -> 200  (sem secret_key no payload — antes vazava)
[GET /usuarios]          -> 200  (sem campo "senha" — antes vazava)
[POST /login admin]      -> 200  {"dados":{...,"tipo":"admin"},"mensagem":"Login OK"}
[POST /login wrong]      -> 401  {"erro":"Email ou senha inválidos"}
[POST /pedidos]          -> 201  {"dados":{"pedido_id":1,"total":6179.79}}   (idêntico ao baseline)
[POST /admin/query]      -> 403  {"erro":"Endpoint desativado por segurança"} (rota mantida)
```

**Projeto 2** — checkout e relatório (depois):
```
[POST /api/checkout ok]      -> 200  {"msg":"Sucesso","enrollment_id":2}     (idêntico ao baseline)
[POST /api/checkout denied]  -> 400  Pagamento recusado                       (idêntico)
[GET /api/admin/financial-report] -> 200  [{"course":"Clean Architecture",...}] (idêntico)
[DELETE /api/users/1]        -> 200  cascata aplicada (sem registros órfãos)
log de pagamento:            card "****4444"  (antes logava o número completo + a chave)
```

**Projeto 3** — stats, relatório e segurança (depois):
```
[GET /tasks/stats]      -> 200  {"total":10,"pending":6,"done":1,"overdue":2,"completion_rate":10.0}  (idêntico)
[GET /reports/summary]  -> overdue_count=2, by_priority idêntico ao baseline
[POST /login joao/1234] -> 200  + token   (funciona após re-seed com hash; sem campo password)
[POST /login wrong]     -> 401
hash armazenado:        scrypt:...   (antes: MD5)
nenhum warning de datetime.utcnow (deprecated API corrigida)
```

### Como a skill se comportou em stacks diferentes

A mesma skill detectou corretamente Python/Flask (cru e com ORM) e Node/Express, e **adaptou a profundidade da refatoração ao contexto**: reestruturação completa em `src/` para os dois monólitos, e *deepening in-place* para o projeto já parcialmente organizado, sem quebrar nenhum contrato de endpoint.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado.
- Para validar localmente: **Python 3.12+** (projetos 1 e 3) e **Node.js 18+** (projeto 2).

### Executar a skill

A skill já está em `.claude/skills/refactor-arch/` dentro de cada projeto. Em cada um:

```bash
cd code-smells-project        # ou ecommerce-api-legacy / task-manager-api
claude "/refactor-arch"
```

A skill roda a Fase 1 (análise) e a Fase 2 (auditoria), salva o relatório em `reports/audit.md` e **pausa** pedindo `[y/n]`. Ao confirmar com `y`, executa a Fase 3 (refatoração + validação).

### Rodar e validar cada projeto refatorado

Os três projetos leem segredos do ambiente — **copie `.env.example` para `.env`** antes de subir.

**Projeto 1 — code-smells-project (Flask)**
```bash
cd code-smells-project
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # ajuste SECRET_KEY se quiser
.venv/bin/python app.py     # http://localhost:5000
curl localhost:5000/health
curl -X POST localhost:5000/login -H 'Content-Type: application/json' -d '{"email":"admin@loja.com","senha":"admin123"}'
```

**Projeto 2 — ecommerce-api-legacy (Express)**
```bash
cd ecommerce-api-legacy
npm install
cp .env.example .env        # defina PAYMENT_GATEWAY_KEY
npm start                   # http://localhost:3000
curl -X POST localhost:3000/api/checkout -H 'Content-Type: application/json' \
  -d '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}'
curl localhost:3000/api/admin/financial-report
```

**Projeto 3 — task-manager-api (Flask + SQLAlchemy)**
```bash
cd task-manager-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # defina SECRET_KEY
.venv/bin/python seed.py    # popula o banco (senhas já com hash)
.venv/bin/python app.py     # http://localhost:5000
curl localhost:5000/tasks/stats
curl -X POST localhost:5000/login -H 'Content-Type: application/json' -d '{"email":"joao@email.com","password":"1234"}'
```

### Validar que a refatoração funcionou

Para cada projeto: o app **sobe sem erros** e os **endpoints originais respondem** com o mesmo status/shape de antes (com as melhorias de segurança esperadas: nenhum segredo ou senha exposto, SQL parametrizado, endpoints perigosos neutralizados). Os relatórios de auditoria estão em `reports/audit-project-{1,2,3}.md`.
