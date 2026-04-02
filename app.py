from flask import Flask, render_template, request, session, url_for, redirect
from dotenv import load_dotenv
import os
import json
import services.ai_service as ai_service
import services.pdf_service as pdf
from services.email_service import EmailService
import tempfile
import uuid


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_local')

# Verificar configurações essenciais ao iniciar
def verificar_configuracao():
    gemini_key = os.getenv('GEMINI_API_KEY')
    email_config = {
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': os.getenv('SMTP_PORT'),
        'email_user': os.getenv('EMAIL_USER'),
        'email_password': os.getenv('EMAIL_PASSWORD'),
        'director_email': os.getenv('DIRECTOR_EMAIL')
    }
    
    print("🔍 Verificando configuração:")
    print(f"   Gemini API Key: {'✅ Configurada' if gemini_key else '❌ Não configurada'}")
    print(f"   Email SMTP: {'✅ Configurado' if all(email_config.values()) else '❌ Incompleto'}")
    
    if not gemini_key:
        print("⚠️ AVISO: GEMINI_API_KEY não configurada. A geração de diagnóstico falhará.")
    
    if not all(email_config.values()):
        print("⚠️ AVISO: Configuração de email incompleta. O envio de emails será pulado.")
    
    return gemini_key is not None

# Executar verificação ao iniciar
verificar_configuracao()

def carregar_perguntas():
    with open('knowledge/forms.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['perguntas']

def carregar_questoes_diagnostico():
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
        cargo = request.form.get('cargo', '')
        cidade = request.form.get('cidade', '')
        segmento_empresa = request.form.get('segmento_empresa', '')
        num_colaboradores = request.form.get('num_colaboradores', '')
        faturamento = request.form.get('faturamento', '')
        
        if not nome or not email:
            return "Erro: preencha nome e email", 400
        
        if '@' not in email:
            return "Erro: email inválido", 400
        
        session['cliente'] = {
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'empresa': empresa,
            'cargo': cargo,
            'cidade': cidade,
            'segmento_empresa': segmento_empresa,
            'num_colaboradores': num_colaboradores,
            'faturamento': faturamento
        }
        
        return redirect('/questoes')
    
    perguntas = carregar_perguntas()
    return render_template('forms.html', perguntas=perguntas)
            
    
@app.route('/questoes', methods=['GET', 'POST'])    
def questoes():

    cliente = session.get('cliente')

    if 'cliente' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        perguntas = carregar_questoes_diagnostico()

        # perguntas=... da esquerda, nome que a variavel tera dentro do HTML
        # perguntas... da direita, nome da variavel que contem as perguntas dentro do Python
        return render_template('questoes.html', cliente=session['cliente'], perguntas=perguntas) 

    if request.method == 'POST':
        session['respostas'] = dict(request.form) # request.form é um dicionário com as respostas do formulário, dict() converte para um formato mais fácil de usar
        return redirect('/analisar')
    
@app.route('/analisar', methods=['GET'])
def analisar():
    """Exibe a página de carregamento da análise"""
    if 'cliente' not in session or 'respostas' not in session:
        print(f"❌ Sessão inválida - Cliente: {('cliente' in session)}, Respostas: {('respostas' in session)}")
        return redirect(url_for('index'))
    
    print(f"✅ Sessão válida - Processando análise para: {session['cliente'].get('nome', 'Desconhecido')}")
    return render_template('analisar.html')


@app.route('/api/analisar', methods=['POST'])
def api_analisar():
    if 'cliente' not in session or 'respostas' not in session:
        return {'erro': 'Dados incompletos - sessão inválida'}, 400
    
    try:
        cliente = session['cliente']
        respostas = session['respostas']
        
        print(f"📊 Iniciando análise para: {cliente.get('nome', 'Desconhecido')}")
        
        diagnostico = ai_service.gerar_diagnostico(respostas)
        print("✅ Diagnóstico gerado com sucesso")
        
        # Salvar em arquivo temporário em vez de na sessão
        token = str(uuid.uuid4())
        caminho = f"diagnosticos/temp_{token}.txt"
        os.makedirs("diagnosticos", exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(diagnostico)
        
        session['diagnostico_token'] = token  # só o token fica na sessão (pequeno)
        session.modified = True
        print(f"💾 Diagnóstico salvo em arquivo: {caminho}")
        
        return {'sucesso': True}, 200
    
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")
        return {'erro': str(e)}, 500


@app.route('/api/processar_background', methods=['POST'])
def api_processar_background():
    if 'cliente' not in session or 'respostas' not in session:
        return {'erro': 'Dados incompletos'}, 400
    
    try:
        cliente = session['cliente']
        respostas = session['respostas']
        
        # Ler diagnóstico do arquivo temporário
        token = session.get('diagnostico_token', '')
        caminho = f"diagnosticos/temp_{token}.txt"
        
        with open(caminho, 'r', encoding='utf-8') as f:
            diagnostico = f.read()
        
        print("📄 Gerando PDFs em background...")
        pdf_diagnostico = pdf.gerar_pdf_diagnostico(cliente, diagnostico)
        pdf_respostas = pdf.gerar_pdf_respostas(cliente, respostas)
        
        print("📧 Enviando emails em background...")
        email_svc = EmailService()
        email_svc.enviar_para_cliente(
            cliente_email=cliente['email'],
            pdf_diagnostico=pdf_diagnostico,
            cliente_nome=cliente['nome']
        )
        email_svc.enviar_para_diretor(
            pdf_diagnostico=pdf_diagnostico,
            pdf_respostas=pdf_respostas,
            cliente_nome=cliente['nome'],
            cliente_empresa=cliente['empresa']
        )
        
        # Limpar arquivo temporário e sessão
        if os.path.exists(caminho):
            os.remove(caminho)
        session.pop('respostas', None)
        session.pop('diagnostico_token', None)
        print("✅ Processamento background concluído")
        
        return {'sucesso': True}, 200
    
    except Exception as e:
        print(f"❌ Erro no processamento background: {str(e)}")
        return {'erro': str(e)}, 500

@app.route('/sucesso', methods=['GET'])
def sucesso():
    if 'cliente' not in session:
        return redirect(url_for('index'))
    
    cliente = session['cliente']
    
    # Ler diagnóstico do arquivo temporário
    token = session.get('diagnostico_token', '')
    caminho = f"diagnosticos/temp_{token}.txt"
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            diagnostico = f.read()
    except:
        diagnostico = 'Diagnóstico não disponível'
    
    return render_template('sucesso.html', cliente=cliente, diagnostico=diagnostico)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
