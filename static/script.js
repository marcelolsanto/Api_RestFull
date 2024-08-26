function editarUsuario() {
    const id = document.getElementById('edit-id-input').value;

    // Fazer uma requisição ao servidor para obter os dados do usuário com o ID fornecido
    fetch('/obter_usuario/' + id)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Preencher o formulário de edição com os dados do usuário
                document.getElementById('edit-id').value = data.usuario.id;
                document.getElementById('edit-nome').value = data.usuario.nome;
                document.getElementById('edit-email').value = data.usuario.email;
                document.getElementById('edit-senha').value = data.usuario.senha;
                document.getElementById('edit-data-cadastro').value = data.usuario.data_cadastro;

                // Exibir o formulário de edição
                document.getElementById('edit-id-container').style.display = 'none';
                document.getElementById('form-container').style.display = 'block';
            } else {
                alert('Erro ao obter dados do usuário.');
            }
        })
        .catch(error => console.error('Erro:', error));
}

function mostrarFormularioEdicao() {
    document.getElementById('edit-id-container').style.display = 'block';
    document.getElementById('container').style.display = 'none';
}

function mostrarFormularioDeletar() {
    document.getElementById('delete-id-container').style.display = 'block';
    document.getElementById('container').style.display = 'none';
}

function cancelarDeletar() {
    document.getElementById('delete-id-container').style.display = 'none';
    document.getElementById('container').style.display = 'block';
}

function cancelarEdicao() {
    document.getElementById('form-container').style.display = 'none';
    document.getElementById('edit-id-container').style.display = 'none';
    document.getElementById('container').style.display = 'block';
}

document.getElementById('edit-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const id = document.getElementById('edit-id').value;
    const formData = new FormData(this);

    fetch('/atualizar_usuario/' + id, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Usuário atualizado com sucesso!');
            cancelarEdicao();
            location.reload(); // Recarregar a página para atualizar a lista de usuários
        } else {
            alert('Erro ao atualizar usuário.');
        }
    })
    .catch(error => console.error('Erro:', error));
});

function deletarUsuario() {
    const id = document.getElementById('delete-id-input').value;
    if (confirm('Tem certeza que deseja deletar este usuário?')) {
        fetch('/deletar_usuario/' + id, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Usuário deletado com sucesso!');
                cancelarDeletar();
                location.reload(); // Recarregar a página para atualizar a lista de usuários
            } else {
                alert('Erro ao deletar usuário.');
            }
        })
        .catch(error => console.error('Erro:', error));
    }
}
