#!/usr/bin/env python3
"""
Testa diferentes formatos de usuário para autenticação
"""
import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

def testar_formatos_usuario():
    """Testa diferentes formatos de usuário"""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print("🧪 TESTANDO FORMATOS DE USUÁRIO 🧪")
    print("=" * 50)
    
    # Extrair partes do email
    partes = email_user.split('@')
    usuario = partes[0]
    dominio = partes[1]
    
    formatos_teste = [
        ("Email completo", email_user),
        ("Só usuário", usuario),
        ("Usuário + domínio (minuscula)", f"{usuario}@{dominio.lower()}"),
        ("Usuário + domínio (maiuscula)", f"{usuario}@{dominio.upper()}"),
        ("cPanel format", f"{usuario}+{dominio}"),
        ("Webmail", f"webmail@{dominio}"),
        ("Conta principal", f"account@{dominio}"),
    ]
    
    for nome, formato in formatos_teste:
        print(f"\n🔧 Testando: {nome}")
        print(f"👤 Usuário: '{formato}'")
        
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            server.login(formato, email_password)
            print(f"✅ SUCESSO! Use: EMAIL_USER={formato}")
            server.quit()
            return formato
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Falha: {e.smtp_error.decode()}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return None

def main():
    formato_sucesso = testar_formatos_usuario()
    
    if formato_sucesso:
        print(f"\n✅ SOLUÇÃO ENCONTRADA!")
        print(f"🔧 Altere seu .env para:")
        print(f"EMAIL_USER={formato_sucesso}")
        print(f"EMAIL_PASSWORD={os.getenv('EMAIL_PASSWORD')}")
    else:
        print("\n❌ Nenhum formato funcionou!")
        print("\n🔧 VERIFICAÇÕES:")
        print("1. A senha tem caracteres especiais? Tente sem aspas")
        print("2. Há espaços em branco no usuário/senha?")
        print("3. O email foi criado no cPanel?")
        print("4. Tente redefinir a senha no cPanel")
        print("5. Verifique se há bloqueio no IP")

if __name__ == "__main__":
    main()
