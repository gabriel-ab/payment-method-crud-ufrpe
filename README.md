# Payment Method CRUD Microservice

Este microserviço fornece uma API para cadastro, consulta, atualização e remoção de métodos de pagamento de cartão, utilizando FastAPI, SQLModel e SQLite.

## Funcionalidades
- Cadastro de métodos de pagamento de cartão (com UUID)
- Listagem de métodos de pagamento por usuário
- Atualização parcial de métodos de pagamento
- Remoção de métodos de pagamento

## Estrutura do Model
- **uuid**: Identificador único (UUID)
- **user**: UUID do usuário
- **owner_name**: Nome do titular do cartão
- **card_number**: Número do cartão (16 dígitos)
- **expiration_date**: Data de validade (MM/YYYY)
- **security_code**: Código de segurança (3 dígitos)

## Endpoints

### Criar método de pagamento
`POST /payment_method`
- Body: `{ "user": UUID, "owner_name": str, "card_number": str, "expiration_date": str, "security_code": str }`
- Resposta: Dados do método criado

### Listar métodos de pagamento
`GET /payment_method?user=<UUID>`
- Resposta: Lista de métodos do usuário

### Atualizar método de pagamento
`PATCH /payment_method?user=<UUID>&uuid=<UUID>`
- Body: Campos a atualizar
- Resposta: Dados atualizados

### Remover método de pagamento
`DELETE /payment_method?user=<UUID>&uuid=<UUID>`
- Resposta: 204 No Content

## Como rodar localmente

1. Execute a API:
```sh
docker compose up
# OR
uv sync
source .venv/bin/activate
fastapi devfastapi dev
```

2. Acesse a documentação interativa em: [http://localhost:8000/docs](http://localhost:8000/docs)

> OU: execute `docker compose up`
---

> Projeto desenvolvido para fins acadêmicos na UFRPE.
