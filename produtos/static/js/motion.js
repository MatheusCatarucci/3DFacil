/* ============================================================
   motion.js — animação de entrada da página

   Uma única responsabilidade:

     Adicionar .reveal nos blocos de conteúdo e trocar por
     .is-visible quando eles entram na tela, com um pequeno
     atraso entre cada um (efeito cascata).

   Não altera o layout: apenas adiciona classes.
   ============================================================ */

(function () {
    'use strict';

    // Respeita quem pediu menos movimento no sistema.
    const semMovimento = window.matchMedia(
        '(prefers-reduced-motion: reduce)'
    ).matches;

    /* ----------------------------------------------------
       1. REVELAR AO ROLAR
    ---------------------------------------------------- */

    // Blocos que entram em cena. Os seletores batem com o HTML
    // atual, entao nenhuma mudanca de markup e necessaria.
    const seletores = [
        'header > div',
        'main h1',
        'main h1 + p',
        '#produtos > div',
        'main section > p',
        'footer > div',
        'footer > div:last-child'
    ];

    const alvos = [];

    seletores.forEach((seletor) => {
        document.querySelectorAll(seletor).forEach((elemento) => {
            if (!alvos.includes(elemento)) {
                alvos.push(elemento);
            }
        });
    });

    // Sem IntersectionObserver ou sem movimento desejado,
    // mostra tudo de uma vez.
    if (semMovimento || !('IntersectionObserver' in window)) {
        return;
    }

    /*
        Marca o documento antes de esconder qualquer bloco. O CSS so
        aplica opacity:0 em .motion-ready .reveal, entao se algo
        falhar entre esta linha e o observer, o conteudo aparece
        normalmente em vez de ficar invisivel.
    */
    document.documentElement.classList.add('motion-ready');

    let indice = 0;

    alvos.forEach((elemento) => {
        elemento.classList.add('reveal');

        // Cascata: cada bloco atrasa um pouco o anterior.
        const atraso = Math.min(indice * 70, 420);
        elemento.style.transitionDelay = atraso + 'ms';

        indice += 1;
    });

    const observer = new IntersectionObserver(
        (entradas) => {
            entradas.forEach((entrada) => {
                if (entrada.isIntersecting) {
                    entrada.target.classList.add('is-visible');
                    // Depois de aparecer, nao observa mais: evita
                    // a animacao repetir a cada rolagem.
                    observer.unobserve(entrada.target);
                }
            });
        },
        {
            /*
                threshold baixo e sem rootMargin negativo.

                Isso parece bobagem, mas um rootMargin negativo no
                fundo trava de vez elementos colados no fim da
                pagina: o copyright do footer tem poucas linhas, a
                pagina nao rola o suficiente para ele entrar na
                faixa encolhida e ficaria invisivel para sempre.
            */
            threshold: 0.05,
            rootMargin: '0px'
        }
    );

    alvos.forEach((elemento) => observer.observe(elemento));
})();