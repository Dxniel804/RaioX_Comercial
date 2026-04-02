#!/usr/bin/env python3
"""
Testa se o problema é restrição de destinatário
"""
import smtplib
import ssl
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def testar_envio_para_diferentes_destinatarios():
    """Testa envio para diferentes tipos de destinatário"""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    director_email = os.getenv('DIRECTOR_EMAIL')
    
    print("🧪 TESTANDO ENVIO PARA DIFERENTES DESTINATÁRIOS 🧪")
    print("=" * 60)
    
    destinatarios_teste = [
        ("Email próprio (mesmo domínio)", email_user),
        ("Diretor (mesmo domínio)", director_email),
        ("Email externo (Gmail)", "dani.guto911@gmail.com"),
    ]
    
    for nome_dest, destinatario in destinatarios_teste:
        print(f"\n🔧 Testando envio para: {nome_dest}")
        print(f"📧 Destinatário: {destinatario}")
        
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            # Login
            server.login(email_user, email_password)
            print("✅ Login bem-sucedido")
            
            # Criar email simples
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = destinatario
            msg['Subject'] = "Teste de SMTP"
            msg.attach(MIMEText("Este é um email de teste", 'plain', 'utf-8'))
            
            # Tentar enviar
            server.send_message(msg)
            print(f"✅ Email enviado com sucesso para {destinatario}")
            server.quit()
            
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ Destinatário RECUSADO: {e.recipients}")
            print("🔧 O servidor não permite envio para este destinatário!")
        except smtplib.SMTPSenderRefused as e:
            print(f"❌ Remetente RECUSADO: {e.sender}")
            print("🔧 O servidor não aceita este remetente!")
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Erro de autenticação: {e.smtp_error.decode()}")
        except Exception as e:
            print(f"❌ Erro ao enviar: {e}")

def testar_relay_smtp():
    """Testa se o servidor requer configuração especial"""
    print("\n🔧 TESTANDO CONFIGURAÇÕES ESPECIAIS DO SERVIDOR")
    print("=" * 60)
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        
        # Verificar comandos suportados
        server.ehlo()
        print("🔧 Comandos suportados pelo servidor:")
        print(server.esmtp_features)
        
        server.starttls(context=context)
        server.ehlo()
        
        # Login
        server.login(email_user, email_password)
        print("✅ Autenticação OK")
        
        # Verificar se há limites
        print("🔧 Verificando se há restrições de envio...")
        
        server.quit()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    testar_envio_para_diferentes_destinatarios()
    testar_relay_smtp()
    
    print("\n" + "=" * 60)
    print("🔧 ANÁLISE FINAL:")
    print("1. Se só emails do mesmo domínio funcionam:")
    print("   → O servidor tem restrição de relay (comum em hospedagens)")
    print("2. Se nenhum email funciona:")
    print("   → Pode ser bloqueio de IP ou configuração específica")
    print("3. Se só Gmail falha:")
    print("   → Pode ser SPF/DKIM ou política anti-spam")

if __name__ == "__main__":
    main()
