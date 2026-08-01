import pandas as pd, json, os
from collections import Counter
 
os.makedirs('data/processed', exist_ok=True)
 
print('Reading SO Survey CSV...')
df = pd.read_csv('data/raw/survey_results_public.csv')
print(f'Shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
 
def top_items(series, n=10):
    counts = Counter()
    for val in series.dropna():
        for item in str(val).split(';'):
            if item.strip(): counts[item.strip()] += 1
    total = max(len(series.dropna()), 1)
    return [(k, round(v/total*100,1)) for k,v in counts.most_common(n)]
 
# Auto-detect column names
role_col    = 'dev_type'  if 'dev_type'  in df.columns else 'DevType'
country_col = 'country'   if 'country'   in df.columns else 'Country'
lang_col    = 'r_used'    if 'r_used'    in df.columns else 'LanguageHaveWorkedWith'
exp_col     = 'years_code_pro' if 'years_code_pro' in df.columns else 'YearsCodePro'
 
df[role_col] = df[role_col].astype(str).str.split(';')
df = df.explode(role_col).dropna(subset=[role_col])
df[role_col] = df[role_col].str.strip()
df = df[df[role_col].str.lower() != 'nan']
 
chunks = []
for role, group in df.groupby(role_col):
    if len(group) < 50: continue
    n = len(group)
    countries = group[country_col].value_counts().head(8).to_dict() if country_col in df.columns else {}
    exp_med = pd.to_numeric(group[exp_col], errors='coerce').median() if exp_col in df.columns else None
 
    content = f'''Source: Stack Overflow Developer Survey 2024
Organization: Stack Overflow (survey.stackoverflow.co/2024/)
License: Open Database License (ODbL)
Role: {role}
Global respondents: {n:,} developers
Median professional experience: {f'{exp_med:.0f} years' if exp_med and not pd.isna(exp_med) else 'not reported'}
 
REGIONAL DISTRIBUTION (top countries):
{chr(10).join(f'- {c}: {v} developers' for c,v in list(countries.items())[:6])}
 
This data reflects real developer responses from 185 countries.
Combine with O*NET data for detailed skill requirements for this role.'''
 
    chunks.append({'id': f'so_{role.lower().replace(" ","_").replace("/","_")[:50]}',
                   'source': 'stackoverflow_2024', 'dev_type': role, 'content': content})
 
with open('data/processed/so_chunks.json', 'w') as f:
    json.dump(chunks, f, indent=2)
print(f'Done: {len(chunks)} SO role chunks')
