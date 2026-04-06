# Serviço de geração de PDFs — Raio X Comercial
import os
import re
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.flowables import Flowable
from datetime import datetime

# ── Paleta (espelha o CSS do sistema) ────────────────────────────────────────
NAVY       = colors.HexColor('#1a1a2e')
GOLD       = colors.HexColor('#c8a96e')
GOLD_DARK  = colors.HexColor('#a8893e')
MUTED      = colors.HexColor('#7a7469')
BG         = colors.HexColor('#f5f3ef')
SURFACE    = colors.HexColor('#fafaf8')
BORDER     = colors.HexColor('#ddd8d0')
WHITE      = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 40


# ════════════════════════════════════════════════════════════════════════════
# FLOWABLES CUSTOMIZADOS
# ════════════════════════════════════════════════════════════════════════════

class GoldRule(Flowable):
    """Linha decorativa."""
    def __init__(self, width=None, thickness=2, color=GOLD, spaceAfter=12):
        super().__init__()
        self._width    = width
        self.thickness = thickness
        self.color     = color
        self.spaceAfter = spaceAfter

    def draw(self):
        w = self._width or 500
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, w, 0)

    def wrap(self, availW, availH):
        self._width = self._width or availW
        return (self._width, self.thickness + self.spaceAfter)


class SectionHeader(Flowable):
    """Cabeçalho de seção com barra lateral dourada."""
    def __init__(self, text, width=None):
        super().__init__()
        self.text    = text
        self._width  = width
        self.height  = 30

    def draw(self):
        w = self._width or 500
        self.canv.setFillColor(GOLD)
        self.canv.rect(0, 4, 3, 22, fill=1, stroke=0)
        self.canv.setFillColor(BG)
        self.canv.rect(6, 2, w - 6, 26, fill=1, stroke=0)
        self.canv.setFillColor(NAVY)
        self.canv.setFont('Helvetica-Bold', 9)
        self.canv.drawString(14, 10, self.text.upper())

    def wrap(self, availW, availH):
        self._width = availW
        return (availW, self.height)


# ════════════════════════════════════════════════════════════════════════════
# PARSER DE MARKDOWN → FLOWABLES
# ════════════════════════════════════════════════════════════════════════════

def _inline(texto):
    """
    Converte marcações inline de markdown para tags ReportLab:
      **bold** → <b>bold</b>
      *italic* → <i>italic</i>
    Remove asteriscos soltos que sobrarem.
    """
    texto = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', texto)
    texto = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', texto)
    texto = texto.replace('**', '').replace('*', '')
    return texto


def _limpar_diagnostico(texto):
    """
    Remove artefatos que a IA pode inserir:
      - Linhas com 10+ caracteres = ou -
      - Linhas que sejam apenas o título do relatório em maiúsculas
    """
    linhas = texto.splitlines()
    linhas_limpas = []
    for linha in linhas:
        stripped = linha.strip()
        # Remove separadores de igual ou traço
        if re.match(r'^[=\-]{10,}$', stripped):
            continue
        # Remove linha de título duplicado que a IA insere
        if re.match(r'^RELATÓRIO\s+EXECUTIVO[:\s]', stripped, re.IGNORECASE):
            continue
        linhas_limpas.append(linha)
    return '\n'.join(linhas_limpas)


