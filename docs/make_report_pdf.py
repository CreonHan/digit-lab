from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent


def build_pdf() -> None:
    markdown = (ROOT / "project_report.md").read_text(encoding="utf-8")
    output = ROOT / "project_report.pdf"
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ChineseTitle", parent=styles["Title"], fontName="STSong-Light", fontSize=18))
    styles.add(ParagraphStyle(name="ChineseHeading2", parent=styles["Heading2"], fontName="STSong-Light", fontSize=13))
    styles.add(ParagraphStyle(name="ChineseBody", parent=styles["BodyText"], fontName="STSong-Light", fontSize=9, leading=13))
    story = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 8))
            continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["ChineseTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["ChineseHeading2"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + line[2:], styles["ChineseBody"]))
        elif line.startswith("```"):
            continue
        else:
            story.append(Paragraph(line.replace("\\", "\\\\"), styles["ChineseBody"]))

    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    doc.build(story)
    print(output)


if __name__ == "__main__":
    build_pdf()
