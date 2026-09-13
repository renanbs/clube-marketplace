---
name: data-privacy-observability
description: |
  Especialista em tratamento de dados pessoais em logs, telemetria, erros e analytics.
  Agnóstica de stack e de linguagem: cada seção declara o princípio e exemplifica numa stack concreta.
  Ative esta skill sempre que:
  - Escrever ou revisar logging, structured logging, tracing ou métricas que toquem dados de usuário.
  - Instrumentar erros com Sentry, Rollbar, Datadog, Grafana ou similar.
  - Lidar com telefone, e-mail, CPF/CNPJ, endereço, cartão, documento ou qualquer PII em código de backend ou frontend.
  - Depurar um bug cujo diagnóstico exige ver dados reais de cliente.
  - Montar dashboards, eventos de analytics ou exportações que agreguem dados de usuário.
  - Implementar retenção, anonimização, exclusão de conta ou resposta a pedido de titular (LGPD/GDPR).
license: Apache-2.0
metadata:
  version: v1.0
  author: clubedepontos
---

# Privacidade de Dados em Logs e Observabilidade

Como instrumentar um sistema para ser depurável **sem** transformar o agregador de logs num banco de dados pessoais paralelo, sem retenção, sem controle de acesso e fora de qualquer política.

> **Como ler esta skill:** cada seção declara primeiro o **princípio** e depois um **exemplo** numa stack concreta (Go no backend, JavaScript no frontend). O princípio é o que viaja entre projetos; o exemplo se traduz.

---

## 1. O Princípio Central: logue a FORMA do dado, não o dado

A escolha não é entre "logar o telefone do cliente" e "não logar nada". Essa falsa dicotomia é o que leva times a logar PII em claro — porque a alternativa aparente é ficar cego.

**O que você precisa em produção quase nunca é o valor.** É a *forma* do valor: o dado chegou? tem o tamanho certo? veio com máscara de formatação? é do país esperado? é o mesmo entre duas requisições? Tudo isso é observável sem materializar o dado.

Para cada campo sensível, crie um helper que exponha **o mínimo necessário para depurar** e nada além:

```go
package phonelog

// Mask exibe DDD + meio mascarado + últimos 4 dígitos (ex.: "11*****4321").
// Suficiente para o suporte confirmar com o cliente "é o número terminado em 4321?"
// sem que o número completo exista em nenhum log.
func Mask(phone string) string { /* ... */ }

// DDD retorna o código de área. Permite agregar e detectar anomalia regional
// (ex.: pico de cadastros de um DDD só) sem identificar ninguém.
func DDD(phone string) string { /* ... */ }

// DigitCount retorna a quantidade de dígitos após normalização.
// É isto que responde "o número chegou truncado?" — a pergunta real do bug.
func DigitCount(phone string) int { /* ... */ }
```

No ponto de uso:
```go
logger.Log.Warn("falha ao enviar confirmação",
    zap.String("phone", phonelog.Mask(customer.Phone)),
    zap.Int("phone_digits", phonelog.DigitCount(customer.Phone)),
    zap.String("appointment_id", appt.ID),
)
```

**Teste os helpers de mascaramento.** São código de segurança com aparência de formatação de string: um off-by-one que expõe um dígito a mais não quebra nada e não aparece em code review, mas muda o que fica retido em produção. Cubra caso vazio, curto demais, com e sem DDI, com pontuação.

### Formas de máscara por tipo de dado

| Dado | Logue | Nunca logue |
| :--- | :--- | :--- |
| Telefone | DDD + `*****` + últimos 4 | número completo |
| E-mail | domínio + 1ª letra (`r***@dominio.com`) ou hash estável | endereço completo |
| CPF/CNPJ | últimos 3 dígitos, ou só "válido/inválido" | documento completo, mesmo parcial no meio |
| Cartão | bandeira + últimos 4 (padrão PCI-DSS) | PAN, CVV ou validade — em hipótese nenhuma |
| Endereço | cidade/UF, ou CEP truncado nos 5 primeiros | logradouro, número, complemento |
| Nome | iniciais, ou omita | nome completo |
| Token/senha/chave | comprimento e prefixo de 4 chars, no máximo | o valor, nem "só pra debugar" |
| ID interno (UUID) | completo — é pseudônimo, não PII | — |

