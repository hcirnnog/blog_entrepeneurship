from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

# Conexão com MongoDB (ajuste se necessário)
client = MongoClient('mongodb://localhost:27017/')
db = client['blog_db']
posts_collection = db['posts']

#  Endpoints CRUD da API
@app.route('/posts', methods=['GET'])
def get_posts():
    posts = []
    for post in posts_collection.find():
        post['_id'] = str(post['_id'])  # Converte ObjectId para string para uso em URLs/templates
        posts.append(post)
    return jsonify(posts), 200

@app.route('/posts/<id>', methods=['GET'])
def get_post(id):
    try:
        post = posts_collection.find_one({'_id': ObjectId(id)})
        if post:
            post['_id'] = str(post['_id'])
            return jsonify(post), 200
        return jsonify({'error': 'Post not found'}), 404
    except:
        return jsonify({'error': 'Invalid ID'}), 400

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    titulo = data.get('titulo', '').strip()
    conteudo = data.get('conteudo', '').strip()
    autor = data.get('autor', '').strip()
    
    if not titulo or not conteudo or not autor:
        return jsonify({'error': 'Título, conteúdo e autor são obrigatórios'}), 400
    
    post = {
        'titulo': titulo,
        'conteudo': conteudo,
        'autor': autor,
        'data': datetime.utcnow()
    }
    result = posts_collection.insert_one(post)
    post['_id'] = str(result.inserted_id)
    return jsonify(post), 201

@app.route('/posts/<id>', methods=['DELETE'])
def delete_post(id):
    try:
        result = posts_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count > 0:
            return '', 200
        return jsonify({'error': 'Post not found'}), 404
    except:
        return jsonify({'error': 'Invalid ID'}), 400

# Parte 2: Rota para renderização HTML
@app.route('/blog')
def blog():
    posts = []
    for post in posts_collection.find():
        post['_id'] = str(post['_id'])
        posts.append(post)
    return render_template('blog.html', posts=posts)

# Bônus: Rotas auxiliares para integração com formulário HTML (criar e deletar via form, com redirecionamento)
@app.route('/create', methods=['POST'])
def create_post_form():
    titulo = request.form.get('titulo', '').strip()
    conteudo = request.form.get('conteudo', '').strip()
    autor = request.form.get('autor', '').strip()
    
    if titulo and conteudo and autor:
        post = {
            'titulo': titulo,
            'conteudo': conteudo,
            'autor': autor,
            'data': datetime.utcnow()
        }
        posts_collection.insert_one(post)
    # Após criar, redireciona para /blog (mesmo se erro, para simplicidade)
    return redirect(url_for('blog'))

@app.route('/delete/<id>', methods=['POST'])
def delete_post_form(id):
    try:
        posts_collection.delete_one({'_id': ObjectId(id)})
    except:
        pass  # Ignora erro para simplicidade
    # Após deletar, redireciona para /blog
    return redirect(url_for('blog'))

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Blog API com Flask e MongoDB")
    print("="*50)
    print("\nAcesse: http://localhost:5000/blog")
    print("\nEndpoints API:")
    print("  GET    /posts")
    print("  GET    /posts/<id>")
    print("  POST   /posts")
    print("  DELETE /posts/<id>")
    print("="*50 + "\n")
    app.run(port=5000, debug=True)