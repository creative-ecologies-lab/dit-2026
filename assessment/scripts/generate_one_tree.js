/**
 * Generate a single organism-only SVG.
 *
 * Usage: node generate_one_tree.js <rd> <cw> <ch> <seed> [outfile]
 *
 * If outfile is provided, writes there. Otherwise prints to stdout.
 */

const fs = require('fs');
const path = require('path');

const window = {};
const treeVizCode = fs.readFileSync(
    path.join(__dirname, '..', 'static', 'tree-viz.js'), 'utf8'
);
eval(treeVizCode);

const { generateOrganismSVG, W, H } = window.TreeViz;

const [,, rdStr, cwStr, chStr, seedStr, outFile] = process.argv;
const rd = parseInt(rdStr), cw = parseInt(cwStr), ch = parseInt(chStr);
const seed = parseInt(seedStr) || 42;

const viz = { root_depth: rd, root_spread: rd, canopy_width: cw, canopy_height: ch, seed: seed };
const org = generateOrganismSVG(viz);
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">${org}</svg>`;

if (outFile) {
    fs.mkdirSync(path.dirname(outFile), { recursive: true });
    fs.writeFileSync(outFile, svg);
} else {
    process.stdout.write(svg);
}
