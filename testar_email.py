#!/usr/bin/env python3
"""
Script de teste para diagnosticar problemas de SMTP
"""
from services.email_service import EmailService
import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

def testar_diferentes_formatos():
    """Testa diferentes formatos de usuário"""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print("🧪 TESTANDO DIFERENTES FORMATOS DE USUÁRIO 🧪")
    print("=" * 60)
    
    # Extrair diferentes formatos do email
    dominio = email_user.split('@')[1]
    usuario_sem_dominio = email_user.split('@')[0]
    
    formatos_teste = [
        email_user,  # email completo
        usuario_sem_dominio,  # só usuário
        f"{usuario_sem_dominio}@{dominio}",  # mesmo formato
        f"webmail@{dominio}",  # webmail
        f"postmaster@{dominio}",  # postmaster
    ]
    
    for i, formato in enumerate(formatos_teste, 1):
        print(f"\n🔧 Teste {i}: Usuário = '{formato}'")
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            server.login(formato, email_password)
            print(f"✅ SUCESSO com usuário: '{formato}'")
            server.quit()
            return formato
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Falha: {e.smtp_error.decode()}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return None

def main():
    print("🧪 TESTE DE CONEXÃO SMTP 🧪")
    print("=" * 50)
    
    # Criar instância do serviço
    email_svc = EmailService()
    
    # Executar teste detalhado
    sucesso = email_svc.testar_conexao()
    
    if not sucesso:
        print("\n" + "=" * 50)
        print("🔧 Testando diferentes formatos de usuário...")
        formato_sucesso = testar_diferentes_formatos()
        
        if formato_sucesso:
            print(f"\n✅ SOLUÇÃO ENCONTRADA!")
            print(f"🔧 Use este usuário no .env: {formato_sucesso}")
        else:
            print("\n❌ Nenhum formato funcionou!")
            print("\n🔧 VERIFICAÇÕES FINAIS:")
            print("1. A senha está 100% correta?")
            print("2. O email existe mesmo na hospedagem?")
            print("3. Há autenticação de 2 fatores ativada?")
            print("4. O IP está bloqueado?")
            print("5. Contate o suporte da hospedagem")

if __name__ == "__main__":
    main()
