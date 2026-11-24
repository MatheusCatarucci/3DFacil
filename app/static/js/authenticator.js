const formulario = document.getElementById("form-login")
const email = document.getElementById("email")
const senha = document.getElementById("senha")
const btn_login = document.getElementById("btn-login")

let temporizadorNotificacao


formulario.addEventListener("submit", (evento) => {
    evento.preventDefault()

    const email_value = email.value
    const senha_value = senha.value

    entrarNoSistema(email_value, senha_value)
})


async function entrarNoSistema(email, senha) {

    btn_login.disabled = true

    try {
        const consulta = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                senha
            })
        })

        if (consulta.status === 200) {
            window.location.href = "/dashboard"
            return
        }

        if (consulta.status === 401) {
            mostrarNotificacao(
                "Erro na autenticação",
                "E-mail ou senha incorretos."
            )
            return
        }

        mostrarNotificacao(
            "Erro inesperado",
            "Não foi possível realizar o login."
        )

    } catch (erro) {
        mostrarNotificacao(
            "Erro de conexão",
            "Não foi possível conectar ao servidor."
        )

    } finally {
        btn_login.disabled = false
    }
}


function mostrarNotificacao(titulo, mensagem) {

    const notificacao = document.getElementById("notificacao")

    document.getElementById("notificacao-titulo").textContent = titulo
    document.getElementById("notificacao-mensagem").textContent = mensagem

    clearTimeout(temporizadorNotificacao)

    notificacao.classList.add("ativa")

    temporizadorNotificacao = setTimeout(() => {
        notificacao.classList.remove("ativa")
    }, 4000)
}


document.getElementById("fechar-notificacao").addEventListener("click", () => {

    document.getElementById("notificacao").classList.remove("ativa")

    clearTimeout(temporizadorNotificacao)
})