> **Prefira o ID ao dado.** Na maioria dos bugs, `user_id` + `appointment_id` levam o dev ao registro no banco, onde o acesso é controlado e auditado. O log só precisa da chave, não do conteúdo. Se o log tem ID suficiente, ele não precisa de PII nenhuma.

---

## 2. Hash estável quando você precisa correlacionar

Quando a pergunta é "é o mesmo usuário nas duas pontas?" e não "quem é o usuário?", use hash com salt fixo de aplicação. Isso permite `GROUP BY` e correlação entre serviços sem valor reversível no log.

```go
func StableHash(value string) string {
    sum := sha256.Sum256([]byte(appSalt + strings.ToLower(strings.TrimSpace(value))))
    return hex.EncodeToString(sum[:])[:12] // 12 chars bastam para correlacionar
}
```

Dois cuidados:
* **Normalize antes de hashear** (minúsculas, trim, só dígitos), ou o mesmo dado gera hashes diferentes e a correlação falha silenciosamente.
* **Hash de dado de baixa entropia é reversível por força bruta.** CPF tem 11 dígitos e telefone brasileiro tem ~11 — o espaço inteiro é enumerável em minutos. O salt de aplicação é o que impede isso, então ele é segredo de verdade: variável de ambiente, nunca no repositório. Sem salt, hashear CPF é teatro de privacidade.

---

## 3. O vazamento mais comum: serialização de struct inteira

Quase todo vazamento de PII em log vem de uma linha escrita para depurar e esquecida:

```go
log.Printf("payload: %+v", req)        // ❌ despeja o struct todo
logger.Info("user", zap.Any("u", user)) // ❌ idem
console.log('checkout', payload)        // ❌ idem, no browser
```

O problema não é a intenção, é que **o conjunto de campos cresce sem o log ser revisitado**. A linha foi escrita quando o struct tinha 3 campos; hoje tem 20, incluindo CPF e endereço, e ninguém releu aquele `%+v`.

**Regras:**
1. **Nunca serialize um struct de domínio, request ou response inteiro num log.** Liste campos explicitamente, sempre. É o mesmo princípio do `zero SELECT *` na camada de persistência, pela mesma razão.
2. **Implemente o marshaller do tipo sensível para já sair mascarado**, assim o erro deixa de ser possível em vez de depender de disciplina:
   ```go
   type Phone string

   func (p Phone) String() string        { return phonelog.Mask(string(p)) }
   func (p Phone) MarshalJSON() ([]byte, error) { return json.Marshal(phonelog.Mask(string(p))) }
   ```
   Em Python, `__repr__`; em Java, `toString()`; em TypeScript, um branded type com `toJSON()`.
3. **Trate erro de banco e de driver como conteúdo sensível.** Mensagens de erro de constraint frequentemente embutem o valor que violou a constraint (`duplicate key value violates unique constraint ... Key (email)=(fulano@x.com)`). Logar `err` cru vaza o valor. Logue o código do erro e a constraint, não a mensagem inteira.

---

## 4. Superfícies esquecidas

O log de aplicação é a superfície óbvia. Estas são as que passam:

* **Rastreador de erros (Sentry/Rollbar).** Captura variáveis locais do stack frame automaticamente. Configure o `before_send` / scrubbing para remover campos sensíveis por nome, e desative o envio de request body por padrão.
* **Tracing distribuído.** Atributos de span viram searchable text. `db.statement` com valores interpolados vaza o dado; com parâmetros ligados, não — é mais um motivo para nunca interpolar valor em query.
* **Labels de métrica.** Nunca use PII como label de Prometheus: além de vazar, é cardinalidade ilimitada (ver a skill de performance). Métrica é agregado; se precisa identificar alguém, não é métrica.
* **URL e query string.** Aparecem em log de acesso, de CDN, no `Referer` enviado a terceiros e no histórico do browser. Nunca coloque token, e-mail, CPF ou documento em path ou query — use corpo de requisição ou header.
* **`console.log` no frontend.** Fica visível para o usuário e para qualquer extensão instalada, e é capturado por ferramentas de session replay. Trate o console de produção como log público.
* **Session replay (Hotjar, Clarity, FullStory).** Grava o DOM, incluindo o que o usuário digita. Exige marcação explícita de exclusão nos campos sensíveis — normalmente um atributo por campo. Campo de senha, cartão e documento sempre mascarado.
* **Corpo de webhook e payload de gateway.** Logar a resposta bruta do gateway de pagamento "para depurar" é o caminho mais rápido para ter dado de cartão em texto puro no agregador.
* **Dump de banco em ambiente de desenvolvimento.** Restaurar dump de produção em stage ou local espalha a base de dados pessoais inteira para máquinas sem controle de acesso. Use dados sintéticos ou um dump anonimizado; se precisar de dado real, anonimize no momento da extração, não depois.

