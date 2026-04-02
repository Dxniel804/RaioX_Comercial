#!/usr/bin/env python3
"""
Teste específico para vendamais.com.br
"""
import smtplib
import ssl
import os
from dotenv import load_dotenv
from services.email_service import EmailService

load_dotenv()

def testar_formatos_especificos():
    """Testa formatos específicos para hospedagens cPanel"""
    smtp_server = "vendamais.com.br"
    smtp_port = 587
    
    # Senha original (não criptografada para teste)
    senha_original = "240696Da*"
    
    # Formatos comuns em hospedagens cPanel
    formatos_teste = [
        ("Email completo", "daniel.batista@vendamais.com.br"),
        ("Só usuário", "daniel.batista"),
        ("Usuário com +", "daniel.batista+vendamais.com.br"),
        ("Conta principal", "daniel@vendamais.com.br"),
        ("Webmail", "webmail@vendamais.com.br"),
        ("cPanel format", "danielb"),  # sem ponto
        ("Dominio só", "vendamais.com.br"),
    ]
    
    print("🧪 TESTE ESPECÍFICO VENDAMAIS.COM.BR 🧪")
    print("=" * 60)
    
    for nome, usuario in formatos_teste:
        print(f"\n🔧 Testando: {nome}")
        print(f"👤 Usuário: '{usuario}'")
        
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            server.login(usuario, senha_original)
            print(f"✅ SUCESSO! Formato correto: '{usuario}'")
            server.quit()
            
            print(f"\n🎯 SOLUÇÃO ENCONTRADA!")
            print(f"🔧 Configure seu .env com:")
            print(f"EMAIL_USER={usuario}")
            print(f"EMAIL_PASSWORD={senha_original}")
            return usuario
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Falha: {e.smtp_error.decode()}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return None

def testar_portas_alternativas():
    """Testa portas alternativas"""
    print("\n🔧 TESTANDO PORTAS ALTERNATIVAS")
    print("=" * 40)
    
    portas = [25, 26, 465, 587, 2525]
    usuario = "daniel.batista@vendamais.com.br"
    senha = "240696Da*"
    
    for porta in portas:
        print(f"\n🔧 Testando porta {porta}...")
        try:
            if porta == 465:
                # SSL direto
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL("vendamais.com.br", porta, context=context, timeout=10)
                server.login(usuario, senha)
                print(f"✅ SSL porta {porta} funcionou!")
                server.quit()
                return porta
            else:
                # STARTTLS
                context = ssl.create_default_context()
                server = smtplib.SMTP("vendamais.com.br", porta, timeout=10)
                server.ehlo()
                if porta != 25:  # Porta 25 geralmente não usa STARTTLS
                    server.starttls(context=context)
                    server.ehlo()
                server.login(usuario, senha)
                print(f"✅ STARTTLS porta {porta} funcionou!")
                server.quit()
                return porta
                
        except Exception as e:
            print(f"❌ Porta {porta} falhou: {e}")
    
    return None

def main():
    # Testar formatos de usuário
    usuario_sucesso = testar_formatos_especificos()
    
    if not usuario_sucesso:
        # Testar portas alternativas
        porta_sucesso = testar_portas_alternativas()
        
        if porta_sucesso:
            print(f"\n🎯 Tente usar a porta {porta_sucesso}")
        else:
            print("\n❌ Nenhuma configuração funcionou!")
            print("\n🔧 RECOMENDAÇÕES:")
            print("1. Verifique no cPanel > Email Accounts > Configure Email Client")
            print("2. Confirme se o email foi criado corretamente")
            print("3. Verifique se há 'SMTP Authentication' habilitado")
            print("4. Tente redefinir a senha no cPanel")
            print("5. Contate o suporte da hospedagem")

if __name__ == "__main__":
    main()
