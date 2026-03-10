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
        
        # Carrega o prompt base
        prompt_base = ler_prompt()
        
        # Formata as respostas
        prompt_completo = prompt_base + "\n\n=== RESPOSTAS DO CLIENTE ===\n"
        
        for pergunta, resposta in respostas.items():
            prompt_completo += f"\n{pergunta}: {resposta}"
        
        prompt_completo += "\n\n=== DIAGNÓSTICO REQUERIDO ===\n"
        prompt_completo += "Gere um diagnóstico executivo com: 1) Situação atual, 2) Pontos fortes, 3) Oportunidades, 4) Recomendações"
        
        # Força o uso de gemini-2.5-flash (modelo mais novo e disponível)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Gera a resposta com PROCESSAMENTO OTIMIZADO
        response = model.generate_content(
            prompt_completo,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1500,  # Reduzido de 2500 para não atingir limite
                temperature=0.7,  # Reduzido de 0.8 para ser mais direto
                top_p=0.9,  # Reduzido para evitar estouro
                top_k=30  # Reduzido para evitar estouro
            )
        )
        
        # Retorna o texto gerado
        diagnostico = response.text
        print(f"✅ Diagnóstico gerado com sucesso usando gemini-pro")
        return diagnostico
    
    except Exception as e:
        print(f"❌ Erro ao gerar diagnóstico: {str(e)}")
        raise