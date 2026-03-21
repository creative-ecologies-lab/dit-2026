from pathlib import Path
from flask import Blueprint, render_template, request, jsonify, current_app
from config import settings as app_settings

bp = Blueprint('assessment', __name__)


def index():
    from assessment.scorer import SAE_NAMES, STAGE_NAMES
    heatmap_total = 0
    heatmap_counts = {}
    try:
        from storage import get_heatmap_data
        hm = get_heatmap_data(include_test=False)
        heatmap_total = hm.get('total', 0)
        heatmap_counts = hm.get('counts', {})
    except Exception:
        pass
    from assessment.matrix import MATRIX_DATA
    cell_descriptions = {f"{lvl}_{stg}": desc for (lvl, stg), desc in MATRIX_DATA.items()}
    return render_template('index.html',
                           heatmap_total=heatmap_total,
                           heatmap_counts=heatmap_counts,
                           cell_descriptions=cell_descriptions,
                           sae_names=SAE_NAMES,
                           stage_names=STAGE_NAMES,
                           stage_descriptions=_STAGE_DESCRIPTIONS,
                           level_descriptions=_LEVEL_DESCRIPTIONS,
                           stage_order=['E', 'P', 'I', 'A', 'S'])


@bp.route('/about')
def about():
    from assessment.scorer import SAE_NAMES, STAGE_NAMES
    from assessment.matrix import MATRIX_DATA
    heatmap_total = 0
    heatmap_counts = {}
    try:
        from storage import get_heatmap_data
        hm = get_heatmap_data(include_test=False)
        heatmap_total = hm.get('total', 0)
        heatmap_counts = hm.get('counts', {})
    except Exception:
        pass
    cell_descriptions = {f"{lvl}_{stg}": desc for (lvl, stg), desc in MATRIX_DATA.items()}
    return render_template('about.html',
                           heatmap_total=heatmap_total,
                           heatmap_counts=heatmap_counts,
                           cell_descriptions=cell_descriptions,
                           sae_names=SAE_NAMES,
                           stage_names=STAGE_NAMES,
                           stage_descriptions=_STAGE_DESCRIPTIONS,
                           level_descriptions=_LEVEL_DESCRIPTIONS,
                           stage_order=['E', 'P', 'I', 'A', 'S'])


@bp.route('/')
@bp.route('/tree')
@bp.route('/tree/v2/explore')
def tree_gallery():
    from storage import get_forest_svg
    trees_svg, forest_svg, stats = get_forest_svg()
    return render_template('tree-gallery.html',
                           trees_svg=trees_svg, forest_svg=forest_svg,
                           stats=stats)


@bp.route('/tree/forest')
def tree_forest():
    from storage import get_forest_svg
    group = (request.args.get('group') or request.args.get('cohort', '')).strip().lower() or None
    trees_svg, forest_svg, stats = get_forest_svg(cohort=group)
    return render_template('forest.html',
                           trees_svg=trees_svg,
                           forest_svg=forest_svg,
                           stats=stats,
                           group=group)


@bp.route('/tree/v2')
def assess_v2():
    from assessment.questions import get_all_sae_questions, get_root_questions
    questions_design = get_all_sae_questions(role='design')
    questions_uxr = get_all_sae_questions(role='uxr')
    root_design = get_root_questions(role='design')
    root_uxr = get_root_questions(role='uxr')
    cohort = (request.args.get('group') or request.args.get('cohort', '')).strip().lower()
    return render_template('assessment-v2.html',
                           questions_design=questions_design,
                           questions_uxr=questions_uxr,
                           root_questions_design=root_design,
                           root_questions_uxr=root_uxr,
                           cohort=cohort)


