/**
 * Pre-generate all possible tree SVGs.
 *
 * Run: node assessment/scripts/generate_trees.js
 *
 * Combinations:
 *   root_depth 1-5 × canopy_width 0 × canopy_height 0  =  5
 *   root_depth 1-5 × canopy_width 1-5 × canopy_height 1-5 = 125
 *   Total: 130 SVG files
 *
 * Output: assessment/static/trees/r{1-5}_c{0-5}_h{0-5}.svg
 */

const fs = require('fs');
const path = require('path');

// Load tree-viz.js by simulating browser globals
const window = {};
const treeVizCode = fs.readFileSync(
    path.join(__dirname, '..', 'static', 'tree-viz.js'), 'utf8'
);
eval(treeVizCode);
const { generateTreeSVG, generateOrganismSVG, generateMiniOrganismSVG, CX, GY, W, H } = window.TreeViz;

const outDir = path.join(__dirname, '..', 'static', 'trees');
fs.mkdirSync(outDir, { recursive: true });
const orgDir = path.join(outDir, 'org');
fs.mkdirSync(orgDir, { recursive: true });
const miniDir = path.join(outDir, 'mini');
fs.mkdirSync(miniDir, { recursive: true });

let count = 0;

for (let rd = 1; rd <= 5; rd++) {
    // L0 canopy (no AI)
    const viz0 = { root_depth: rd, root_spread: rd, canopy_width: 0, canopy_height: 0 };
    const meta0 = { balance: 'grounded', root_code: `L0-${'EPIAS'[rd-1]}`, canopy_code: null };
    const svg0 = generateTreeSVG(viz0, meta0);
    const fname0 = `r${rd}_c0_h0.svg`;
    fs.writeFileSync(path.join(outDir, fname0), svg0);

    // Organism-only SVG (no background/grid/arcs/labels)
    const org0 = generateOrganismSVG(viz0);
    const orgSvg0 = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">${org0}</svg>`;
    fs.writeFileSync(path.join(orgDir, fname0), orgSvg0);

    // Mini organism for forest view (~1KB)
    const mini0 = generateMiniOrganismSVG(viz0);
    const miniSvg0 = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">${mini0}</svg>`;
    fs.writeFileSync(path.join(miniDir, fname0), miniSvg0);
    count++;

    // L1-L5 canopy
    for (let cw = 1; cw <= 5; cw++) {
        for (let ch = 1; ch <= 5; ch++) {
            const viz = { root_depth: rd, root_spread: rd, canopy_width: cw, canopy_height: ch };
            // Compute balance for meta label
            const demand = cw * 2 + ch * 2;
            const capacity = rd * 5;
            const ratio = demand / capacity;
            let balance;
            if (ratio <= 0.6) balance = 'deeply rooted';
            else if (ratio <= 1.1) balance = 'balanced';
            else if (ratio <= 1.8) balance = 'reaching';
            else balance = 'top-heavy';

            const stages = ['', 'E', 'P', 'I', 'A', 'S'];
            const meta = {
                balance: balance,
                root_code: `L0-${stages[rd]}`,
                canopy_code: `L${cw}-${stages[ch]}`,
            };

            const svg = generateTreeSVG(viz, meta);
            const fname = `r${rd}_c${cw}_h${ch}.svg`;
            fs.writeFileSync(path.join(outDir, fname), svg);

            // Organism-only SVG
            const org = generateOrganismSVG(viz);
            const orgSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">${org}</svg>`;
            fs.writeFileSync(path.join(orgDir, fname), orgSvg);

            // Mini organism for forest view
            const mini = generateMiniOrganismSVG(viz);
            const miniSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">${mini}</svg>`;
            fs.writeFileSync(path.join(miniDir, fname), miniSvg);
            count++;
        }
    }
}

console.log(`Generated ${count} tree SVGs in ${outDir}`);
