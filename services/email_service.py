import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from flask import session

load_dotenv()

class EmailService:
    
    def __init__(self):
        """Inicializa as credenciais de email do .env"""
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.director_email = os.getenv('DIRECTOR_EMAIL')
    
    def enviar_para_cliente(self, cliente_email, pdf_diagnostico, cliente_nome):
        assunto = "Seu Diagnóstico - Raio X Comercial"
        corpo = f"""
        Olá {cliente_nome},
        
        Segue em anexo seu diagnóstico personalizado do Raio X Comercial.
        
        Este diagnóstico foi gerado com base nas informações que você forneceu
        e apresenta uma análise detalhada sobre a saúde comercial da sua empresa.
        
        Qualquer dúvida, entre em contato conosco!
        
        Atenciosamente,
        Equipe de Análise Comercial
        """
        
        self._enviar_email(cliente_email, assunto, corpo, [pdf_diagnostico])
    
    def enviar_para_diretor(self, pdf_diagnostico, pdf_respostas, cliente_nome, cliente_empresa):
        assunto = f"Novo Raio X Comercial - {cliente_nome} ({cliente_empresa})"
        corpo = f"""
        Novo Raio X Comercial recebido!
        
        Cliente: {cliente_nome}
        Empresa: {cliente_empresa}
        
        Em anexo você encontra:
        1. Mini Diagnóstico - Análise da saúde comercial
        2. Perguntas com Respostas - Detalhamento das respostas coletadas
        
        Atenciosamente,
        Sistema Raio X Comercial
        """
        
        self._enviar_email(
            self.director_email, 
            assunto, 
            corpo, 
            [pdf_diagnostico, pdf_respostas]
        )
    
    def _enviar_email(self, destinatario, assunto, corpo, anexos):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = destinatario
            msg['Subject'] = assunto
            
            msg.attach(MIMEText(corpo, 'plain'))
            
            for arquivo_path in anexos:
                self._anexar_arquivo(msg, arquivo_path)
            
            # Troca SMTP + starttls por SMTP_SSL na porta 465
            with smtplib.SMTP_SSL(self.smtp_server, 465) as server:
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Email enviado com sucesso para {destinatario}")
            return True
        
        except Exception as e:
            print(f"❌ Erro ao enviar email: {str(e)}")
            raise
    
    def _anexar_arquivo(self, msg, arquivo_path):
        try:
            nome_arquivo = os.path.basename(arquivo_path)
            
            with open(arquivo_path, 'rb') as anexo:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(anexo.read())
                encoders.encode_base64(parte)
                parte.add_header(
                    'Content-Disposition', 
                    f'attachment; filename= {nome_arquivo}'
                )
                msg.attach(parte)
            
            print(f"✅ Arquivo anexado: {nome_arquivo}")
        
        except Exception as e:
            print(f"❌ Erro ao anexar arquivo {arquivo_path}: {str(e)}")
            raise