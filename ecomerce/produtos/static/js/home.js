const input = document.getElementById('inp-produtos')
const produtos = document.querySelectorAll('#produtos > div')

input.addEventListener('input', () => {
    const busca = input.value.toLowerCase().trim()

    produtos.forEach(produto => {
        const nome = produto
            .querySelector('h2')
            .textContent
            .toLowerCase()

        if (nome.includes(busca)) {
            produto.style.display = ''
        } else {
            produto.style.display = 'none'
        }
    })
})