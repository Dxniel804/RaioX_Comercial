from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def ler_prompt():
    try:
        with open('knowledge/prompt.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Você é um consultor especializado em análise comercial. Analise as respostas abaixo e gere um diagnóstico."

def gerar_diagnostico(respostas):
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada no .env")

        client = genai.Client(api_key=api_key)

        prompt_base = ler_prompt()
        prompt_completo = prompt_base + "\n\n=== RESPOSTAS DO CLIENTE ===\n"

        for idx, (chave, resposta) in enumerate(respostas.items(), 1):
            resposta_str = str(resposta).strip()
            prompt_completo += f"\nPergunta {idx}: {resposta_str}"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_completo,
            config=genai.types.GenerateContentConfig(
                max_output_tokens=12000,
                temperature=0.6,
                top_p=0.95,
                top_k=40
            )
        )

        diagnostico = response.text
        print(f"✅ Diagnóstico gerado com sucesso")
        return diagnostico

    except Exception as e:
        print(f"❌ Erro ao gerar diagnóstico: {str(e)}")
        raise