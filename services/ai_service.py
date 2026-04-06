from google import genai
import os
import json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / '.env', override=True)

def ler_prompt():
    try:
        with open('knowledge/prompt.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Você é um consultor especializado em análise comercial."

def carregar_perguntas_contexto():
    try:
        with open('knowledge/questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['perguntas']
    except FileNotFoundError:
        print("⚠️ Arquivo questions.json não encontrado")
        return []
    except Exception as e:
        print(f"⚠️ Erro ao carregar perguntas: {str(e)}")
        return []

def montar_conteudo_respostas(perguntas, respostas):
    """Monta APENAS os dados/respostas — sem repetir as instruções do prompt"""
    
    conteudo = "=" * 80 + "\n"
    conteudo += "DADOS DO DIAGNÓSTICO RAIO-X COMERCIAL VENDAMAIS\n"
    conteudo += "=" * 80 + "\n\n"

    # Agrupar por dimensão
    respostas_por_dimensao = {}
    for pergunta in perguntas:
        pilar_nome = pergunta['pilar_nome']
        if pilar_nome not in respostas_por_dimensao:
            respostas_por_dimensao[pilar_nome] = []

        resposta_key = f"pergunta_{pergunta['id']}"
        resposta_texto = respostas.get(resposta_key, "Não respondida")

        respostas_por_dimensao[pilar_nome].append({
            'id': pergunta['id'],
            'pergunta': pergunta['pergunta'],
            'resposta': resposta_texto
        })

    for dimensao, itens in respostas_por_dimensao.items():
        conteudo += f"\n### {dimensao.upper()} ###\n"
        for item in itens:
            conteudo += f"\nP{item['id']}: {item['pergunta']}\n"
            conteudo += f"Resposta: {item['resposta']}\n"

    conteudo += "\n" + "=" * 80 + "\n"
    conteudo += "ATENÇÃO: Gere o relatório COMPLETO seguindo TODOS os 14 itens da estrutura.\n"
    conteudo += "Não pule nenhuma seção. Não resuma. Escreva cada seção por extenso.\n"
    conteudo += "=" * 80 + "\n"

    return conteudo

def gerar_diagnostico(respostas):
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada no .env")

        client = genai.Client(api_key=api_key)

        perguntas = carregar_perguntas_contexto()
        system_prompt = ler_prompt()  # prompt.txt vira system instruction
        conteudo_respostas = montar_conteudo_respostas(perguntas, respostas)

        print(f"📋 System prompt: {len(system_prompt)} caracteres")
        print(f"📊 Conteúdo respostas: {len(conteudo_respostas)} caracteres")
        print(f"📝 Número de respostas: {len(respostas)}")

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=conteudo_respostas,  # Só os dados aqui
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,  # Instruções como system
                    max_output_tokens=32768,
                    temperature=0.3,
                    top_p=0.95,
                    top_k=40
                )
            )
            print("✅ Resposta recebida do Gemini 2.5 Flash")

        except Exception as e:
            print(f"⚠️ Falha com gemini-2.5-flash: {str(e)}")
            response = client.models.generate_content(
                model='gemini-1.5-pro',
                contents=conteudo_respostas,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=32768,
                    temperature=0.3,
                    top_p=0.95,
                    top_k=40
                )
            )
            print("✅ Resposta recebida do Gemini 1.5 Pro (fallback)")

        diagnostico = response.text

        # Verificação de qualidade: checar se as seções principais estão presentes
        secoes_esperadas = [
            "ALERTA ESTRATÉGICO",
            "DIAGNÓSTICO CENTRAL", 
            "RESUMO EXECUTIVO",
            "MATURIDADE COMERCIAL",
            "DIAGNÓSTICO POR DIMENSÃO",
            "PRIORIDADES ESTRATÉGICAS",
            "PRÓXIMOS PASSOS"
        ]
        
        secoes_presentes = sum(1 for s in secoes_esperadas if s.lower() in diagnostico.lower())
        print(f"✅ Diagnóstico gerado — {secoes_presentes}/{len(secoes_esperadas)} seções detectadas")

        if secoes_presentes < 4:
            print("⚠️ Diagnóstico incompleto, usando fallback estruturado")
            return gerar_diagnostico_fallback(respostas)

        return diagnostico

    except Exception as e:
        print(f"❌ Erro ao gerar diagnóstico: {str(e)}")
        return gerar_diagnostico_fallback(respostas)


