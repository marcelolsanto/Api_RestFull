from flask import Flask, json, request, Response, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_migrate import Migrate
from models import db, Usuario
import time


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:#Gf71402730225@localhost/Bd_Liberacao'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.__init__(app)
migrate = Migrate(app, db)

# Rota para renderizar a página inicial
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def logar():
    return render_template('login.html')

# Rota de exemplo para cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

            # Validação básica dos dados (pode ser expandida conforme necessário)
            if not nome or not email or not senha:
                return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

            existing_user = Usuario.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'Email já cadastrado'}), 400

            novo_usuario = Usuario(nome=nome, email=email, senha=senha)
            db.session.add(novo_usuario)
            db.session.commit()
            return redirect(url_for('login'))

        except Exception as error:
            # Log do erro (opcional, mas útil para depuração)
            print(f"Erro ao cadastrar usuário: {error}")
            return jsonify({'error': 'Erro ao cadastrar usuário'}), 500
    return render_template('cadastro.html')

# Rota de exemplo para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            senha = request.form['senha']

            # Verifica se o email e a senha foram fornecidos
            if not email or not senha:
                return jsonify({'message': 'Email and password are required'}), 400

            usuario = Usuario.query.filter_by(email=email, senha=senha).first()
            if usuario:
                return redirect(url_for('usuarios'))
            else:
                return jsonify({'message': 'Invalid credentials'}), 401

        except KeyError:
            return jsonify({'message': 'Missing email or password field'}), 400
        except Exception as error:
            # Log do erro (opcional, mas útil para depuração)
            print(f"Erro ao fazer login: {error}")
            return jsonify({'message': 'An error occurred during login'}), 500
    return render_template('login.html')

# Rota para exibir usuários cadastrados
@app.route('/usuarios', methods=['GET'])
def usuarios():
    # Usando db.session.execute para obter todos os usuários
    usuarios = db.session.execute(db.select(Usuario)).scalars().all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/deletar_usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    usuario = db.session.get(Usuario, id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return render_template('usuarios.html')
    else:
        return jsonify({'success': False})

@app.route('/atualizar_usuario/<int:id>', methods=['POST'])
def atualizar_usuario(id):
    usuario = db.session.get(Usuario, id)
    if usuario:
        usuario.nome = request.form.get('nome', usuario.nome)
        usuario.email = request.form.get('email', usuario.email)
        usuario.senha = request.form.get('senha', usuario.senha)
        db.session.commit()
        return render_template('usuarios.html')
    else:
        return jsonify({'success': False})


@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        data_cadastro = request.form.get('data_cadastro')

        if not nome or not email or not senha:
            return jsonify({'success': False, 'message': 'Dados incompletos.'})

        novo_usuario = Usuario(nome=nome, email=email, senha=senha, data_cadastro=data_cadastro)
        db.session.add(novo_usuario)
        db.session.commit()

        # Notificar clientes sobre a atualização
        notify_clients()

        #return jsonify({'success': True, 'message': 'Usuário cadastrado com sucesso!'})
        #return redirect(url_for('usuarios'))
        return usuarios()

    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro de integridade. Possivelmente o email já está em uso.'})

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao cadastrar usuário: {str(e)}'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro inesperado: {str(e)}'})

# Lista de clientes conectados
clients = []

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            if clients:
                yield f"data: {json.dumps({'message': 'update'})}\n\n"
            time.sleep(1)

    return Response(event_stream(), mimetype="text/event-stream")

def notify_clients():
    for client in clients:
        client.put(json.dumps({'message': 'update'}))

@app.route('/obter_usuarios', methods=['GET'])
def obter_usuarios():
    # Usando db.session.execute para obter todos os usuários
    usuarios = db.session.execute(db.select(Usuario)).scalars().all()
    usuarios_list = []
    if usuarios:
        for usuario in usuarios:
            usuarios_list.append({
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'senha': usuario.senha,
                'data_cadastro': usuario.data_cadastro
            })
        return jsonify({
            'success': True,
            'usuarios': usuarios_list
        })
    else:
        return jsonify({'success': False, 'message': 'Nenhum usuário encontrado'})

@app.template_filter('mask_password')
def mask_password(value):
    return '*' * len(value)

if __name__ == '__main__':
    app.run(debug=True)