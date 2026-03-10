from flask import Flask, render_template, request, session, url_for, redirect
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

def carregar_perguntas():
    with open('knowledge/questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['perguntas']
    
@app.route('/forms', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        empresa = request.form.get('empresa')
        
        if not nome or not email:
            return "Erro: preencha nome e email", 400
        
        if '@' not in email:
            return "Erro: email inválido", 400
        
        session['cliente'] = {
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'empresa': empresa
        }
        
        return redirect('/questoes')
    
    return render_template('forms.html')
            
    
@app.route('/questoes', methods=['GET'])    
def questoes():

    cliente = session.get['cliente']

    if cliente not in session:
        return redirect(url_for('forms'))
    
    if request.method == 'GET':
        perguntas = carregar_perguntas()
        return render_template('questoes.html', cliente=session['cliente'], perguntas=perguntas)

    if request.method == 'POST':
        respostas = request.form.get
        return redirect('/analisar')
    
@app.route('/analisar', methods=['POST'])    
def analisar():

    resposta = request
    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')