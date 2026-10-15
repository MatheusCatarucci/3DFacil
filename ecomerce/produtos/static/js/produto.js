/* ============================================================
   produto.js — modal do produto em tela cheia

   Um unico modal no fim da pagina, reaproveitado por qualquer
   card. Os dados de cada produto chegam em uma tag
   <script type="application/json"> (json_script do Django), que
   e lida e transformada em objeto aqui.

   Fecha de tres formas: no X, no fundo desfocado ou no Esc.
   ============================================================ */

(function () {
    'use strict';

    const modal = document.getElementById('modal-produto');

    if (!modal) return;

    const fundo = modal.querySelector('.modal-fundo');
    const botaoFechar = modal.querySelector('[data-fechar]');
    const imgGaleria = modal.querySelector('[data-galeria-img]');
    const contador = modal.querySelector('[data-galeria-contador]');
    const setaAnterior = modal.querySelector('[data-galeria-anterior]');
    const setaProxima = modal.querySelector('[data-galeria-proxima]');
    const formModal = modal.querySelector('[data-modal-form]');

    const campoNome = modal.querySelector('[data-modal-nome]');
    const campoPreco = modal.querySelector('[data-modal-preco]');
    const campoDescricao = modal.querySelector('[data-modal-descricao]');
    const campoCodigo = modal.querySelector('[data-modal-codigo]');
    const campoEstoque = modal.querySelector('[data-modal-estoque]');
    const campoEstoqueValor = modal.querySelector('[data-modal-estoque-valor]');

    let fotos = [];
    let indice = 0;
    let cardAnterior = null;

    /* ----------------------------------------------------
       GALERIA
    ---------------------------------------------------- */

    function mostrarFoto(nova) {
        if (!fotos.length) return;

        // O % faz o ciclo: da ultima volta para a primeira.
        indice = (nova + fotos.length) % fotos.length;

        const foto = fotos[indice];

        imgGaleria.src = foto.src;
        imgGaleria.alt = foto.legenda || '';

        contador.textContent = (indice + 1) + ' / ' + fotos.length;
    }

    setaAnterior.addEventListener('click', function () {
        mostrarFoto(indice - 1);
    });

    setaProxima.addEventListener('click', function () {
        mostrarFoto(indice + 1);
    });

    /* ----------------------------------------------------
       ABRIR E FECHAR
    ---------------------------------------------------- */

    function abrir(card) {
        cardAnterior = card;

        // Os dados de todos os produtos ficam em uma unica tag JSON,
        // indexados pelo id. Aqui pegamos o deste card.
        const container = document.getElementById('dados-produtos');

        if (!container) return;

        const todos = JSON.parse(container.textContent);
        const dados = todos[card.dataset.produtoId];

        if (!dados) return;

        fotos = dados.fotos || [];
        indice = 0;

        // Sem foto cadastrada, mostra a imagem padrao do site.
        if (fotos.length) {
            mostrarFoto(0);
        } else {
            imgGaleria.src = '/static/img/bulldog_cube.png';
            imgGaleria.alt = dados.nome;
            contador.textContent = '';
        }

        // Com uma foto so, as setas ficam escondidas.
        const varias = fotos.length > 1;
        setaAnterior.hidden = !varias;
        setaProxima.hidden = !varias;
        contador.hidden = !varias;

        campoNome.textContent = dados.nome;
        campoPreco.textContent = 'R$ ' + Number(dados.preco).toFixed(2).replace('.', ',');
        campoDescricao.textContent = dados.descricao || '';
        campoDescricao.hidden = !dados.descricao;
        campoCodigo.textContent = '#' + String(dados.id).padStart(4, '0');
        campoEstoqueValor.textContent = dados.estoque;

        campoEstoque.textContent = dados.estoque > 0
            ? 'Em estoque'
            : 'Produto esgotado';

        formModal.action = '/carrinho/adicionar/' + dados.id + '/';
        formModal.hidden = dados.estoque <= 0;

        modal.hidden = false;
        modal.classList.add('modal-aberto');

        // Trava o scroll do fundo enquanto o modal esta aberto.
        document.body.style.overflow = 'hidden';
        botaoFechar.focus();
    }

    function fechar() {
        modal.classList.remove('modal-aberto');
        modal.hidden = true;
        document.body.style.overflow = '';

        // Devolve o foco para o card que foi aberto.
        cardAnterior?.querySelector('[data-abrir-modal]')?.focus();
        cardAnterior = null;
    }

    /* ----------------------------------------------------
       EVENTOS
    ---------------------------------------------------- */

    document.querySelectorAll('[data-abrir-modal]').forEach(function (botao) {
        botao.addEventListener('click', function () {
            abrir(botao.closest('[data-produto-id]'));
        });
    });

    modal.querySelectorAll('[data-fechar]').forEach(function (elemento) {
        elemento.addEventListener('click', fechar);
    });

    // Setas do teclado dentro do modal.
    document.addEventListener('keydown', function (evento) {
        if (modal.hidden) return;

        if (evento.key === 'Escape') {
            fechar();
        } else if (evento.key === 'ArrowLeft') {
            mostrarFoto(indice - 1);
        } else if (evento.key === 'ArrowRight') {
            mostrarFoto(indice + 1);
        }
    });
})();