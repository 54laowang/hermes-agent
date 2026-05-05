#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kami PDF 生成器 - ReportLab 版本
用途：当 WeasyPrint 依赖失败时，使用此脚本生成 PDF

用法：
    python3 generate_pdf.py <content_file> [output_path]

示例：
    python3 generate_pdf.py report.md ~/Desktop/report.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

# 颜色定义（Kami 设计规范）
INK = HexColor('#1B365D')
TEXT = HexColor('#2c2c2c')
MUTED = HexColor('#6b6b6b')
BORDER = HexColor('#d4d3c8')
RISK_RED = HexColor('#b43c3c')

# 注册中文字体
font_paths = [
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
]

font_registered = False
for font_path in font_paths:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
            font_registered = True
            break
        except:
            continue

font_name = 'ChineseFont' if font_registered else 'Helvetica'

def create_styles():
    """创建 Kami 风格样式"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        'KamiTitle',
        fontName=font_name,
        fontSize=22,
        textColor=INK,
        spaceAfter=4*mm,
        leading=26
    ))
    
    styles.add(ParagraphStyle(
        'KamiSubtitle',
        fontName=font_name,
        fontSize=11,
        textColor=MUTED,
        spaceAfter=8*mm
    ))
    
    styles.add(ParagraphStyle(
        'KamiSection',
        fontName=font_name,
        fontSize=14,
        textColor=INK,
        spaceBefore=8*mm,
        spaceAfter=4*mm
    ))
    
    styles.add(ParagraphStyle(
        'KamiSubsection',
        fontName=font_name,
        fontSize=12,
        textColor=INK,
        spaceBefore=5*mm,
        spaceAfter=3*mm
    ))
    
    styles.add(ParagraphStyle(
        'KamiBody',
        fontName=font_name,
        fontSize=10.5,
        textColor=TEXT,
        spaceAfter=3*mm,
        leading=16,
        alignment=TA_JUSTIFY
    ))
    
    styles.add(ParagraphStyle(
        'KamiMeta',
        fontName=font_name,
        fontSize=8,
        textColor=MUTED,
        spaceAfter=6*mm
    ))
    
    styles.add(ParagraphStyle(
        'KamiFooter',
        fontName=font_name,
        fontSize=8,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=6*mm
    ))
    
    return styles

def create_table(data, col_widths):
    """创建 Kami 风格表格"""
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), INK),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), HexColor('#f5f4ed')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
    ]))
    return table

def generate_pdf(output_path, content_func):
    """
    生成 PDF 文件
    
    Args:
        output_path: 输出 PDF 路径
        content_func: 内容生成函数，接收 (story, styles) 参数
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    styles = create_styles()
    story = []
    
    # 调用内容生成函数
    content_func(story, styles)
    
    # 生成 PDF
    doc.build(story)
    print(f'✅ PDF 已生成：{output_path}')

# 使用示例
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 generate_pdf.py <output_path>')
        print('提示: 这是一个框架脚本，请复制并修改内容生成函数')
        sys.exit(1)
    
    output = os.path.expanduser(sys.argv[1])
    
    def sample_content(story, styles):
        """示例内容 - 替换为实际内容"""
        story.append(Paragraph('报告标题', styles['KamiTitle']))
        story.append(Paragraph('副标题', styles['KamiSubtitle']))
        story.append(Paragraph('报告日期：2026-05-02', styles['KamiMeta']))
        
        story.append(Paragraph('一、章节标题', styles['KamiSection']))
        story.append(Paragraph('正文内容...', styles['KamiBody']))
    
    generate_pdf(output, sample_content)
