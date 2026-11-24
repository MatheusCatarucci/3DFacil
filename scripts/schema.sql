-- =====================================================================
-- 3D Business Manager: schema SQLite
-- Convenções:
--   * Dinheiro em CENTAVOS (INTEGER). Ex.: R$ 12,50 = 1250
--   * Datas em texto ISO: 'AAAA-MM-DD' ou 'AAAA-MM-DD HH:MM:SS' (UTC)
--   * Pesos em gramas, tempos em minutos, potência em watts
--   * Percentuais em pontos percentuais (5 = 5%)
-- O script pode ser executado várias vezes (usa IF NOT EXISTS).
-- =====================================================================

-- ---------------------------------------------------------------------
-- USUÁRIOS E CONFIGURAÇÕES
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'staff' CHECK (role IN ('admin', 'staff')),
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Linha única (id = 1) com os dados da empresa
CREATE TABLE IF NOT EXISTS company_settings (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    name       TEXT,
    document   TEXT,
    phone      TEXT,
    email      TEXT,
    address    TEXT,
    city       TEXT,
    logo_path  TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Linha única (id = 1) com os parâmetros da calculadora de precificação.
-- Valores por hora em centavos. Perdas e margem em pontos percentuais.
CREATE TABLE IF NOT EXISTS pricing_settings (
    id                          INTEGER PRIMARY KEY CHECK (id = 1),
    kwh_price_cents             INTEGER NOT NULL DEFAULT 0 CHECK (kwh_price_cents >= 0),
    maintenance_cents_per_hour  INTEGER NOT NULL DEFAULT 0 CHECK (maintenance_cents_per_hour >= 0),
    depreciation_cents_per_hour INTEGER NOT NULL DEFAULT 0 CHECK (depreciation_cents_per_hour >= 0),
    labor_cents_per_hour        INTEGER NOT NULL DEFAULT 0 CHECK (labor_cents_per_hour >= 0),
    packaging_cents             INTEGER NOT NULL DEFAULT 0 CHECK (packaging_cents >= 0),
    additional_cents            INTEGER NOT NULL DEFAULT 0 CHECK (additional_cents >= 0),
    loss_percent                REAL NOT NULL DEFAULT 5  CHECK (loss_percent >= 0 AND loss_percent < 100),
    margin_percent              REAL NOT NULL DEFAULT 40 CHECK (margin_percent >= 0 AND margin_percent < 100),
    created_at                  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at                  TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO pricing_settings (id) VALUES (1);
INSERT OR IGNORE INTO company_settings (id) VALUES (1);

-- ---------------------------------------------------------------------
-- MARKETING
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id                       INTEGER PRIMARY KEY,
    name                     TEXT NOT NULL,
    channel                  TEXT NOT NULL DEFAULT 'outro'
        CHECK (channel IN ('instagram', 'whatsapp', 'site', 'indicacao', 'anuncio_pago', 'outro')),
    status                   TEXT NOT NULL DEFAULT 'planejada'
        CHECK (status IN ('planejada', 'ativa', 'pausada', 'encerrada')),
    start_date               TEXT,
    end_date                 TEXT,
    investment_cents         INTEGER NOT NULL DEFAULT 0 CHECK (investment_cents >= 0),
    leads_count              INTEGER NOT NULL DEFAULT 0 CHECK (leads_count >= 0),
    conversions_count        INTEGER NOT NULL DEFAULT 0 CHECK (conversions_count >= 0),
    attributed_revenue_cents INTEGER NOT NULL DEFAULT 0 CHECK (attributed_revenue_cents >= 0),
    notes                    TEXT,
    created_at               TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at               TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS marketing_posts (
    id            INTEGER PRIMARY KEY,
    campaign_id   INTEGER REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    channel       TEXT NOT NULL DEFAULT 'instagram',
    title         TEXT NOT NULL,
    caption       TEXT,
    scheduled_for TEXT,
    status        TEXT NOT NULL DEFAULT 'rascunho'
        CHECK (status IN ('rascunho', 'agendada', 'publicada', 'cancelada')),
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------
-- CLIENTES (CRM)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    phone       TEXT,
    email       TEXT CHECK (email IS NULL OR email <> ''),   -- guarde NULL, não ''
    city        TEXT,
    source      TEXT NOT NULL DEFAULT 'outro'
        CHECK (source IN ('instagram', 'whatsapp', 'site', 'indicacao', 'anuncio_pago', 'outro')),
    campaign_id INTEGER REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    status      TEXT NOT NULL DEFAULT 'lead' CHECK (status IN ('lead', 'cliente', 'inativo')),
    notes       TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_customers_email ON customers(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_customers_name     ON customers(name);
CREATE INDEX IF NOT EXISTS idx_customers_status   ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_campaign ON customers(campaign_id);

CREATE TABLE IF NOT EXISTS customer_interactions (
    id             INTEGER PRIMARY KEY,
    customer_id    INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    user_id        INTEGER REFERENCES users(id) ON DELETE SET NULL,
    channel        TEXT NOT NULL DEFAULT 'outro'
        CHECK (channel IN ('telefone', 'whatsapp', 'email', 'presencial', 'instagram', 'outro')),
    summary        TEXT NOT NULL,
    interacted_at  TEXT NOT NULL DEFAULT (datetime('now')),
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_interactions_customer ON customer_interactions(customer_id, interacted_at);

-- ---------------------------------------------------------------------
-- PRODUTOS
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS categories (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY,
    sku             TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name            TEXT NOT NULL,
    category_id     INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    description     TEXT,
    product_type    TEXT NOT NULL DEFAULT 'catalogo' CHECK (product_type IN ('catalogo', 'personalizado')),
    material_type   TEXT,
    color           TEXT,
    weight_g        REAL NOT NULL DEFAULT 0 CHECK (weight_g >= 0),
    print_minutes   INTEGER NOT NULL DEFAULT 0 CHECK (print_minutes >= 0),
    cost_cents      INTEGER NOT NULL DEFAULT 0 CHECK (cost_cents >= 0),
    price_cents     INTEGER NOT NULL DEFAULT 0 CHECK (price_cents >= 0),
    stock_qty       INTEGER NOT NULL DEFAULT 0 CHECK (stock_qty >= 0),
    model_file_path TEXT,
    status          TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo', 'rascunho')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_status   ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_name     ON products(name);

CREATE TABLE IF NOT EXISTS product_images (
    id         INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    file_path  TEXT NOT NULL,
    is_cover   INTEGER NOT NULL DEFAULT 0 CHECK (is_cover IN (0, 1)),
    position   INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_product_images_product ON product_images(product_id);

-- Margem = (preço − custo) / preço. NÃO é markup.
CREATE VIEW IF NOT EXISTS v_products AS
SELECT p.*,
       CASE WHEN p.price_cents > 0
            THEN (p.price_cents - p.cost_cents) * 100.0 / p.price_cents
       END AS margin_percent
FROM products p;

-- ---------------------------------------------------------------------
-- FORNECEDORES, ESTOQUE, IMPRESSORAS
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS suppliers (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    contact    TEXT,
    phone      TEXT,
    email      TEXT,
    notes      TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Filamentos (kind = 'filamento') e outros materiais (kind = 'outro')
CREATE TABLE IF NOT EXISTS materials (
    id                 INTEGER PRIMARY KEY,
    kind               TEXT NOT NULL DEFAULT 'filamento' CHECK (kind IN ('filamento', 'outro')),
    brand              TEXT,
    material_type      TEXT NOT NULL,                       -- PLA, PETG, ABS, TPU...
    color              TEXT,
    initial_weight_g   REAL NOT NULL CHECK (initial_weight_g > 0),
    available_weight_g REAL NOT NULL DEFAULT 0 CHECK (available_weight_g >= 0),
    spool_price_cents  INTEGER NOT NULL DEFAULT 0 CHECK (spool_price_cents >= 0),
    supplier_id        INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    purchase_date      TEXT,
    min_stock_g        REAL NOT NULL DEFAULT 0 CHECK (min_stock_g >= 0),
    is_active          INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_materials_supplier ON materials(supplier_id);

CREATE VIEW IF NOT EXISTS v_materials AS
SELECT m.*,
       m.spool_price_cents * 1.0 / m.initial_weight_g AS cost_per_gram_cents,
       CASE WHEN m.available_weight_g <= m.min_stock_g THEN 1 ELSE 0 END AS is_low_stock
FROM materials m;

CREATE TABLE IF NOT EXISTS printers (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    manufacturer        TEXT,
    model               TEXT,
    acquired_at         TEXT,
    value_cents         INTEGER NOT NULL DEFAULT 0 CHECK (value_cents >= 0),
    power_w             INTEGER NOT NULL DEFAULT 0 CHECK (power_w >= 0),
    hours_accumulated   REAL NOT NULL DEFAULT 0 CHECK (hours_accumulated >= 0),
    status              TEXT NOT NULL DEFAULT 'disponivel'
        CHECK (status IN ('disponivel', 'imprimindo', 'manutencao', 'inativa')),
    last_maintenance_at TEXT,
    next_maintenance_at TEXT,
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS maintenance_records (
    id           INTEGER PRIMARY KEY,
    printer_id   INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    performed_at TEXT NOT NULL,
    description  TEXT NOT NULL,
    cost_cents   INTEGER NOT NULL DEFAULT 0 CHECK (cost_cents >= 0),
    next_due_at  TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_maintenance_printer ON maintenance_records(printer_id, performed_at);

-- ---------------------------------------------------------------------
-- ORÇAMENTOS
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS quotes (
    id              INTEGER PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,                  -- gerado pelo app, ex.: ORC-2026-0001
    customer_id     INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    status          TEXT NOT NULL DEFAULT 'novo'
        CHECK (status IN ('novo', 'em_analise', 'enviado', 'aguardando_resposta',
                          'aprovado', 'recusado', 'expirado')),
    valid_until     TEXT,
    lead_time_days  INTEGER CHECK (lead_time_days IS NULL OR lead_time_days >= 0),
    subtotal_cents  INTEGER NOT NULL DEFAULT 0 CHECK (subtotal_cents >= 0),
    discount_cents  INTEGER NOT NULL DEFAULT 0 CHECK (discount_cents >= 0),
    total_cents     INTEGER NOT NULL DEFAULT 0 CHECK (total_cents >= 0),
    notes           TEXT,
    created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (discount_cents <= subtotal_cents)
);

CREATE INDEX IF NOT EXISTS idx_quotes_customer ON quotes(customer_id);
CREATE INDEX IF NOT EXISTS idx_quotes_status   ON quotes(status);

CREATE TABLE IF NOT EXISTS quote_items (
    id               INTEGER PRIMARY KEY,
    quote_id         INTEGER NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    product_id       INTEGER REFERENCES products(id) ON DELETE SET NULL,
    description      TEXT NOT NULL,
    customization    TEXT,
    quantity         INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL DEFAULT 0 CHECK (unit_price_cents >= 0),
    unit_cost_cents  INTEGER NOT NULL DEFAULT 0 CHECK (unit_cost_cents >= 0),
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_quote_items_quote ON quote_items(quote_id);

-- ---------------------------------------------------------------------
-- PEDIDOS
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY,
    number          TEXT NOT NULL UNIQUE,                  -- gerado pelo app, ex.: PED-2026-0001
    customer_id     INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    quote_id        INTEGER REFERENCES quotes(id) ON DELETE SET NULL,
    status          TEXT NOT NULL DEFAULT 'recebido'
        CHECK (status IN ('recebido', 'aguardando_confirmacao', 'aguardando_producao',
                          'em_producao', 'em_acabamento', 'pronto_entrega',
                          'entregue', 'cancelado')),
    payment_method  TEXT
        CHECK (payment_method IS NULL OR payment_method IN
               ('pix', 'dinheiro', 'cartao_credito', 'cartao_debito',
                'boleto', 'transferencia', 'outro')),
    delivery_due    TEXT,
    subtotal_cents  INTEGER NOT NULL DEFAULT 0 CHECK (subtotal_cents >= 0),
    discount_cents  INTEGER NOT NULL DEFAULT 0 CHECK (discount_cents >= 0),
    total_cents     INTEGER NOT NULL DEFAULT 0 CHECK (total_cents >= 0),
    notes           TEXT,
    created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (discount_cents <= subtotal_cents)
);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status   ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created  ON orders(created_at);
-- Um orçamento só pode virar pedido uma vez
CREATE UNIQUE INDEX IF NOT EXISTS uq_orders_quote ON orders(quote_id) WHERE quote_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS order_items (
    id               INTEGER PRIMARY KEY,
    order_id         INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id       INTEGER REFERENCES products(id) ON DELETE SET NULL,
    description      TEXT NOT NULL,
    customization    TEXT,
    quantity         INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL DEFAULT 0 CHECK (unit_price_cents >= 0),
    unit_cost_cents  INTEGER NOT NULL DEFAULT 0 CHECK (unit_cost_cents >= 0),  -- custo no momento da venda
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_order_items_order   ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

CREATE TABLE IF NOT EXISTS order_status_history (
    id          INTEGER PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    from_status TEXT,
    to_status   TEXT NOT NULL,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    note        TEXT,
    changed_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_order_history_order ON order_status_history(order_id, changed_at);

-- ---------------------------------------------------------------------
-- PRODUÇÃO
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS production_orders (
    id                INTEGER PRIMARY KEY,
    code              TEXT NOT NULL UNIQUE,                -- gerado pelo app, ex.: OP-2026-0001
    order_id          INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    order_item_id     INTEGER REFERENCES order_items(id) ON DELETE SET NULL,
    product_id        INTEGER REFERENCES products(id) ON DELETE SET NULL,
    printer_id        INTEGER REFERENCES printers(id) ON DELETE SET NULL,
    material_id       INTEGER REFERENCES materials(id) ON DELETE SET NULL,
    status            TEXT NOT NULL DEFAULT 'fila'
        CHECK (status IN ('fila', 'em_andamento', 'concluida', 'falhou', 'cancelada')),
    estimated_weight_g REAL CHECK (estimated_weight_g IS NULL OR estimated_weight_g >= 0),
    consumed_weight_g  REAL CHECK (consumed_weight_g IS NULL OR consumed_weight_g >= 0),
    estimated_minutes  INTEGER CHECK (estimated_minutes IS NULL OR estimated_minutes >= 0),
    actual_minutes     INTEGER CHECK (actual_minutes IS NULL OR actual_minutes >= 0),
    started_at        TEXT,
    finished_at       TEXT,
    waste_g           REAL NOT NULL DEFAULT 0 CHECK (waste_g >= 0),
    failure_notes     TEXT,
    notes             TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (started_at IS NULL OR finished_at IS NULL OR finished_at >= started_at)
);

CREATE INDEX IF NOT EXISTS idx_production_status   ON production_orders(status);
CREATE INDEX IF NOT EXISTS idx_production_order    ON production_orders(order_id);
CREATE INDEX IF NOT EXISTS idx_production_printer  ON production_orders(printer_id);
CREATE INDEX IF NOT EXISTS idx_production_material ON production_orders(material_id);

CREATE TABLE IF NOT EXISTS production_logs (
    id                  INTEGER PRIMARY KEY,
    production_order_id INTEGER NOT NULL REFERENCES production_orders(id) ON DELETE CASCADE,
    event_type          TEXT NOT NULL DEFAULT 'observacao'
        CHECK (event_type IN ('inicio', 'pausa', 'retomada', 'falha', 'conclusao', 'observacao')),
    notes               TEXT,
    waste_g             REAL NOT NULL DEFAULT 0 CHECK (waste_g >= 0),
    user_id             INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_production_logs_order ON production_logs(production_order_id, created_at);

-- ---------------------------------------------------------------------
-- MOVIMENTAÇÕES DE ESTOQUE
-- quantity_g tem SINAL: entrada > 0, saída < 0, ajuste ≠ 0.
-- O saldo em materials.available_weight_g é atualizado por trigger.
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS inventory_movements (
    id                  INTEGER PRIMARY KEY,
    material_id         INTEGER NOT NULL REFERENCES materials(id) ON DELETE RESTRICT,
    type                TEXT NOT NULL CHECK (type IN ('entrada', 'saida', 'ajuste')),
    reason              TEXT NOT NULL DEFAULT 'outro'
        CHECK (reason IN ('compra', 'producao', 'perda', 'ajuste', 'outro')),
    quantity_g          REAL NOT NULL,
    production_order_id INTEGER REFERENCES production_orders(id) ON DELETE RESTRICT,
    supplier_id         INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    notes               TEXT,
    user_id             INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (
        (type = 'entrada' AND quantity_g > 0) OR
        (type = 'saida'   AND quantity_g < 0) OR
        (type = 'ajuste'  AND quantity_g <> 0)
    ),
    CHECK (reason <> 'producao' OR production_order_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_inventory_material ON inventory_movements(material_id, created_at);

-- Proteção contra baixa duplicada: uma baixa de produção por ordem e material
CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_production
    ON inventory_movements(production_order_id, material_id)
    WHERE reason = 'producao';

-- ---------------------------------------------------------------------
-- FINANCEIRO
-- Contas a pagar    = type 'despesa' com status 'pendente'
-- Contas a receber  = type 'receita' com status 'pendente'
-- Faturado          = competence_date  |  Recebido = status 'pago' + paid_date
-- Lançamentos de pedido cancelado devem ficar com status 'cancelado'.
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_transactions (
    id              INTEGER PRIMARY KEY,
    type            TEXT NOT NULL CHECK (type IN ('receita', 'despesa')),
    category        TEXT,
    description     TEXT NOT NULL,
    amount_cents    INTEGER NOT NULL CHECK (amount_cents > 0),
    cost_nature     TEXT CHECK (cost_nature IS NULL OR cost_nature IN ('fixo', 'variavel')),
    status          TEXT NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'pago', 'cancelado')),
    competence_date TEXT NOT NULL DEFAULT (date('now')),
    due_date        TEXT,
    paid_date       TEXT,
    payment_method  TEXT,
    order_id        INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    customer_id     INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    supplier_id     INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    notes           TEXT,
    created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (type = 'despesa' OR cost_nature IS NULL),
    CHECK (status <> 'pago' OR paid_date IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_fin_type_status ON financial_transactions(type, status);
CREATE INDEX IF NOT EXISTS idx_fin_competence  ON financial_transactions(competence_date);
CREATE INDEX IF NOT EXISTS idx_fin_due         ON financial_transactions(due_date);
CREATE INDEX IF NOT EXISTS idx_fin_order       ON financial_transactions(order_id);

-- ---------------------------------------------------------------------
-- TAREFAS
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    due_date    TEXT,
    priority    TEXT NOT NULL DEFAULT 'media' CHECK (priority IN ('baixa', 'media', 'alta')),
    status      TEXT NOT NULL DEFAULT 'pendente'
        CHECK (status IN ('pendente', 'em_andamento', 'concluida', 'cancelada')),
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    order_id    INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, due_date);

-- =====================================================================
-- TRIGGERS
-- =====================================================================

-- Histórico automático de status do pedido
CREATE TRIGGER IF NOT EXISTS trg_orders_status_insert
AFTER INSERT ON orders
BEGIN
    INSERT INTO order_status_history (order_id, from_status, to_status)
    VALUES (NEW.id, NULL, NEW.status);
END;

CREATE TRIGGER IF NOT EXISTS trg_orders_status_update
AFTER UPDATE OF status ON orders
WHEN OLD.status <> NEW.status
BEGIN
    INSERT INTO order_status_history (order_id, from_status, to_status)
    VALUES (NEW.id, OLD.status, NEW.status);
END;

-- Saldo do estoque
CREATE TRIGGER IF NOT EXISTS trg_inventory_apply
AFTER INSERT ON inventory_movements
BEGIN
    UPDATE materials
       SET available_weight_g = available_weight_g + NEW.quantity_g
     WHERE id = NEW.material_id;
END;

-- Movimentações são imutáveis: para corrigir, crie um ajuste
CREATE TRIGGER IF NOT EXISTS trg_inventory_no_update
BEFORE UPDATE ON inventory_movements
BEGIN
    SELECT RAISE(ABORT, 'Movimentações de estoque não podem ser alteradas. Crie um ajuste.');
END;

CREATE TRIGGER IF NOT EXISTS trg_inventory_no_delete
BEFORE DELETE ON inventory_movements
BEGIN
    SELECT RAISE(ABORT, 'Movimentações de estoque não podem ser apagadas. Crie um ajuste.');
END;

-- updated_at automático
CREATE TRIGGER IF NOT EXISTS trg_users_updated AFTER UPDATE ON users
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE users SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_company_settings_updated AFTER UPDATE ON company_settings
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE company_settings SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_pricing_settings_updated AFTER UPDATE ON pricing_settings
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE pricing_settings SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_marketing_campaigns_updated AFTER UPDATE ON marketing_campaigns
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE marketing_campaigns SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_marketing_posts_updated AFTER UPDATE ON marketing_posts
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE marketing_posts SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_customers_updated AFTER UPDATE ON customers
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE customers SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_categories_updated AFTER UPDATE ON categories
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE categories SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_products_updated AFTER UPDATE ON products
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE products SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_suppliers_updated AFTER UPDATE ON suppliers
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE suppliers SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_materials_updated AFTER UPDATE ON materials
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE materials SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_printers_updated AFTER UPDATE ON printers
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE printers SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_quotes_updated AFTER UPDATE ON quotes
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE quotes SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_orders_updated AFTER UPDATE ON orders
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE orders SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_production_orders_updated AFTER UPDATE ON production_orders
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE production_orders SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_financial_transactions_updated AFTER UPDATE ON financial_transactions
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE financial_transactions SET updated_at = datetime('now') WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS trg_tasks_updated AFTER UPDATE ON tasks
WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE tasks SET updated_at = datetime('now') WHERE id = NEW.id; END;