def gerar_diagnostico_fallback(respostas):
    """Fallback estruturado com os 14 itens obrigatórios"""
    
    fallback = """
1. ALERTA ESTRATÉGICO
Sua operação comercial apresenta sinais claros de baixa previsibilidade e dependência de fatores externos que limitam o crescimento sustentável. A ausência de processos sistematizados cria um teto invisível para o crescimento.

2. DIAGNÓSTICO CENTRAL
O principal fator que trava o crescimento é a falta de estruturação comercial sistemática. Sem processos previsíveis, cada resultado depende do esforço individual — não do sistema.

3. IMPACTO NO CRESCIMENTO
Compromete previsibilidade de resultados, limita capacidade de escala e gera dependência de esforço individual vs. processo. Crescimento instável e difícil de replicar.

4. RESUMO EXECUTIVO
Score de maturidade: 45/100
Classificação: Em desenvolvimento
Principais desafios: falta de processo, gestão reativa, dependência de carteira existente

5. PERFIL DA EMPRESA
Indústria B2B com operação comercial baseada em relacionamento e baixa sistematização de processos. Modelo com presença de representantes e uso parcial de ferramentas de gestão.

6. MATURIDADE COMERCIAL
Maturidade Comercial: 45/100
Classificação: Em desenvolvimento
Operação com processos definidos mas baixa adesão e gestão predominantemente reativa. Há ferramentas disponíveis, mas sem uso estratégico consistente.

7. INSIGHTS CRÍTICOS
- Crescimento concentrado na carteira existente, sem geração ativa de novos negócios
- Baixa previsibilidade mesmo com utilização parcial de CRM
- Canais comerciais sem integração ou alinhamento estratégico claro
- Remuneração potencialmente distorcendo comportamentos de longo prazo
- Gestão focada em resultado pontual vs. desenvolvimento de processo

8. DIAGNÓSTICO POR DIMENSÃO
Estratégia e Posicionamento: Nível baixo — impacto direto na consistência e direcionamento comercial
Estrutura e Canais: Nível médio — impacto na eficiência operacional e cobertura de mercado
Execução Comercial: Nível baixo — impacto na previsibilidade e consistência de resultados
Geração de Demanda: Nível baixo — impacto no crescimento sustentável e redução de dependência
Gestão e Liderança: Nível médio — impacto na gestão por dados e tomada de decisão
Política Comercial e Remuneração: Nível médio — impacto no alinhamento de comportamentos
Carteira, Escala e Risco: Nível baixo — impacto na dependência e concentração de receita

9. O QUE ESTÁ LIMITANDO A EVOLUÇÃO
Falta de processo comercial estruturado → gestão reativa → resultados inconsistentes → incapacidade de escalar a operação de forma previsível e sustentável.

10. PRINCIPAIS GARGALOS
- Ausência de processo comercial sistematizado → gestão por intuição → resultados imprevisíveis
- Baixa geração de demanda estruturada → dependência excessiva da base → risco de estagnação
- Gestão focada em resultado vs. processo → sem melhoria contínua → sem evolução de maturidade

11. RISCOS ESTRATÉGICOS
- Dependência de clientes-chave e vendedores críticos sem substitutos
- Baixa previsibilidade de faturamento comprometendo planejamento financeiro
- Incapacidade de escalar crescimento sem aumentar proporcionalmente o time
- Perda de competitividade pela ausência de inovação comercial
- Margens pressionadas por negociação de preço sem gestão de valor

12. PRIORIDADES ESTRATÉGICAS
1. Implementar processo comercial estruturado → criar previsibilidade → escalar operação com consistência
2. Desenvolver geração de demanda ativa → reduzir dependência da carteira → garantir crescimento orgânico
3. Estruturar gestão por indicadores → decisões baseadas em dados → melhoria contínua real
4. Alinhar remuneração com comportamentos estratégicos → foco em valor vs. volume → rentabilidade
5. Integrar CRM como ferramenta de gestão → visibilidade do funil → previsão de receita confiável

13. INSIGHT FINAL
Transformar uma operação comercial de reativa para proativa não é sobre trabalhar mais — é sobre construir um sistema que funcione com consistência, independente de quem está na equipe.

14. PRÓXIMOS PASSOS
Se você chegou até aqui, já percebeu que estruturar uma área comercial não é apenas vender mais. É criar previsibilidade, escala e consistência de crescimento.
A VendaMais ajuda empresas a construir operações comerciais de alta performance há mais de 30 anos.
Se quiser aprofundar esse diagnóstico e transformar essas recomendações em um plano de ação real para sua empresa, fale com nosso time.
Agende uma conversa estratégica com um especialista da VendaMais.
(41) 99239-0796 ou e-mail: atendimento@vendamais.com.br
"""
    
    print("✅ Diagnóstico fallback estruturado gerado")
    return fallback