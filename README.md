# 🖨️ 3DFacil — Sistema de Gestão para Impressão 3D

> Plataforma completa para gerenciar o seu negócio de impressão 3D: orçamentos, pedidos, produção, estoque de filamento, financeiro, CRM e campanhas de marketing.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-07405E?logo=sqlite)](https://www.sqlite.org/)
[![Jinja2](https://img.shields.io/badge/Templates-Jinja2-white?logo=jinja)](https://palletsprojects.com/p/jinja/)
[![Tailwind CSS](https://img.shields.io/badge/CSS-Tailwind-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![bcrypt](https://img.shields.io/badge/Auth-bcrypt-purple?logo=python)](https://pypi.org/project/bcrypt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PT-BR](https://img.shields.io/badge/idioma-Português_do_Brasil-green)](README.md)

---

## 📖 Sobre o projeto

O **3DFacil** é um sistema de gestão (ERP leve) pensado especificamente para oficinas e prestadores de serviço de impressão 3D. Ele centraliza em um só lugar:

*   **Catálogo de produtos** — modelos prontos e personalizados, com peso, tempo de impressão, custo, preço, estoque e arquivos 3D.
*   **Orçamentos e pedidos** — geração de orçamentos (ORC-XXXX), conversão em pedidos, acompanhamento de status e histórico de alterações.
*   **Produção** — ordens de produção vinculadas a impressoras e filamentos, controle de consumo de material, registro de falhas e logs.
*   **Estoque de materiais** — filamentos (PLA, PETG, ABS, TPU...) com controle automático de saldo por movimentação de estoque (entrada/saída/ajuste).
*   **Impressoras** — cadastro de máquinas, potência, horas acumuladas e manutenções.
*   **Financeiro** — receitas e despesas, competência, vencimento, pagamento e vínculo com pedidos/clientes/fornecedores.
*   **CRM e marketing** — clientes, interações, campanhas e posts agendados.
*   **Tarefas** — quadro de atividades atribuídas a usuários.
*   **Precificação** — parâmetros de custo (energia, manutenção, depreciação, mão de obra, embalagem, perda e margem) para calcular o preço de venda.
*   **Usuários e segurança** — autenticação com senhas hasheadas (bcrypt), sessões, perfis `admin` e `staff`.

O banco de dados é **SQLite** (arquivo único, sem servidor externo) e a interface usa **Jinja2 + Tailwind CSS** renderizados pelo **FastAPI**.

---

## 🚀 Começando

### Pré-requisitos

*   [Python 3.10+](https://www.python.org/downloads/)
*   [pip](https://pip.pypa.io/en/stable/installation/) (vem com o Python)
*   [Git](https://git-scm.com/)

### 1. Clone o repositório

```powershell
git clone https://github.com/SEU_USUARIO/3DFacil.git
cd 3DFacil
```

### 2. Crie e ative o ambiente virtual

```powershell
# Cria o ambiente virtual
python -m venv venv

# Ativa (PowerShell)
venv\Scripts\Activate.ps1

# Ativa (CMD)
venv\Scripts\activate.bat

# Ativa (Linux/macOS)
source venv/bin/activate
```

> 💡 O `venv/` já está ignorado pelo `.gitignore`.

### 3. Instale as dependências

```powershell
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com os seus valores:

```powershell
copy .env.example .env
```

Edite o arquivo `.env`:

```ini
APP_ENV=development
SECRET_KEY=coloque_uma_chave_secreta_muito_forte_aqui
DATABASE_PATH=data/business.db
```

*   `APP_ENV`: ambiente da aplicação (`development` ou `production`).
*   `SECRET_KEY`: chave secreta para assinar as sessões de usuário (obrigatória em produção).
*   `DATABASE_PATH`: caminho do banco SQLite (padrão: `data/business.db`).

---

## 🛠️ Inicializando o banco de dados

O esquema SQL completo fica em `scripts/schema.sql` e é executado idempotentemente (seguro rodar mais de uma vez).

```powershell
python scripts/init_db.py
```

Você verá algo como:

```text
Banco: C:\...\3DFacil\data\business.db

22 tabelas:
  - categories
  - company_settings
  - customers
  ...
4 views:
  - v_materials
  - v_products
```

### Criando o primeiro administrador

Após criar o banco, cadastre o primeiro usuário com perfil de administrador:

```powershell
python scripts/create_admin.py
```

Informe nome, e-mail e senha (mínimo de 8 caracteres). A senha será armazenada com hash **bcrypt**.

---

## ▶️ Rodando a aplicação

### Opção A — pelo script da aplicação (recomendado)

```powershell
python app/app.py
```

Você verá as URLs de acesso:

```text
============================================
       SERVIDOR 3D FÁCIL
============================================
 Local:  http://localhost:8000
 Rede:   http://192.168.x.x:8000
============================================
```

Abra o navegador em **http://localhost:8000**.

### Opção B — direto com o Uvicorn

```powershell
uvicorn app:app --host 0.0.0.0 --port 8000
```
*(Execute dentro da pasta `app/` ou ajuste o caminho do módulo.)*

---

## 📁 Estrutura de pastas

```
3DFacil/
├── app/
│   ├── app.py              # Aplicação FastAPI, rotas e inicialização do servidor
│   ├── config.py           # Configurações baseadas em variáveis de ambiente
│   ├── database.py         # Conexão SQLite, sessões e init do schema
│   ├── static/             # CSS, JS, imagens e uploads (arquivos estáticos)
│   └── templates/          # Templates HTML (Jinja2 + Tailwind)
│       └── home.html
├── scripts/
│   ├── schema.sql          # Esquema completo do banco SQLite (tabelas, views, triggers)
│   ├── init_db.py          # Inicializa/create das tabelas
│   └── create_admin.py     # Cria o primeiro usuário administrador
├── data/                   # Banco de dados SQLite (ignorado pelo Git)
├── venv/                   # Ambiente virtual (ignorado pelo Git)
├── .env                    # Variáveis de ambiente locais (ignorado pelo Git)
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos e pastas ignorados pelo Git
├── requirements.txt        # Dependências Python
└── README.md
```

---

## 🗄️ Banco de dados

O esquema está em `scripts/schema.sql` e segue estas convenções:

| Convenção | Detalhe |
|-----------|---------|
| Dinheiro | Armazenado em **centavos** (`INTEGER`). Ex.: R$ 12,50 = `1250` |
| Datas | Texto ISO: `AAAA-MM-DD` ou `AAAA-MM-DD HH:MM:SS` (UTC) |
| Pesos | Gramas (`REAL`) |
| Tempos | Minutos (`INTEGER`) |
| Potência | Watts (`INTEGER`) |
| Percentuais | Pontos percentuais (`5 = 5%`) |

Principais entidades:

*   `users` — usuários do sistema (`admin`, `staff`)
*   `company_settings` — dados da empresa (nome, documento, endereço, logo)
*   `pricing_settings` — parâmetros da calculadora de precificação
*   `customers` / `customer_interactions` — CRM e histórico de contatos
*   `categories` / `products` / `product_images` — catálogo de produtos 3D
*   `suppliers` / `materials` / `printers` / `maintenance_records` — estoque e máquinas
*   `quotes` / `quote_items` — orçamentos
*   `orders` / `order_items` / `order_status_history` — pedidos e rastreamento de status
*   `production_orders` / `production_logs` — ordens de produção e logs
*   `inventory_movements` — movimentações de estoque com gatilhos (triggers) que atualizam o saldo automaticamente
*   `financial_transactions` — contas a pagar/receber
*   `tasks` — tarefas
*   `marketing_campaigns` / `marketing_posts` — marketing

As views `v_products` e `v_materials` expõem margem de lucro, custo por grama e alerta de estoque baixo.

---

## 🔐 Segurança

*   Senhas armazenadas com **bcrypt** (nunca em texto puro).
*   Sessões de usuário assinadas com `SECRET_KEY` via `SessionMiddleware` (Starlette).
*   Chave secreta deve ser definida via variável de ambiente `SECRET_KEY`.
*   Movimentações de estoque são **imutáveis**: para corrigir, crie um ajuste (imposto por triggers do SQLite).

---

## 🧭 Rotas principais

Atualmente a aplicação expõe a página inicial:

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Página inicial / dashboard (HTML via Jinja2) |

Os arquivos estáticos são servidos em `/static`.

> 🚧 Em desenvolvimento: rotas de autenticação, CRUD de clientes, produtos, orçamentos, pedidos, produção e financeiro estão sendo implementadas sobre o schema já existente.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir **issues** e enviar **pull requests**.

1. Faça um fork do projeto
2. Crie uma branch: `git checkout -b minha-feature`
3. Faça suas alterações e commit: `git commit -m "feat: descrição da alteração"`
4. Envie: `git push origin minha-feature`
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

Desenvolvido com ❤️ para facilitar a gestão de negócios de impressão 3D.

---

*Última atualização: Novembro de 2026*
