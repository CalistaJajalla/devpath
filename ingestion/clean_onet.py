import pandas as pd, json, os
 
os.makedirs('data/processed', exist_ok=True)
 
TECH_SOCS = {
    '15-1252': 'Software Developers',
    '15-2051': 'Data Scientists and Mathematical Science Occupations',
    '15-1211': 'Computer Systems Analysts',
    '15-1212': 'Information Security Analysts',
    '15-1243': 'Database Administrators and Architects',
    '15-1257': 'Web Developers and Digital Interface Designers',
    '15-1299': 'Computer Occupations (All Other - includes ML/AI Engineers)',
    '15-1231': 'Computer Network Support Specialists',
}
 
print('Reading O*NET files...')
occupations = pd.read_excel('data/raw/onet_occupations.xlsx')
skills      = pd.read_excel('data/raw/onet_skills.xlsx')
tech        = pd.read_excel('data/raw/onet_tech_skills.xlsx')
 
# Find column names dynamically
occ_soc  = next(c for c in occupations.columns if 'SOC' in c or 'Code' in c)
occ_desc = next(c for c in occupations.columns if 'Description' in c or 'Title' in c)
sk_soc   = next(c for c in skills.columns if 'SOC' in c or 'Code' in c)
sk_name  = next(c for c in skills.columns if 'Element Name' in c or 'Skill' in c)
te_soc   = next(c for c in tech.columns if 'SOC' in c or 'Code' in c)
te_name  = next(c for c in tech.columns if 'Example' in c or 'Technology' in c or 'Tool' in c)
 
chunks = []
for soc_prefix, role_name in TECH_SOCS.items():
    role_skills = skills[skills[sk_soc].astype(str).str.startswith(soc_prefix)][sk_name].dropna().unique()[:15]
    role_tech   = tech[tech[te_soc].astype(str).str.startswith(soc_prefix)][te_name].dropna().unique()[:20]
    occ_rows    = occupations[occupations[occ_soc].astype(str).str.startswith(soc_prefix)]
    description = occ_rows[occ_desc].iloc[0] if len(occ_rows) > 0 and occ_desc in occ_rows.columns else ''
 
    if len(role_skills) == 0 and len(role_tech) == 0: continue
 
    content = f'''Source: O*NET 29.0 Database
Organization: U.S. Department of Labor / Employment and Training Administration
License: CC BY 4.0 - free for any use with attribution
Website: onetonline.org
Note: O*NET is the world standard for occupation-skills mapping, used as reference by 100+ countries
 
Occupation: {role_name}
SOC Code: {soc_prefix}
{f'Description: {description[:300]}' if description else ''}
 
CORE SKILLS REQUIRED (O*NET validated):
{chr(10).join(f'- {s}' for s in role_skills)}
 
TECHNOLOGY TOOLS AND SOFTWARE USED:
{chr(10).join(f'- {t}' for t in role_tech)}
 
Career pathway: These skills form the foundation for entering and advancing in this role.
Skills are globally transferable even though data is from US labor market research.'''
 
    chunks.append({'id': f'onet_{soc_prefix.replace("-","_")}',
                   'source': 'onet_2024', 'dev_type': role_name, 'content': content})
    print(f'  {role_name}: {len(role_skills)} skills, {len(role_tech)} tools')
 
with open('data/processed/onet_chunks.json', 'w') as f:
    json.dump(chunks, f, indent=2)
print(f'Done: {len(chunks)} O*NET chunks')

