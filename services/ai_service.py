import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def ler_prompt():
    """Carrega o prompt da pasta knowledge"""
    try:
        with open('knowledge/prompt.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Você é um consultor especializado em análise comercial. Analise as respostas abaixo e gere um diagnóstico."

def gerar_diagnostico(respostas):
    """
    Gera um diagnóstico usando a API Gemini
    
    Args:
        respostas: Dicionário com as respostas do cliente
        
    Returns:
        Texto do diagnóstico gerado pela IA
    """
    try:
        # Configura a API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        
        genai.configure(api_key=api_key)
        
        # Carrega o prompt base (prompt completo com 13 seções de análise)
        prompt_base = ler_prompt()
        
        # Formata as respostas do cliente
        prompt_completo = prompt_base + "\n\n=== RESPOSTAS DO CLIENTE ===\n"
        
        # Adicionar cada resposta ao prompt
        for idx, (chave, resposta) in enumerate(respostas.items(), 1):
            resposta_str = str(resposta).strip()
            prompt_completo += f"\nPergunta {idx}: {resposta_str}"
        
        # Força o uso de gemini-2.5-flash (modelo mais novo e disponível)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Gera a resposta com PROCESSAMENTO OTIMIZADO PARA ANÁLISE COMPLETA
        response = model.generate_content(
            prompt_completo,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=8000,  # Aumentado significativamente para análise completa até seção 13 + próximos passos
                temperature=0.6,  # Reduzido para mais consistência
                top_p=0.95,  # Otimizado para qualidade
                top_k=40  # Configurado para diversidade controlada
            )
        )
        
        # Retorna o texto gerado
        diagnostico = response.text
        print(f"✅ Diagnóstico gerado com sucesso usando gemini-pro")
        return diagnostico
    
    except Exception as e:
        print(f"❌ Erro ao gerar diagnóstico: {str(e)}")
        raise