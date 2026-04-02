import smtplib
import ssl
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

try:
    from cryptography.fernet import Fernet
    CRIPTOGRAFIA_DISPONIVEL = True
except ImportError:
    CRIPTOGRAFIA_DISPONIVEL = False

load_dotenv()

class EmailService:
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = os.getenv('SMTP_PORT')
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.director_email = os.getenv('DIRECTOR_EMAIL')
        
        # Tentar descriptografar senha se estiver criptografada
        if self.email_password and CRIPTOGRAFIA_DISPONIVEL:
            encryption_key = os.getenv('ENCRYPTION_KEY')
            if encryption_key:
                try:
                    self.email_password = self._descriptografar_senha(self.email_password, encryption_key)
                    print(" Senha descriptografada com sucesso")
                except Exception as e:
                    print(f" Falha ao descriptografar senha: {e}")
                    print(" Usando senha como texto plano")
        
        print(" Verificando configurações de email:")
        print(f"   SMTP_SERVER: {self.smtp_server}")
        print(f"   SMTP_PORT: {self.smtp_port}")
        print(f"   EMAIL_USER: {self.email_user}")
        print(f"   EMAIL_PASSWORD: {'*' * len(self.email_password) if self.email_password else 'None'}")
        print(f"   DIRECTOR_EMAIL: {self.director_email}")
      
        self.email_configurado = all([
            self.smtp_server, self.smtp_port, 
            self.email_user, self.email_password
        ])
        
        if self.email_configurado:
            self.smtp_port = int(self.smtp_port)
            print(" Configurações de email OK")
        else:
            print(" Email não configurado corretamente")
    
    def _descriptografar_senha(self, senha_criptografada, chave):
        """Descriptografa a senha usando Fernet"""
        if not CRIPTOGRAFIA_DISPONIVEL:
            raise ImportError("cryptography não está instalado")
        
        f = Fernet(chave.encode())
        return f.decrypt(senha_criptografada.encode()).decode()
    
    def _validar_email(self, email):
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    def testar_conexao(self):
        """Testa a conexão SMTP com detalhes adicionais"""
        if not self.email_configurado:
            print("❌ Email não configurado para teste")
            return False
            
        print("🧪 Iniciando teste de conexão SMTP...")
        
        # Teste 1: STARTTLS na porta configurada
        try:
            print(f"\n🔧 Teste 1: STARTTLS na porta {self.smtp_port}")
            print(f"🔧 Servidor: {self.smtp_server}")
            print(f"🔧 Usuário: {self.email_user}")
            
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            print(f"🔧 Conectado ao servidor SMTP")
            
            server.ehlo()
            print("🔧 EHLO enviado com sucesso")
            
            server.starttls(context=context)
            print("🔧 STARTTLS iniciado com sucesso")
            
            server.ehlo()
            print("🔧 EHLO pós-TLS enviado com sucesso")
            
            print("🔧 Tentando login...")
            server.login(self.email_user, self.email_password)
            print("✅ Login STARTTLS bem-sucedido!")
            server.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Erro de autenticação STARTTLS: {e.smtp_error}")
            print(f"❌ Código: {e.smtp_code}")
        except Exception as e:
            print(f"❌ Erro STARTTLS: {e}")
        
        # Teste 2: SSL na porta 465
        try:
            print(f"\n🔧 Teste 2: SSL na porta 465")
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(self.smtp_server, 465, context=context, timeout=10)
            print(f"🔧 Conectado ao servidor SSL")
            
            server.login(self.email_user, self.email_password)
            print("✅ Login SSL bem-sucedido!")
            server.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Erro de autenticação SSL: {e.smtp_error}")
            print(f"❌ Código: {e.smtp_code}")
        except Exception as e:
            print(f"❌ Erro SSL: {e}")
        
        return False

    def _conectar_smtp(self):
        """
        Tenta conectar ao SMTP em três modos, na ordem:
          1. SMTP + STARTTLS na porta configurada (587)
          2. SMTP_SSL na porta 465 (SSL direto)
          3. SMTP simples sem criptografia (fallback)
        Retorna o objeto server autenticado ou lança exceção.
        """
        context = ssl.create_default_context()

        # 1. Tenta STARTTLS na porta configurada (prioridade para porta 587)
        try:
            print(f"🔧 Tentando STARTTLS na porta {self.smtp_port}...")
            print(f"🔧 Servidor: {self.smtp_server}, Usuário: {self.email_user}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            print(f"🔧 Enviando credenciais para autenticação...")
            server.login(self.email_user, self.email_password)
            print(f"✅ Conexão STARTTLS ({self.smtp_port}) estabelecida")
            return server
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Erro específico de autenticação STARTTLS: {e.smtp_error}")
            print(f"❌ Código do erro: {e.smtp_code}")
            raise  # Senha errada — não adianta tentar outros modos
        except Exception as e:
            print(f"⚠️ STARTTLS {self.smtp_port} falhou: {e}")

        # 2. Tenta SSL direto na 465
        try:
            print("🔧 Tentando SMTP_SSL na porta 465...")
            server = smtplib.SMTP_SSL(self.smtp_server, 465, context=context, timeout=10)
            server.login(self.email_user, self.email_password)
            print("✅ Conexão SSL (465) estabelecida")
            return server
        except smtplib.SMTPAuthenticationError:
            raise
        except Exception as e:
            print(f"⚠️ SSL 465 falhou: {e}")

        # 3. Fallback sem criptografia
        print(f"🔧 Tentando conexão simples na porta {self.smtp_port}...")
        server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
        server.login(self.email_user, self.email_password)
        print(f"✅ Conexão simples ({self.smtp_port}) estabelecida")
        return server

    def enviar_para_cliente(self, cliente_email, pdf_diagnostico, cliente_nome):
        print(f"🔍 Verificando email do cliente: {cliente_email}")
        
        if not self.email_configurado:
            print("⚠️ Email não configurado - pulando envio para cliente")
            return False
            
        if not self._validar_email(cliente_email):
            print(f"❌ Email inválido: '{cliente_email}'")
            return False
            
        print(f"✅ Email válido: {cliente_email}")
            
        assunto = "Seu Diagnóstico - Raio X Comercial"
        corpo = f"""\
Olá {cliente_nome},

Segue em anexo seu diagnóstico personalizado do Raio X Comercial.

Este diagnóstico foi gerado com base nas informações que você forneceu e apresenta uma análise detalhada sobre a saúde comercial da sua empresa.

Qualquer dúvida, entre em contato conosco!

Atenciosamente,
Equipe de Análise Comercial"""
        
        resultado = self._enviar_email(cliente_email, assunto, corpo, [pdf_diagnostico])
        if not resultado:
            print(f"❌ Falha ao enviar email para: {cliente_email}")
        return resultado
    
    def enviar_para_diretor(self, pdf_diagnostico, pdf_respostas, cliente_nome, cliente_empresa):
        if not self.email_configurado or not self.director_email:
            print("⚠️ Email não configurado - pulando envio para diretor")
            return False
            
        assunto = f"Novo Raio X Comercial - {cliente_nome} ({cliente_empresa})"
        corpo = f"""
Novo Raio X Comercial recebido!

Cliente: {cliente_nome}
Empresa: {cliente_empresa}

Em anexo você encontra:
1. Diagnóstico — Análise da saúde comercial
2. Perguntas & Respostas — Detalhamento das respostas coletadas

Atenciosamente,
Sistema Raio X Comercial"""
        
        resultado = self._enviar_email(
            self.director_email, 
            assunto, 
            corpo, 
            [pdf_diagnostico, pdf_respostas]
        )
        if not resultado:
            print("❌ Falha ao enviar email para o diretor")
        return resultado
    
    def _enviar_email(self, destinatario, assunto, corpo, anexos):
        try:
            print(f"📧 Enviando email para: {destinatario}")
            print(f"🔧 Configuração SMTP: {self.smtp_server}:{self.smtp_port}")
            print(f"👤 Remetente: {self.email_user}")
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = destinatario
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
            
            for arquivo_path in anexos:
                self._anexar_arquivo(msg, arquivo_path)
            
            server = self._conectar_smtp()
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email enviado com sucesso para {destinatario}")
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Falha na autenticação SMTP: {e.smtp_error}")
            print(f"🔧 Verifique a senha do email {self.email_user}")
            print(f"🔧 Se for hospedagem, confirme usuário/senha no painel de controle (cPanel)")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ Destinatário rejeitado: {destinatario} — {e.recipients}")
            return False
        except smtplib.SMTPSenderRefused as e:
            print(f"❌ Remetente rejeitado: {self.email_user} — {e.sender}")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Erro SMTP: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar email: {str(e)}")
            return False
    
    def _anexar_arquivo(self, msg, arquivo_path):
        try:
            nome_arquivo = os.path.basename(arquivo_path)
            with open(arquivo_path, 'rb') as anexo:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(anexo.read())
                encoders.encode_base64(parte)
                parte.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{nome_arquivo}"'
                )
                msg.attach(parte)
            print(f"✅ Arquivo anexado: {nome_arquivo}")
        except Exception as e:
            print(f"❌ Erro ao anexar {arquivo_path}: {str(e)}")
            raise