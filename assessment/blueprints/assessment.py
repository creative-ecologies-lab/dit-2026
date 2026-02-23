from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, current_app
from config import settings as app_settings

bp = Blueprint('assessment', __name__)


@bp.route('/')
def index():
    has_llm = bool([p for p in current_app.llm_registry.get_available_providers() if p['available']])
    return render_template('index.html', has_llm=has_llm)


@bp.route('/assess')
def assess():
    from assessment.questions import get_all_sae_questions
    questions = get_all_sae_questions()
    cohort = request.args.get('cohort', '').strip().lower() or ''
    return render_template('assessment.html', questions=questions, cohort=cohort)


@bp.route('/api/assess', methods=['POST'])
def submit_assessment():
    from assessment.scorer import score_assessment
    from assessment.matrix import get_placement
    data = request.get_json()
    # Separate intake fields from assessment answers
    cohort = data.pop('cohort', None)
    age_range = data.pop('age_range', None)
    role = data.pop('role', None)
    score = score_assessment(data)
    placement = get_placement(score)
    # Store anonymous result (fire-and-forget)
    try:
        from storage import store_result
        store_result(
            score['sae_level'], score['epias_stage'],
            cohort=cohort, age_range=age_range, role=role,
        )
    except Exception as e:
        current_app.logger.warning(f"Failed to store result: {e}")
    # Include cohort in response so results page can link to cohort heatmap
    if cohort:
        placement['cohort'] = cohort.strip().lower()
    # Find relevant growth path chunks via search
    query = f"growth path for SAE L{placement['sae_level']} {placement['epias_stage']}"
    chunks = current_app.search_engine.search(query, top_k=5)
    placement['growth_chunks'] = [{'text': c['text'], 'section': c.get('section_title', ''), 'source': c.get('source_file', '')} for c in chunks]
    return jsonify(placement)


@bp.route('/results')
def results():
    return render_template('results.html')


@bp.route('/heatmap')
@bp.route('/heatmap/<cohort_code>')
def heatmap(cohort_code=None):
    if cohort_code:
        cohort_code = cohort_code.strip().lower()
    return render_template('heatmap.html', cohort=cohort_code or '')


@bp.route('/settings')
def settings():
    return render_template('settings.html')


# Ordered list of source documents with short labels
# Index 0 is the overview tab (rendered from template, not a file)
_FRAMEWORK_DOCS = [
    (None, 'At a Glance'),
    ('ai-upskilling-for-product-designers.md', 'Overview'),
    ('ai-upskilling-for-product-designers-L1-to-L2.md', 'L1 to L2'),
    ('ai-upskilling-for-product-designers-L2-to-L3.md', 'L2 to L3'),
    ('ai-upskilling-for-product-designers-L3-L4.md', 'L3 to L4'),
    ('ai-upskilling-for-uxr.md', 'UX Research'),
]

_OVERVIEW_HTML = """
<h2>About the E-P-I-A-S &times; SAE Framework</h2>
<p>From John Maeda's <strong>Design in Tech Report 2026: From UX to AX</strong>, presented at <a href="https://schedule.sxsw.com/2026/events/PP1148536" target="_blank">SXSW 2026</a>. This framework maps AI adoption for product designers along two axes:</p>
<div class="framework-axes">
    <div class="axis">
        <h3>SAE Levels (Automation)</h3>
        <table class="mini-table">
            <tr><td><strong>L0</strong></td><td>Manual &mdash; Classical Designer</td></tr>
            <tr><td><strong>L1</strong></td><td>AI-Assisted &mdash; Marketing Designer &times; AI</td></tr>
            <tr><td><strong>L2</strong></td><td>Partially Automated &mdash; Product Designer &times; AI</td></tr>
            <tr><td><strong>L3</strong></td><td>Guided Automation &mdash; Design Engineer &times; AI</td></tr>
            <tr><td><strong>L4</strong></td><td>Mostly Automated &mdash; Super Design Engineer &times; AI</td></tr>
            <tr><td><strong>L5</strong></td><td>Full Automation &mdash; AI &times; AI (aspirational)</td></tr>
        </table>
    </div>
    <div class="axis">
        <h3>E-P-I-A-S (Maturity)</h3>
        <table class="mini-table">
            <tr><td><strong>E</strong></td><td>Explorer &mdash; trying things, learning basics</td></tr>
            <tr><td><strong>P</strong></td><td>Practitioner &mdash; consistent habits</td></tr>
            <tr><td><strong>I</strong></td><td>Integrator &mdash; part of workflow</td></tr>
            <tr><td><strong>A</strong></td><td>Architect &mdash; systems others use</td></tr>
            <tr><td><strong>S</strong></td><td>Steward &mdash; setting standards</td></tr>
        </table>
    </div>
</div>
<blockquote class="key-insight">
    &ldquo;An S-Steward at L1 is more valuable than an E-Explorer at L4. Depth of judgment beats breadth of tooling.&rdquo;
    <cite>&mdash; John Maeda, DIT 2026</cite>
</blockquote>
<p class="evolving-note">This framework is a living document. The source content may have been updated since this app was built. Check the <a href="https://github.com/aji-ai/dit-2026" target="_blank">GitHub repository</a> for the latest version.</p>
"""