@bp.route('/api/assess-v2', methods=['POST'])
def submit_assessment_v2():
    from assessment.scorer import score_assessment_v2
    from assessment.matrix import get_placement_v2
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400
    cohort = (data.pop('cohort', '') or '')[:64].strip().lower() or None
    role = data.pop('role', None)
    if role not in ('design', 'uxr', None):
        role = None
    utm_source = (data.pop('utm_source', '') or '')[:100].strip() or None
    utm_medium = (data.pop('utm_medium', '') or '')[:100].strip() or None
    utm_campaign = (data.pop('utm_campaign', '') or '')[:100].strip() or None
    session_id = (data.pop('session_id', '') or '')[:64].strip() or None
    tree_id = (data.pop('tree_id', '') or '')[:10].strip().upper() or None
    raw_answers = dict(data)
    score = score_assessment_v2(data, role=role or 'design')
    placement = get_placement_v2(score)
    try:
        from storage import store_result, store_tree_result
        # Legacy v1 heatmap storage (sae_level × epias_stage)
        store_result(
            score['sae_level'],
            score.get('canopy_stage') or score['root_stage'],
            cohort=cohort, role=role,
            answers=raw_answers,
            sae_distribution=score.get('sae_distribution'),
            epias_distribution=score.get('root_distribution'),
            referrer=request.referrer,
            ua=request.headers.get('User-Agent', ''),
            utm_source=utm_source, utm_medium=utm_medium, utm_campaign=utm_campaign,
        )
        # V2 tree storage (3D: root_depth × canopy_width × canopy_height)
        # Generates a unique organism SVG seeded by session_id
        store_tree_result(
            score['root_numeric'],
            score['sae_level'],
            score['canopy_numeric'],
            tree_id=tree_id,
            session_id=session_id or tree_id,
            cohort=cohort, role=role,
            balance=score.get('balance'),
            tree_species=score.get('tree_species'),
            root_stage=score.get('root_stage'),
            canopy_stage=score.get('canopy_stage'),
            answers=raw_answers,
            referrer=request.referrer,
            ua=request.headers.get('User-Agent', ''),
            utm_source=utm_source, utm_medium=utm_medium, utm_campaign=utm_campaign,
        )
    except Exception as e:
        current_app.logger.warning(f"Failed to store v2 result: {e}")
    if cohort:
        placement['cohort'] = cohort
    if tree_id:
        placement['tree_id'] = tree_id
    return jsonify(placement)


@bp.route('/tree/v2/results')
def results_v2():
    from assessment.scorer import SAE_NAMES, STAGE_NAMES
    from storage import get_forest_svg
    trees_svg, forest_svg, stats = get_forest_svg()
    return render_template('results-v2.html',
                           sae_names=SAE_NAMES, stage_names=STAGE_NAMES,
                           trees_svg=trees_svg, forest_svg=forest_svg,
                           stats=stats)


@bp.route('/assess')
def assess():
    from assessment.questions import get_all_sae_questions
    questions_design = get_all_sae_questions(role='design')
    questions_uxr = get_all_sae_questions(role='uxr')
    cohort = (request.args.get('group') or request.args.get('cohort', '')).strip().lower()
    return render_template('assessment.html',
                           questions_design=questions_design,
                           questions_uxr=questions_uxr,
                           cohort=cohort)


