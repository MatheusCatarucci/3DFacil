const input_buscar = document.getElementById('buscar_input')
const btn_buscar = document.getElementById('buscar_btn')
const cards_produtos = document.querySelectorAll('.card_produto')
const nomes_produtos = document.querySelectorAll('.nome_produto')

btn_buscar.addEventListener('click', () => {
    const input_value = input_buscar.value.toLowerCase().trim()

    for (let i = 0; i < nomes_produtos.length; i++) {
        const nome_produto = nomes_produtos[i].textContent.toLowerCase().trim()
        console.log(nome_produto)
        if ((nome_produto.includes(input_value))) {
            cards_produtos[i].style.display = 'flex'
        }
        else {
            cards_produtos[i].style.display = 'none'
        }
    }



})