def _md_para_flowables(texto_md, estilos):
    """
    Recebe texto markdown vindo da IA e devolve lista de Flowables
    com hierarquia visual limpa.

    Suportado:
      ## Título 2   →  subtítulo de seção
      ### Título 3  →  subtítulo menor
      - item        →  bullet
      1. item       →  lista numerada
      linha vazia   →  espaçamento entre parágrafos
      texto normal  →  parágrafo justificado
    """
    # Limpa artefatos antes de processar
    texto_md = _limpar_diagnostico(texto_md)

    fl = []
    linhas = texto_md.splitlines()
    i = 0

    while i < len(linhas):
        linha = linhas[i].rstrip()

        # ── Linha em branco → espaço pequeno ──────────────────────────────
        if not linha.strip():
            fl.append(Spacer(1, 6))
            i += 1
            continue

        # ── H2: ## Título ──────────────────────────────────────────────────
        if linha.startswith('## '):
            txt = _inline(linha[3:].strip())
            fl.append(Spacer(1, 14))
            fl.append(Paragraph(txt, estilos['h2']))
            fl.append(HRFlowable(width='100%', thickness=0.6,
                                 color=BORDER, spaceAfter=6))
            i += 1
            continue

        # ── H3: ### Título ─────────────────────────────────────────────────
        if linha.startswith('### '):
            txt = _inline(linha[4:].strip())
            fl.append(Spacer(1, 10))
            fl.append(Paragraph(txt, estilos['h3']))
            i += 1
            continue

        # ── Bullet: - item ou * item ───────────────────────────────────────
        if re.match(r'^[-*]\s+', linha):
            txt = _inline(re.sub(r'^[-*]\s+', '', linha))
            fl.append(Paragraph(f'• &nbsp; {txt}', estilos['bullet']))
            i += 1
            continue

        # ── Lista numerada ou cabeçalho de seção: 1. Título ───────────────
        m = re.match(r'^(\d{1,2})\.\s+(.+)', linha)
        if m:
            num = m.group(1)
            titulo_candidato = m.group(2).strip()
            palavras = titulo_candidato.split()
            tem_seta = '→' in titulo_candidato or '->' in titulo_candidato
            # Cabeçalho de seção: curto, sem seta, começa com maiúscula
            is_cabecalho = (
                len(palavras) <= 7
                and not tem_seta
                and palavras[0][0].isupper()
                and not titulo_candidato.endswith('.')
            )
            if is_cabecalho:
                txt = _inline(titulo_candidato)
                fl.append(Spacer(1, 14))
                fl.append(Paragraph(f'{num}. {txt}', estilos['h2']))
                fl.append(HRFlowable(width='100%', thickness=0.6,
                                     color=BORDER, spaceAfter=6))
            else:
                txt = _inline(titulo_candidato)
                fl.append(Spacer(1, 6))
                fl.append(Paragraph(f'<b>{num}.</b> &nbsp; {txt}', estilos['bullet']))
            i += 1
            continue

        # ── Parágrafo normal ───────────────────────────────────────────────
        bloco = [linha]
        i += 1
        while i < len(linhas):
            prox = linhas[i].rstrip()
            if (not prox.strip()
                    or prox.startswith('#')
                    or re.match(r'^[-*]\s+', prox)
                    or re.match(r'^\d+\.\s+', prox)):
                break
            bloco.append(prox)
            i += 1

        txt = _inline(' '.join(bloco))
        fl.append(Paragraph(txt, estilos['corpo']))

    return fl


# ════════════════════════════════════════════════════════════════════════════
# ESTILOS
# ════════════════════════════════════════════════════════════════════════════

def _estilos():
    base = getSampleStyleSheet()
    return {
        # documento
        'titulo': ParagraphStyle(
            'Titulo', parent=base['Normal'],
            fontName='Helvetica-Bold', fontSize=22,
            textColor=colors.HexColor('#a8893e'),  # dourado
            leading=28, spaceAfter=2,
        ),
        'subtitulo': ParagraphStyle(
            'Subtitulo', parent=base['Normal'],
            fontName='Helvetica', fontSize=10,
            textColor=colors.HexColor('#a8893e'),  # dourado
            spaceAfter=0,
        ),
        # card cliente
        'label': ParagraphStyle(
            'Label', parent=base['Normal'],
            fontName='Helvetica-Bold', fontSize=7.5,
            textColor=GOLD_DARK, leading=10, spaceAfter=2,
        ),
        'valor': ParagraphStyle(
            'Valor', parent=base['Normal'],
            fontName='Helvetica', fontSize=9,
            textColor=NAVY, leading=12,
        ),
        # corpo do diagnóstico
        'corpo': ParagraphStyle(
            'Corpo', parent=base['Normal'],
            fontName='Helvetica', fontSize=10,
            textColor=colors.HexColor('#2c2c3e'),
            alignment=TA_JUSTIFY, spaceAfter=10, spaceBefore=4, leading=16,
        ),
        'h2': ParagraphStyle(
            'H2', parent=base['Normal'],
            fontName='Helvetica-Bold', fontSize=12,
            textColor=GOLD, leading=16, spaceAfter=4, spaceBefore=14,
        ),
        'h3': ParagraphStyle(
            'H3', parent=base['Normal'],
            fontName='Helvetica-Bold', fontSize=10.5,
            textColor=GOLD_DARK, leading=14, spaceAfter=5, spaceBefore=10,
        ),
        'bullet': ParagraphStyle(
            'Bullet', parent=base['Normal'],
            fontName='Helvetica', fontSize=9.5,
            textColor=colors.HexColor('#2c2c3e'),
            leading=14, spaceAfter=5, spaceBefore=2,
            leftIndent=12,
        ),
        # tabela Q&A
        'pergunta_idx': ParagraphStyle(
            'PerguntaIdx', parent=base['Normal'],
            fontName='Helvetica-Bold', fontSize=8.5,
            textColor=GOLD_DARK, alignment=TA_CENTER,
        ),
        'pergunta_txt': ParagraphStyle(
            'PerguntaTxt', parent=base['Normal'],
            fontName='Helvetica', fontSize=8.5,
            textColor=NAVY, leading=12, spaceAfter=2,
        ),
        'pilar': ParagraphStyle(
            'Pilar', parent=base['Normal'],
            fontName='Helvetica', fontSize=7.5,
            textColor=MUTED, leading=10,
        ),
        'resposta_txt': ParagraphStyle(
            'RespostaTxt', parent=base['Normal'],
            fontName='Helvetica', fontSize=8.5,
            textColor=colors.HexColor('#2c2c3e'), leading=12,
        ),
        'rodape': ParagraphStyle(
            'Rodape', parent=base['Normal'],
            fontName='Helvetica', fontSize=7.5,
            textColor=MUTED, alignment=TA_CENTER,
        ),
    }