@bp.route('/framework')
@bp.route('/framework/<int:doc_index>')
def framework(doc_index=0):
    doc_index = max(0, min(doc_index, len(_FRAMEWORK_DOCS) - 1))
    filename, label = _FRAMEWORK_DOCS[doc_index]

    if filename is None:
        # Overview tab — rendered from static HTML
        html_content = _OVERVIEW_HTML
    else:
        filepath = app_settings.source_dir / filename
        raw_md = filepath.read_text(encoding='utf-8')
        html_content = _render_markdown(raw_md)

    tabs = [{'label': lbl, 'index': i, 'active': i == doc_index}
            for i, (_, lbl) in enumerate(_FRAMEWORK_DOCS)]
    return render_template('framework.html', tabs=tabs, content=html_content,
                           current_label=label)


def _render_markdown(md: str) -> str:
    """Convert markdown to HTML. Handles headings, bold, italic, code,
    lists, tables, blockquotes, and horizontal rules."""
    import re

    def esc(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def inline(s):
        s = esc(s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
        s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
        # Images before links (both use []() syntax)
        s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', s)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', s)
        return s

    lines = md.split('\n')
    out = []
    in_table = False
    header_done = False
    list_type = None

    def close_list():
        nonlocal list_type
        if list_type:
            out.append(f'</{list_type}>')
            list_type = None

    for line in lines:
        stripped = line.strip()

        # Table rows
        if stripped.startswith('|'):
            close_list()
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(re.match(r'^[-:\s]+$', c) for c in cells):
                header_done = True
                continue
            if not in_table:
                out.append('<table class="chunk-table">')
                in_table = True
                header_done = False
            if not header_done:
                out.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
            else:
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
            continue
        if in_table:
            out.append('</tbody></table>')
            in_table = False
            header_done = False

        # Blank line
        if not stripped:
            close_list()
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', stripped):
            close_list()
            out.append('<hr>')
            continue

        # Headings
        hm = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if hm:
            close_list()
            level = len(hm.group(1))
            out.append(f'<h{level}>{inline(hm.group(2))}</h{level}>')
            continue

        # Blockquote
        if stripped.startswith('>'):
            close_list()
            text = stripped.lstrip('>').strip()
            out.append(f'<blockquote>{inline(text)}</blockquote>')
            continue

        # Unordered list
        um = re.match(r'^(\s*)[-*]\s+(.*)', line)
        if um:
            if list_type != 'ul':
                close_list()
                out.append('<ul>')
                list_type = 'ul'
            out.append(f'<li>{inline(um.group(2))}</li>')
            continue

        # Ordered list
        om = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if om:
            if list_type != 'ol':
                close_list()
                out.append('<ol>')
                list_type = 'ol'
            out.append(f'<li>{inline(om.group(2))}</li>')
            continue

        # Regular paragraph
        close_list()
        out.append(f'<p>{inline(stripped)}</p>')

    close_list()
    if in_table:
        out.append('</tbody></table>')
    return '\n'.join(out)
