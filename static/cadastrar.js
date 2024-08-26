document.addEventListener('DOMContentLoaded', function() {
    // Função para carregar a lista de usuários
    function carregarUsuarios() {
        fetch('/obter_usuarios')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const tbody = document.getElementById('usuarios-table').querySelector('tbody');
                    tbody.innerHTML = ''; // Limpar a tabela antes de adicionar novos usuários
                    data.usuarios.forEach(usuario => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${usuario.id}</td>
                            <td>${usuario.nome}</td>
                            <td>${usuario.email}</td>
                            <td>${new Date(usuario.data_cadastro).toLocaleDateString()}</td>
                        `;
                        tbody.appendChild(row);
                        location.reload(); // Recarregar a página para atualizar a lista de usuários
                    });
                } else {
                    alert('Erro ao carregar usuários.');
                }
            })
            .catch(error => console.error('Erro:', error));
    }

    // Função para mostrar o formulário de cadastro
    window.mostrarFormularioCadastro = function() {
        document.getElementById('cadastro-container').style.display = 'block';
    }

    // Função para cancelar o cadastro
    window.cancelarCadastro = function() {
        document.getElementById('cadastro-container').style.display = 'none';
    }

    // Evento de submissão do formulário de cadastro
    document.getElementById('cadastro-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch('/cadastrar_usuario', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Usuário cadastrado com sucesso!');
                cancelarCadastro();
                carregarUsuarios(); // Atualizar a lista de usuários
            } else {
                alert('Erro ao cadastrar usuário: ' + data.message);
            }
        })
        .catch(error => console.error('Erro:', error));
    });

    // Carregar a lista de usuários ao carregar a página
    carregarUsuarios();

    // Configurar o EventSource para ouvir eventos de atualização do servidor
    const eventSource = new EventSource('/stream');
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.message === 'update') {
            carregarUsuarios(); // Atualizar a lista de usuários
        }
    };
});