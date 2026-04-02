#!/usr/bin/env python3
"""
Script para criptografar senhas de forma segura
"""
import base64
from cryptography.fernet import Fernet
import os

def gerar_chave():
    """Gera uma chave de criptografia e salva em arquivo"""
    chave = Fernet.generate_key()
    with open('chave_criptografia.key', 'wb') as f:
        f.write(chave)
    print(f"✅ Chave gerada: {chave.decode()}")
    print("🔧 Guarde esta chave em local seguro!")
    return chave

def criptografar_senha(senha, chave):
    """Criptografa a senha"""
    f = Fernet(chave)
    senha_criptografada = f.encrypt(senha.encode())
    return senha_criptografada.decode()

def main():
    print("🔐 CRIPTOGRAFADOR DE SENHA 🔐")
    print("=" * 40)
    
    # Gerar chave
    chave = gerar_chave()
    
    # Senha do vendamais
    senha_vendamais = "240696Da*"
    
    # Criptografar
    senha_cript = criptografar_senha(senha_vendamais, chave)
    
    print(f"\n📧 Senha original: {senha_vendamais}")
    print(f"🔒 Senha criptografada: {senha_cript}")
    
    print(f"\n🔧 Configure seu .env assim:")
    print(f"# SMTP")
    print(f"SMTP_SERVER=vendamais.com.br")
    print(f"SMTP_PORT=587")
    print(f"EMAIL_USER=daniel.batista@vendamais.com.br")
    print(f"EMAIL_PASSWORD={senha_cript}")
    print(f"ENCRYPTION_KEY={chave.decode()}")
    
    print(f"\n🔧 E no email_service.py adicione:")
    print(f"def _descriptografar_senha(self, senha_cript):")
    print(f"    f = Fernet(self.encryption_key.encode())")
    print(f"    return f.decrypt(senha_cript.encode()).decode()")

if __name__ == "__main__":
    main()