# ════════════════════════════════════════════════════════════════════════════
# HELPERS DE LAYOUT
# ════════════════════════════════════════════════════════════════════════════

def _capa(elements, titulo, subtitulo, estilos):
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        '<font color="#a8893e">RAIO X</font>'
        ' <font color="#1a1a2e">COMERCIAL</font>',
        ParagraphStyle('Logo', fontName='Helvetica-Bold', fontSize=11,
                       textColor=NAVY, letterSpacing=3, spaceAfter=4),
    ))
    elements.append(GoldRule(thickness=1, color=BORDER, spaceAfter=16))
    elements.append(Paragraph(titulo,    estilos['titulo']))
    elements.append(Paragraph(subtitulo, estilos['subtitulo']))
    elements.append(Spacer(1, 14))
    elements.append(GoldRule(thickness=2.5, color=GOLD, spaceAfter=20))


def _card_cliente(cliente, estilos, campos=None):
    campos = campos or ['nome', 'cargo', 'empresa', 'email', 'telefone', 'cidade']
    labels = {
        'nome': 'Nome', 'cargo': 'Cargo', 'empresa': 'Empresa',
        'email': 'E-mail', 'telefone': 'Telefone', 'cidade': 'Cidade',
    }
    pares = [(labels[k], cliente.get(k, '—')) for k in campos if k in labels]
    pares.append(('Data de geração',
                  datetime.now().strftime('%d/%m/%Y  às  %H:%M')))

    rows = []
    for i in range(0, len(pares), 2):
        l = pares[i]
        r = pares[i + 1] if i + 1 < len(pares) else ('', '')
        rows.append([
            [Paragraph(l[0], estilos['label']), Paragraph(str(l[1]), estilos['valor'])],
            [Paragraph(r[0], estilos['label']), Paragraph(str(r[1]), estilos['valor'])],
        ])

    t = Table(rows, colWidths=[245, 245])
    t.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, SURFACE]),
        ('TOPPADDING',     (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 8),
        ('LEFTPADDING',    (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 12),
        ('LINEBELOW',      (0, 0), (-1, -2), 0.5, BORDER),
        ('LINEBELOW',      (0, -1),(-1, -1), 1.5, GOLD),
        ('BOX',            (0, 0), (-1, -1), 1,   BORDER),
    ]))
    return t


# ════════════════════════════════════════════════════════════════════════════
# UTILITÁRIOS
# ════════════════════════════════════════════════════════════════════════════

def criar_diretorio_se_nao_existe(diretorio):
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)


def carregar_perguntas():
    try:
        with open('knowledge/questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)['perguntas']
    except Exception as e:
        print(f'Erro ao carregar perguntas: {e}')
        return []


# ════════════════════════════════════════════════════════════════════════════
# PDF 1 — DIAGNÓSTICO EXECUTIVO
# ════════════════════════════════════════════════════════════════════════════

def gerar_pdf_diagnostico(cliente, diagnostico):
    criar_diretorio_se_nao_existe('diagnosticos')
    caminho = f"diagnosticos/Raio-X_Comercial_{cliente['empresa']}.pdf"

    print(f"DEBUG - Cliente recebido: {cliente}")

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        rightMargin=MARGIN, leftMargin=MARGIN,
        topMargin=MARGIN,   bottomMargin=50,
        title=f"Diagnóstico — {cliente.get('nome', '')}",
        author='Raio X Comercial',
    )

    s  = _estilos()
    el = []

    _capa(el, 'Diagnóstico Comercial',
          'Análise Executiva — Confidencial', s)

    el.append(SectionHeader('Identificação do Cliente'))
    el.append(Spacer(1, 8))
    el.append(_card_cliente(cliente, s, campos=['nome', 'cargo', 'empresa', 'email', 'telefone', 'cidade']))
    el.append(Spacer(1, 22))

    el.append(SectionHeader('Diagnóstico & Análise'))
    el.append(Spacer(1, 10))

    el += _md_para_flowables(diagnostico, s)

    el.append(Spacer(1, 28))
    el.append(GoldRule(thickness=0.8, color=BORDER, spaceAfter=8))
    el.append(Paragraph(
        'Este diagnóstico foi gerado automaticamente pelo sistema Raio X Comercial. '
        'Documento confidencial — uso interno e exclusivo do destinatário.',
        s['rodape'],
    ))

    doc.build(el)
    print(f'PDF diagnóstico gerado: {caminho}')
    return caminho