---

## 5. Auditoria: o que você DEVE registrar

Privacidade não é logar menos — é logar a coisa certa. Acesso privilegiado a dado de cliente deve ser registrado de forma **mais** completa, não menos.

**Toda sessão de impersonação, acesso administrativo a dado de cliente ou exportação em massa gera registro de auditoria** com: quem acessou, quem foi acessado, quando, o quê e por quê.

```go
func ImpersonationReadOnly() gin.HandlerFunc {
    return func(c *gin.Context) {
        impersonatorID, exists := c.Get("impersonatorID")
        if !exists {
            c.Next()
            return
        }

        // 1. Toda requisição impersonada é auditada — inclusive as bem-sucedidas.
        logger.Log.Info("impersonated request",
            zap.String("impersonator_id", impersonatorID.(string)),
            zap.String("target_user_id", c.GetString("userID")),
            zap.String("method", c.Request.Method),
            zap.String("path", c.Request.URL.Path),
        )

        // 2. Impersonação é somente leitura: suporte vê, suporte não age pelo cliente.
        if c.Request.Method != http.MethodGet {
            c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
                "error":      "read-only impersonation session",
                "error_code": "impersonation_readonly",
            })
            return
        }

        c.Next()
    }
}
```

As duas travas são independentes e ambas necessárias. **Somente leitura** garante que nenhuma ação fique atribuída ao cliente sem que ele a tenha feito — sem isso, o histórico da conta deixa de ser confiável como prova. **Auditoria de toda requisição** (não só das negadas) é o que permite responder "quem da equipe olhou os dados deste cliente?", que é uma pergunta que o titular tem direito de fazer.

O log de auditoria tem regras próprias: retenção mais longa, acesso mais restrito que o log de aplicação, e é append-only. Não misture com o log operacional.

---

## 6. Retenção e direito do titular

* **Defina retenção por tipo de log** e configure no agregador: log de aplicação curto (7–30 dias), auditoria longo (conforme a política/obrigação legal). Log sem política de retenção é retenção infinita — e um pedido de exclusão que você não consegue cumprir.
* **Um pedido de exclusão de conta precisa alcançar os logs.** É a razão prática mais forte para não ter PII neles: se o log só tem `user_id` e valores mascarados, apagar o registro no banco resolve; se tem e-mail e telefone em claro espalhados por 90 dias de log em três serviços, não tem como cumprir o pedido.
* **Minimize na origem.** Não colete campo que o produto não usa. Todo campo coletado vira campo a proteger, mascarar, reter, exportar sob pedido e vazar num incidente.
* **Base legal antes de enviar a terceiros.** Mandar dado de cliente para plataforma de anúncio, CRM ou ferramenta de analytics é tratamento de dado pessoal e precisa estar coberto na política de privacidade e respeitar a escolha do usuário quando houver consentimento — inclusive no disparo server-side, que não é brecha para ignorar uma recusa dada no banner.

---

## Checklist

- [ ] Todo campo sensível tem helper de máscara, e o helper tem teste unitário?
- [ ] O log usa ID (`user_id`, `order_id`) em vez do dado sempre que o ID basta para chegar no registro?
- [ ] Nenhum log serializa struct de domínio, request ou response inteiro (`%+v`, `zap.Any`, `console.log(obj)`)?
- [ ] Tipos sensíveis implementam `String()`/`MarshalJSON()` já mascarados?
- [ ] Erros de banco são logados por código/constraint, não pela mensagem crua?
- [ ] Rastreador de erros com scrubbing configurado e envio de request body desligado?
- [ ] Nenhuma PII como label de métrica, atributo de span, path ou query string?
- [ ] Session replay com campos sensíveis marcados para exclusão?
- [ ] Impersonação e acesso administrativo são somente leitura e geram auditoria de toda requisição?
- [ ] Log de auditoria separado do operacional, com retenção maior e acesso restrito?
- [ ] Retenção configurada por tipo de log no agregador?
- [ ] Ambiente de desenvolvimento usa dado sintético ou dump anonimizado, nunca dump de produção cru?
