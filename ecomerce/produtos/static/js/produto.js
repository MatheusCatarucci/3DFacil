/* ============================================================
   produto.js — expansão dos cards e galeria de fotos

   Duas responsabilidades:

     1. Abrir e fechar os detalhes do produto quando o card é
        clicado. O botão "Comprar" nunca dispara a abertura.

     2. Fazer as setas alternarem entre as fotos dentro do card
        expandido. Com uma foto só, as setas nem são renderizadas.

   Só alterna classes; o layout é resolvido pelo CSS.
   ============================================================ */

(function () {
    'use strict';

    /* ----------------------------------------------------
       1. EXPANDIR / FECHAR O CARD
    ---------------------------------------------------- */

    const cards = document.querySelectorAll('[data-cartao]');

    cards.forEach(function (card) {
        const botaoExpandir = card.querySelector('[data-expandir]');
        const detalhe = card.querySelector('[data-detalhe]');
        const seta = card.querySelector('[data-seta]');

        if (!detalhe) return;

        function definir(estado) {
            card.classList.toggle('aberto', estado);
            botaoExpandir?.setAttribute('aria-expanded', estado ? 'true' : 'false');

            if (seta) {
                // Gira a seta para indicar o estado.
                seta.style.transform = estado ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        }

        function alternar() {
            definir(!card.classList.contains('aberto'));
        }

        /*
            O botão cobre a imagem, o nome e o preço. O handler do
            card cuida das bordas e dos espaços vazios do card, por
            isso ele ignora cliques que já vieram do botão.
        */
        botaoExpandir?.addEventListener('click', alternar);

        card.addEventListener('click', function (evento) {
            // Botão Comprar: não abre nada.
            if (evento.target.closest('[data-comprar]')) return;

            // Já tratado pelo botão da área clicável.
            if (evento.target.closest('[data-expandir]')) return;

            // Dentro da galeria as setas cuidam do próprio clique.
            if (evento.target.closest('[data-galeria]')) return;

            alternar();
        });

        card.dataset.estado = 'fechado';
    });

    /* ----------------------------------------------------
       FECHA COM ESC
    ---------------------------------------------------- */

    document.addEventListener('keydown', function (evento) {
        if (evento.key !== 'Escape') return;

        document.querySelectorAll('[data-cartao].aberto').forEach(function (card) {
            const botao = card.querySelector('[data-expandir]');
            const seta = card.querySelector('[data-seta]');

            card.classList.remove('aberto');
            botao?.setAttribute('aria-expanded', 'false');

            if (seta) seta.style.transform = 'rotate(0deg)';
        });
    });


    /* ----------------------------------------------------
       2. GALERIA DE FOTOS
    ---------------------------------------------------- */

    document.querySelectorAll('[data-galeria]').forEach(function (galeria) {
        const fotos = Array.from(galeria.querySelectorAll('[data-foto]'));
        const contador = galeria.querySelector('[data-contador]');
        const anterior = galeria.querySelector('[data-anterior]');
        const proxima = galeria.querySelector('[data-proxima]');

        if (!fotos.length) return;

        let atual = 0;

        function mostrar(indice) {
            // O % mantém o ciclo: da última volta para a primeira.
            atual = (indice + fotos.length) % fotos.length;

            fotos.forEach(function (foto, i) {
                foto.classList.toggle('hidden', i !== atual);
            });

            if (contador) {
                contador.textContent = (atual + 1) + ' / ' + fotos.length;
            }
        }

        anterior?.addEventListener('click', function () {
            mostrar(atual - 1);
        });

        proxima?.addEventListener('click', function () {
            mostrar(atual + 1);
        });

        mostrar(0);
    });
})();