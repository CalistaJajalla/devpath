from dotenv import load_dotenv
load_dotenv()
 
import json, os
from groq import Groq
from index import load_chunks, build_indexes, text_search, vector_search, hybrid_search, embedder
 
groq_client = Groq()
 
def generate_questions(chunk, n=3):
    prompt = f'''Generate {n} specific questions that ONLY this document answers.
Include the exact role name in each question.
Bad: "What skills do developers need?"
Good: "What programming languages do Data Scientists use according to SO Survey 2024?"

Document:
{chunk["content"][:1000]}

Return ONLY a JSON array: ["question 1", "question 2"]'''
    r = groq_client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role':'user','content':prompt}],
        response_format={'type':'json_object'},
    )
    import re
    text = r.choices[0].message.content
    # Extract array from response
    match = re.search(r'[.*]', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(text).get('questions', [])
 
def hit_rate(relevance_list):
    return sum(1 for r in relevance_list if any(x==1 for x in r)) / len(relevance_list)
 
def mrr(relevance_list):
    scores = []
    for r in relevance_list:
        for i,v in enumerate(r):
            if v==1: scores.append(1/(i+1)); break
        else: scores.append(0)
    return sum(scores)/len(scores)
 
def evaluate(ground_truth, search_fn):
    relevance = []
    for q, doc_id in ground_truth:
        results = search_fn(q)
        rel = [1 if r['id']==doc_id or r.get('dev_type','').lower() in doc_id.lower() or doc_id.lower() in r.get('dev_type','').lower() else 0 for r in results]
        relevance.append(rel)
    return {'hit_rate': round(hit_rate(relevance), 4), 'mrr': round(mrr(relevance), 4)}
 
# Load indexes
print('Building indexes...')
chunks = load_chunks()
text_idx, vec_idx, X = build_indexes(chunks)
 
# Generate ground truth for first 30 chunks
gt_path = 'data/processed/ground_truth.json'
if not os.path.exists(gt_path):
    print('Generating ground truth questions (takes ~3 min)...')
    ground_truth = []
    for chunk in chunks[:30]:
        try:
            qs = generate_questions(chunk, n=3)
            for q in qs:
                ground_truth.append([q, chunk['id']])
            print(f'  {chunk["id"]}: {len(qs)} questions')
        except Exception as e:
            print(f'  Error on {chunk["id"]}: {e}')
    with open(gt_path, 'w') as f:
        json.dump(ground_truth, f, indent=2)
    print(f'Ground truth saved: {len(ground_truth)} questions')
else:
    with open(gt_path) as f:
        ground_truth = json.load(f)
    print(f'Loaded {len(ground_truth)} ground truth questions')
 
# Evaluate all three search methods
print('Evaluating text_search...')
text_eval = evaluate(ground_truth, lambda q: text_search(q, text_idx))
print(f'  Hit Rate: {text_eval["hit_rate"]}  MRR: {text_eval["mrr"]}')
 
print('Evaluating vector_search...')
vec_eval = evaluate(ground_truth, lambda q: vector_search(q, vec_idx))
print(f'  Hit Rate: {vec_eval["hit_rate"]}  MRR: {vec_eval["mrr"]}')
 
print('Evaluating hybrid_search...')
hyb_eval = evaluate(ground_truth, lambda q: hybrid_search(q, text_idx, vec_idx))
print(f'  Hit Rate: {hyb_eval["hit_rate"]}  MRR: {hyb_eval["mrr"]}')
 
results = {'text': text_eval, 'vector': vec_eval, 'hybrid': hyb_eval}
with open('data/processed/eval_results.json', 'w') as f:
    json.dump(results, f, indent=2)
 
print('\n=== EVALUATION SUMMARY ===')
print(f'Method        Hit Rate   MRR')
print(f'text_search   {text_eval["hit_rate"]:.4f}     {text_eval["mrr"]:.4f}')
print(f'vector_search {vec_eval["hit_rate"]:.4f}     {vec_eval["mrr"]:.4f}')
print(f'hybrid (RRF)  {hyb_eval["hit_rate"]:.4f}     {hyb_eval["mrr"]:.4f}')
print('Copy these numbers into your README.')