@bp.route('/api/assess', methods=['POST'])
def submit_assessment():
    from assessment.scorer import score_assessment
    from assessment.matrix import get_placement
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400
    # Separate and sanitize intake fields
    cohort = (data.pop('cohort', '') or '')[:64].strip().lower() or None
    age_range = (data.pop('age_range', '') or '')[:32].strip() or None
    role = data.pop('role', None)
    if role not in ('design', 'uxr', None):
        role = None
    utm_source = (data.pop('utm_source', '') or '')[:100].strip() or None
    utm_medium = (data.pop('utm_medium', '') or '')[:100].strip() or None
    utm_campaign = (data.pop('utm_campaign', '') or '')[:100].strip() or None
    # data now contains only answers — score, then store a copy
    raw_answers = dict(data)
    score = score_assessment(data)
    placement = get_placement(score)
    # Store anonymous result (fire-and-forget)
    try:
        from storage import store_result
        store_result(
            score['sae_level'], score['epias_stage'],
            cohort=cohort, age_range=age_range, role=role,
            answers=raw_answers,
            sae_distribution=score.get('sae_distribution'),
            epias_distribution=score.get('epias_distribution'),
            referrer=request.referrer,
            ua=request.headers.get('User-Agent', ''),
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
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
    from assessment.scorer import SAE_NAMES, STAGE_NAMES
    from assessment.matrix import MATRIX_DATA
    cell_descriptions = {f"{lvl}_{stg}": desc for (lvl, stg), desc in MATRIX_DATA.items()}
    return render_template('results.html',
                           sae_names=SAE_NAMES, stage_names=STAGE_NAMES,
                           cell_descriptions=cell_descriptions,
                           stage_descriptions=_STAGE_DESCRIPTIONS,
                           level_descriptions=_LEVEL_DESCRIPTIONS)


@bp.route('/group-id')
@bp.route('/group')
@bp.route('/groups')
@bp.route('/group-ids')
def cohorts():
    return render_template('cohorts.html')



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

_ROLE_LABELS = {
    0: "Classical Designer", 1: "Marketing Designer &times; AI",
    2: "Product Designer &times; AI", 3: "Design Engineer &times; AI",
    4: "Super Design Engineer &times; AI",
    5: "AI &times; AI (aspirational)",
}

_STAGE_DESCRIPTIONS = {
    "E": "Experimenting and building intuition. Quality varies, still learning what works.",
    "P": "Consistent habits and repeatable techniques. Process is reliable.",
    "I": "Fully integrated into workflow with documented decisions and traceability.",
    "A": "Builds reusable systems and templates that others adopt and trust.",
    "S": "Sets organizational standards, mentors others, and governs practice.",
}

_LEVEL_DESCRIPTIONS = {
    0: "All work is manual. No AI tools in the workflow.",
    1: "AI used for ideas and drafts. Every step is human-directed.",
    2: "AI generates deliverables from specs. Human integration and QA.",
    3: "Multi-step AI workflows in an IDE with checkpoints and context.",
    4: "Autonomous agent harnesses with eval suites and escalation paths.",
    5: "AI runs the workflow. Humans set goals and review exceptions.",
}


def _build_overview_html() -> str:
    """Generate the At a Glance tab from canonical scorer constants.

    Pulls SAE_NAMES, STAGE_NAMES, and KEY_INSIGHT from the scorer/matrix
    modules so this tab stays in sync automatically.
    """
    from assessment.scorer import SAE_NAMES, STAGE_NAMES
    from assessment.matrix import KEY_INSIGHT

    sae_rows = "\n".join(
        f'            <tr><td><strong>L{lvl}</strong></td>'
        f'<td>{SAE_NAMES[lvl]} &mdash; {_ROLE_LABELS[lvl]}</td></tr>'
        for lvl in range(6)
    )
    stage_rows = "\n".join(
        f'            <tr><td><strong>{key}</strong></td>'
        f'<td>{STAGE_NAMES[key]} &mdash; {_STAGE_DESCRIPTIONS[key]}</td></tr>'
        for key in ["E", "P", "I", "A", "S"]
    )

    return f"""
<h2>About the E-P-I-A-S &times; SAE Framework</h2>
<p>From John Maeda's <strong>Design in Tech Report 2026: From UX to AX</strong>, presented at <a href="https://schedule.sxsw.com/2026/events/PP1148536" target="_blank">SXSW 2026</a>. This framework maps AI adoption for product designers along two axes:</p>
<div class="framework-axes">
    <div class="axis">
        <h3>SAE Levels (Automation)</h3>
        <table class="mini-table">
{sae_rows}
        </table>
    </div>
    <div class="axis">
        <h3>E-P-I-A-S (Maturity)</h3>
        <table class="mini-table">
{stage_rows}
        </table>
    </div>
</div>
<blockquote class="key-insight">
    &ldquo;{KEY_INSIGHT}&rdquo;
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
        # Overview tab — built from canonical scorer constants
        html_content = _build_overview_html()
    else:
        filepath = app_settings.source_dir / filename
        raw_md = filepath.read_text(encoding='utf-8')
        html_content = _render_markdown(raw_md)

    tabs = [{'label': lbl, 'index': i, 'active': i == doc_index}
            for i, (_, lbl) in enumerate(_FRAMEWORK_DOCS)]
    return render_template('framework.html', tabs=tabs, content=html_content,
                           current_label=label, active_index=doc_index)


def _render_markdown(md: str) -> str:
    """Convert markdown to HTML. Handles headings, bold, italic, code,
    lists, tables, blockquotes, and horizontal rules."""
    import re

    def slugify(s):
        return re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>', '', s).lower()).strip('-')

    slug_counts = {}

    def esc(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def inline(s):
        s = esc(s)
        # Restore <br> tags that esc() turned into &lt;br/&gt;
        s = re.sub(r'&lt;br\s*/?&gt;', '<br>', s)
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
    in_fence = False
    fence_buf = []

    def close_list():
        nonlocal list_type
        if list_type:
            out.append(f'</{list_type}>')
            list_type = None

    for line in lines:
        stripped = line.strip()

        # Fenced code blocks (``` ... ```)
        if stripped.startswith('```'):
            close_list()
            if not in_fence:
                in_fence = True
                fence_buf = []
            else:
                in_fence = False
                code_html = esc('\n'.join(fence_buf))
                out.append(f'<pre class="code-block"><code>{code_html}</code></pre>')
                fence_buf = []
            continue
        if in_fence:
            fence_buf.append(line)
            continue

        # Table rows
        if stripped.startswith('|'):
            close_list()
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(re.match(r'^[-:\s]+$', c) for c in cells):
                header_done = True
                continue
            if not in_table:
                out.append('<div class="table-scroll-wrap"><table class="chunk-table">')
                in_table = True
                header_done = False
            if not header_done:
                out.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
            else:
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
            continue
        if in_table:
            out.append('</tbody></table></div>')
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
            text = inline(hm.group(2))
            slug = slugify(text)
            slug_counts[slug] = slug_counts.get(slug, 0) + 1
            if slug_counts[slug] > 1:
                slug = f'{slug}-{slug_counts[slug]}'
            out.append(f'<h{level} id="{slug}">{text}</h{level}>')
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
        out.append('</tbody></table></div>')
    return '\n'.join(out)
