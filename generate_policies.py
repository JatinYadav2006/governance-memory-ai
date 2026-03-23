from pathlib import Path

policy_dir = Path('assets/policies')
policy_dir.mkdir(parents=True, exist_ok=True)

try:
    from fpdf import FPDF
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fpdf'])
    from fpdf import FPDF

policies = {
    'flood_response_policy.pdf': [
        'City Flood Response Policy',
        '1. Purpose: Provide clear operational duties when flood threats are detected.',
        '2. Scope: Applies to city services, utilities, and emergency management units.',
        '3. Action: Activate early-warning systems, open community shelters, and deploy drain maintenance crews.',
        '4. Communication: Provide public alerts via SMS, radio, and official portals.',
        '5. Review: Conduct after-action assessment and update procedures annually.',
    ],
    'electricity_outage_policy.pdf': [
        'Power Outage Management Policy',
        '1. Purpose: Ensure safe and timely recovery from electrical outages.',
        '2. Scope: Covers grid faults, storms, and scheduled maintenance in municipal zones.',
        '3. Action: Dispatch repair teams, coordinate with utility provider, and update outage map.',
        '4. Safety: Enforce barricades around exposed cables and grids.',
        '5. Follow-up: Log incident, customer communications, and power-restoration time.',
    ],
    'water_sanitation_policy.pdf': [
        'Water Sanitation and Quality Policy',
        '1. Purpose: Maintain safe drinking water and sanitation standards.',
        '2. Scope: Includes distribution network, treatment plants, and source protection.',
        '3. Action: Test samples weekly, repair contamination sources, and inform public of boil orders.',
        '4. Waste: Manage sewage disposal and canal cleaning to avoid overflow.',
        '5. Education: Carry out community hygiene campaigns.',
    ],
    'road_maintenance_policy.pdf': [
        'Road Maintenance and Pothole Repair Policy',
        '1. Purpose: Provide safe, passable transportation infrastructure.',
        '2. Scope: Applies to urban roadways, sidewalks, and transit lanes.',
        '3. Action: Schedule inspections, prioritize high-traffic roads, and appoint repair crews.',
        '4. Monitoring: Use citizen reports for emergent potholes and surface damage.',
        '5. Quality: Document completion with before/after images and closure reports.',
    ],
    'waste_collection_policy.pdf': [
        'Solid Waste Collection and Recycling Policy',
        '1. Purpose: Reduce litter and improve recyclable recovery.',
        '2. Scope: Covers residential, commercial, and public-area waste streams.',
        '3. Action: Enforce collection schedule, provide recycling bins, and penalize illegal dumping.',
        '4. Programs: Offer education and composting incentives.',
        '5. Audit: Track tons collected and diversion rates.',
    ],
}

for filename, lines in policies.items():
    path = policy_dir / filename
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, lines[0], ln=True)
    pdf.ln(4)
    pdf.set_font('Arial', '', 12)
    for line in lines[1:]:
        pdf.multi_cell(0, 8, line)
    pdf.output(str(path))

print('created', len(policies), 'policy PDFs in', policy_dir)
for f in sorted(policy_dir.glob('*.pdf')):
    print('-', f.name)