# ════════════════════════════════════════════════════════════════════════════
# PDF 2 — PERGUNTAS & RESPOSTAS
# ════════════════════════════════════════════════════════════════════════════

def gerar_pdf_respostas(cliente, respostas):
    criar_diretorio_se_nao_existe('respostas')
    caminho = f"respostas/Respostas_Raio-X_{cliente['empresa']}.pdf"

    perguntas = carregar_perguntas()

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        rightMargin=36, leftMargin=36,
        topMargin=MARGIN, bottomMargin=50,
        title=f"Respostas — {cliente.get('nome', '')}",
        author='Raio X Comercial',
    )

    s  = _estilos()
    el = []

    _capa(el, 'Perguntas & Respostas',
          'Diagnóstico Completo — Visão Detalhada', s)

    el.append(SectionHeader('Identificação do Cliente'))
    el.append(Spacer(1, 8))
    el.append(_card_cliente(cliente, s, campos=['nome', 'cargo', 'empresa', 'email', 'telefone', 'cidade']))
    el.append(Spacer(1, 22))

    # ── Agrupar por pilar ─────────────────────────────────────────────────
    pilares = {}
    for p in sorted(perguntas, key=lambda x: x.get('id', 0)):
        pilar = p.get('pilar_nome', 'Geral')
        pilares.setdefault(pilar, []).append(p)

    st_th = ParagraphStyle('TH', fontName='Helvetica-Bold',
                           fontSize=8.5, textColor=WHITE)
    st_th_c = ParagraphStyle('THC', fontName='Helvetica-Bold',
                             fontSize=8.5, textColor=WHITE,
                             alignment=TA_CENTER)

    for pilar_nome, pergs in pilares.items():
        el.append(KeepTogether([SectionHeader(pilar_nome), Spacer(1, 8)]))

        rows = [[
            Paragraph('#',        st_th_c),
            Paragraph('Pergunta', st_th),
            Paragraph('Resposta', st_th),
        ]]

        for idx, perg in enumerate(pergs, 1):
            pid   = perg.get('id')
            texto = perg.get('pergunta', '')
            pilar = perg.get('pilar_nome', '')

            resp = respostas.get(f'pergunta_{pid}') or respostas.get(str(pid)) or respostas.get(pid) or ''
            if isinstance(resp, list):
                resp = ', '.join(resp)
            resp = str(resp).strip() or '—'
            if len(resp) > 220:
                resp = resp[:220] + '…'

            rows.append([
                Paragraph(str(idx), s['pergunta_idx']),
                [Paragraph(texto, s['pergunta_txt']),
                 Paragraph(pilar, s['pilar'])],
                Paragraph(resp,   s['resposta_txt']),
            ])

        t = Table(rows, colWidths=[22, 258, 240])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0),  NAVY),
            ('TOPPADDING',    (0, 0), (-1, 0),  10),
            ('BOTTOMPADDING', (0, 0), (-1, 0),  10),
            ('LEFTPADDING',   (0, 0), (-1, 0),  8),
            ('RIGHTPADDING',  (0, 0), (-1, 0),  8),
            ('LINEBELOW',     (0, 0), (-1, 0),  2,   GOLD),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, SURFACE]),
            ('TOPPADDING',    (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 9),
            ('LEFTPADDING',   (0, 1), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 1), (-1, -1), 8),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('ALIGN',         (0, 1), (0,  -1), 'CENTER'),
            ('GRID',          (0, 1), (-1, -1), 0.5, BORDER),
            ('LINEAFTER',     (0, 0), (0,  -1), 0.5, BORDER),
        ]))

        el.append(t)
        el.append(Spacer(1, 18))

    el.append(GoldRule(thickness=0.8, color=BORDER, spaceAfter=8))
    el.append(Paragraph(
        'Documento gerado automaticamente pelo sistema Raio X Comercial. '
        'Confidencial — uso interno apenas.',
        s['rodape'],
    ))

    doc.build(el)
    print(f'PDF respostas gerado: {caminho}')
    return caminho