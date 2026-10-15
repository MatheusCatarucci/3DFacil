/* ============================================================
   ui.js — menu mobile, notificações e respostas das interações

   Quatro coisas:

     1. Abrir e fechar o menu no celular, com as três barras
        virando um X e os links entrando em cascata.

     2. Mostrar avisos temporários (notificações) no canto da
        tela, usados pelo carrinho.

     3. Adicionar ao carrinho sem recarregar a página, chamando
        a view por fetch e atualizando o total do menu.

     4. Mostrar que um formulário comum está sendo enviado.

   Tudo respeita prefers-reduced-motion.
   ============================================================ */

(function () {
    'use strict';

    const semMovimento = window.matchMedia(
        '(prefers-reduced-motion: reduce)'
    ).matches;

    /* ----------------------------------------------------
       1. MENU MOBILE
    ---------------------------------------------------- */

    const botaoMenu = document.querySelector('[data-menu-botao]');
    const menu = document.getElementById('menu-mobile');

    if (botaoMenu && menu) {
        /*
            Abrir e fechar passam sempre por aqui. Antes cada
            caminho (botao, clique fora, Esc) mexia no aria-label
            por conta propria e um deles ficava para tras: ao
            fechar pelo Esc, o botao continuava anunciado como
            "Fechar menu" mesmo ja estando fechado.
        */
        function definirMenu(aberto) {
            menu.classList.toggle('aberto', aberto);

            botaoMenu.setAttribute('aria-expanded', aberto ? 'true' : 'false');
            botaoMenu.setAttribute(
                'aria-label',
                aberto ? 'Fechar menu' : 'Abrir menu'
            );
        }

        botaoMenu.addEventListener('click', function () {
            definirMenu(!menu.classList.contains('aberto'));
        });

        // Clicar em um link fecha o menu antes de navegar.
        menu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                definirMenu(false);
            });
        });

        // Clicar fora fecha.
        document.addEventListener('click', function (evento) {
            if (!menu.classList.contains('aberto')) return;
            if (menu.contains(evento.target)) return;
            if (botaoMenu.contains(evento.target)) return;

            definirMenu(false);
        });

        // Esc fecha.
        document.addEventListener('keydown', function (evento) {
            if (evento.key !== 'Escape') return;
            if (!menu.classList.contains('aberto')) return;

            definirMenu(false);
            botaoMenu.focus();
        });
    }


    /* ----------------------------------------------------
       2. NOTIFICACOES (TOAST)
    ---------------------------------------------------- */

    const area = document.getElementById('notificacoes');

    function notificar(mensagem, tipo) {
        if (!area) return;

        const aviso = document.createElement('div');
        const estilo = tipo === 'erro' ? 'erro' : 'sucesso';

        aviso.className = 'notificacao notificacao-' + estilo;
        aviso.setAttribute('role', 'status');

        const icone = document.createElement('span');
        icone.className = 'notificacao-icone';
        icone.textContent = estilo === 'erro' ? '!' : '✓';

        const texto = document.createElement('span');
        texto.textContent = mensagem;

        const fechar = document.createElement('button');
        fechar.type = 'button';
        fechar.className = 'notificacao-fechar';
        fechar.setAttribute('aria-label', 'Fechar aviso');
        fechar.textContent = '×';

        aviso.append(icone, texto, fechar);
        area.appendChild(aviso);

        /*
            A entrada precisa de um quadro antes: o primeiro pinta
            o aviso ja na posicao final (opacity 0, deslocado) e
            so no segundo a classe entra e a transicao roda.
        */
        requestAnimationFrame(function () {
            aviso.classList.add('entrando');
        });

        let removido = false;

        function dispensar() {
            if (removido) return;
            removido = true;

            aviso.classList.remove('entrando');
            aviso.classList.add('saindo');

            aviso.addEventListener('transitionend', function () {
                aviso.remove();
            });
            setTimeout(function () {
                aviso.remove();
            }, 450);
        }

        fechar.addEventListener('click', dispensar);
        setTimeout(dispensar, 4000);
    }


    /* ----------------------------------------------------
       3. TOTAL DO CARRINHO NO MENU
    ---------------------------------------------------- */

    function atualizarTotal(total) {
        document.querySelectorAll('[data-total-carrinho]').forEach(function (elemento) {
            const numero = parseInt(total, 10) || 0;

            elemento.textContent = numero;

            // O badge some quando o carrinho zera.
            const caixa = elemento.closest('[data-caixa-badge]');
            if (caixa) {
                caixa.hidden = numero === 0;
            }
        });
    }


    /* ----------------------------------------------------
       4. ADICIONAR AO CARRINHO SEM RECARREGAR
    ---------------------------------------------------- */

    /*
        Os botoes Comprar nao mudam de pagina: chamam a view por
        fetch e mostram o retorno como notificacao.

        Sem JavaScript, o form continua fazendo POST normal e a
        view redireciona para o carrinho. O botao funciona nos
        dois casos.
    */

    document
        .querySelectorAll('form[action*="/carrinho/adicionar/"]')
        .forEach(function (form) {
            form.addEventListener('submit', function (evento) {
                evento.preventDefault();

                // Trava contra clique duplo.
                if (form.dataset.enviando === 'sim') return;

                const botao = form.querySelector('button[type="submit"]');
                const token = form.querySelector('[name="csrfmiddlewaretoken"]');

                if (!token) return;

                form.dataset.enviando = 'sim';

                const textoOriginal = botao ? botao.textContent.trim() : '';

                if (botao) botao.classList.add('enviando');

                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': token.value,
                    },
                })
                    .then(function (resposta) {
                        return resposta.json().then(function (corpo) {
                            return { ok: resposta.ok, corpo: corpo };
                        });
                    })
                    .then(function (resultado) {
                        notificar(
                            resultado.corpo.mensagem,
                            resultado.ok ? 'sucesso' : 'erro'
                        );

                        if (resultado.corpo.total_itens !== undefined) {
                            atualizarTotal(resultado.corpo.total_itens);
                        }

                        if (resultado.ok && botao) {
                            // Em vez de voltar ao estado inicial,
                            // o botao confirma que ja esta no
                            // carrinho.
                            botao.textContent = 'No carrinho ✓';
                        } else if (botao) {
                            botao.classList.remove('enviando');
                            botao.textContent = textoOriginal;
                        }
                    })
                    .catch(function () {
                        notificar('Não foi possível adicionar.', 'erro');

                        if (botao) {
                            botao.classList.remove('enviando');
                            botao.textContent = textoOriginal;
                        }
                    })
                    .then(function () {
                        delete form.dataset.enviando;
                    });
            });
        });


    /* ----------------------------------------------------
       5. FORMULARIOS COMUNS ENVIANDO
    ---------------------------------------------------- */

    /*
        Atualizar quantidade, remover e esvaziar continuam com
        POST normal: a pessoa ja esta na pagina do carrinho e ver
        a lista recarregar e o comportamento esperado.

        O estado visual evita o duplo clique e da retorno de que
        o pedido saiu.
    */

    document
        .querySelectorAll('form[action*="/carrinho/"]')
        .forEach(function (form) {
            // O submit das forms de adicionar ja foi tratado acima.
            if (form.action.includes('/carrinho/adicionar/')) return;

            form.addEventListener('submit', function () {
                const botao = form.querySelector('button[type="submit"]');

                if (!botao || botao.dataset.enviando === 'sim') return;

                botao.dataset.enviando = 'sim';
                botao.classList.add('enviando');

                // Guarda o texto antes de trocar pelo spinner, para
                // o caso de a pagina voltar do cache do navegador.
                botao.dataset.texto = botao.textContent.trim();

                if (semMovimento) return;

                botao.textContent = '';

                const spinner = document.createElement('span');
                spinner.className = 'girando';

                botao.appendChild(spinner);
            });
        });


    /* ----------------------------------------------------
       6. MOVIMENTO REDUZIDO
    ---------------------------------------------------- */

    if (semMovimento) {
        document.querySelectorAll('.carrinho-badge').forEach(function (badge) {
            badge.classList.remove('carrinho-badge');
        });
    }
})();