from flask import Flask, render_template, request, session, url_for, redirect
from dotenv import load_dotenv
import os
import json
import services.ai_service as ai_service
import services.pdf_service as pdf
from services.email_service import EmailService


load_dotenv()

app = Flask(__name__)
app.secret_key = 'seu_codigo_secreto_aqui_123'  # Mude isso para uma chave segura

def carregar_perguntas():
    with open('knowledge/questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['perguntas']
    
@app.route('/')
def home():
    return render_template('home.html')


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
            
    
@app.route('/questoes', methods=['GET', 'POST'])    
def questoes():

    cliente = session.get('cliente')

    if 'cliente' not in session:
        return redirect(url_for('forms'))
    
    if request.method == 'GET':
        perguntas = carregar_perguntas()

        # perguntas=... da esquerda, nome que a variavel tera dentro do HTML
        # perguntas... da direita, nome da variavel que contem as perguntas dentro do Python
        return render_template('questoes.html', cliente=session['cliente'], perguntas=perguntas) 

    if request.method == 'POST':
        session['respostas'] = dict(request.form) # request.form é um dicionário com as respostas do formulário, dict() converte para um formato mais fácil de usar
        return redirect('/analisar')
    
@app.route('/analisar', methods=['GET', 'POST'])
def analisar():
    
    if 'cliente' not in session or 'respostas' not in session:
        return redirect('/forms')
    
    try:
        cliente = session['cliente']
        respostas = session['respostas']
        
        # 1. Gerar diagnóstico via IA
        diagnostico = ai_service.gerar_diagnostico(respostas)
        
        # 2. Gerar PDFs
        pdf_diagnostico = pdf.gerar_pdf_diagnostico(cliente, diagnostico)
        pdf_respostas = pdf.gerar_pdf_respostas(cliente, respostas)
        
        # 3. ENVIAR EMAILS
        email_svc = EmailService()
        
        # Email para o cliente (apenas diagnóstico)
        email_svc.enviar_para_cliente(
            cliente_email=cliente['email'],
            pdf_diagnostico=pdf_diagnostico,
            cliente_nome=cliente['nome']
        )
        
        # Email para o diretor (diagnóstico + respostas)
        email_svc.enviar_para_diretor(
            pdf_diagnostico=pdf_diagnostico,
            pdf_respostas=pdf_respostas,
            cliente_nome=cliente['nome'],
            cliente_empresa=cliente['empresa']
        )
        
        # 4. Salvar diagnóstico em session
        session['diagnostico'] = diagnostico
        
        # 5. Limpar dados temporários
        session.pop('respostas', None)
        
        # 6. Redirecionar
        return redirect('/sucesso')
    
    except Exception as e:
        return f"Erro ao processar: {str(e)}", 500


@app.route('/sucesso', methods=['GET'])
def sucesso():
    
    if 'cliente' not in session:
        return redirect('/forms')
    
    cliente = session['cliente']
    diagnostico = session.get('diagnostico', 'Diagnóstico não disponível')
    
    return render_template('sucesso.html',
                          cliente=cliente,
                          diagnostico=diagnostico)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')