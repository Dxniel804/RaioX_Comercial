# Serviço de geração de PDFs com ReportLab
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

def criar_diretorio_se_nao_existe(diretorio):
    """Cria o diretório se ele não existir"""
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
        print(f"✅ Diretório criado: {diretorio}")


def gerar_pdf_diagnostico(cliente, diagnostico):
    """Gera PDF profissional com o diagnóstico do cliente"""
    
    criar_diretorio_se_nao_existe("diagnosticos")
    caminho_pdf = f"diagnosticos/pdf_{cliente['nome']}.pdf"
    
    # Criar documento
    doc = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Container de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo customizado para título
    style_titulo = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    style_subtitulo = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    style_diagnostico = ParagraphStyle(
        'DiagnosticoStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14
    )
    
    # Título
    elements.append(Paragraph("📊 Diagnóstico Comercial", style_titulo))
    elements.append(Paragraph("Raio X Comercial - Análise Executiva", style_subtitulo))
    
    # Informações do cliente em tabela
    data_cliente = [
        ["Cliente:", cliente['nome']],
        ["Empresa:", cliente['empresa']],
        ["Email:", cliente['email']],
        ["Telefone:", cliente['telefone']],
        ["Data:", datetime.now().strftime('%d/%m/%Y às %H:%M')]
    ]
    
    table_cliente = Table(data_cliente, colWidths=[1.5*inch, 4*inch])
    table_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9f9f9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMBORDER', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    
    elements.append(table_cliente)
    elements.append(Spacer(1, 20))
    
    # Diagnóstico
    diagnostico_formatado = diagnostico.replace('\n', '<br/>')
    elements.append(Paragraph(diagnostico_formatado, style_diagnostico))
    
    # Rodapé
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "Este diagnóstico foi gerado automaticamente pelo sistema Raio X Comercial.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(elements)
    print(f"✅ PDF de diagnóstico criado: {caminho_pdf}")
    
    return caminho_pdf


def gerar_pdf_respostas(cliente, respostas):
    """Gera PDF profissional com as respostas do cliente"""
    
    criar_diretorio_se_nao_existe("respostas")
    caminho_pdf = f"respostas/pdf_{cliente['nome']}.pdf"
    
    # Criar documento
    doc = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=40
    )
    
    # Container de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo customizado para título
    style_titulo = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    style_subtitulo = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Título
    elements.append(Paragraph("📋 Respostas do Cliente", style_titulo))
    elements.append(Paragraph("Raio X Comercial - Detalhamento das Respostas", style_subtitulo))
    
    # Informações do cliente
    data_cliente = [
        ["Cliente:", cliente['nome']],
        ["Empresa:", cliente['empresa']],
        ["Email:", cliente['email']],
        ["Data:", datetime.now().strftime('%d/%m/%Y às %H:%M')]
    ]
    
    table_cliente = Table(data_cliente, colWidths=[1.5*inch, 4*inch])
    table_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9f9f9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMBORDER', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    
    elements.append(table_cliente)
    elements.append(Spacer(1, 20))
    
    # Tabela de respostas
    data_respostas = [["Pergunta", "Resposta"]]
    
    for pergunta, resposta in respostas.items():
        resposta_str = str(resposta)[:100] if len(str(resposta)) > 100 else str(resposta)
        data_respostas.append([pergunta, resposta_str])
    
    table_respostas = Table(data_respostas, colWidths=[2.5*inch, 3.5*inch])
    table_respostas.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        # Body
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('LEFTPADDING', (0, 1), (-1, -1), 10),
        ('RIGHTPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        # Borders
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        # Alternating rows
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    
    elements.append(table_respostas)
    
    # Rodapé
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "Documento gerado automaticamente pelo sistema Raio X Comercial | Confidencial - Uso interno apenas.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(elements)
    print(f"✅ PDF de respostas criado: {caminho_pdf}")
    
    return caminho_pdf