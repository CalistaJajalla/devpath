from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import agent, Deps

app = FastAPI(title='DevPath API', version='1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

class AskRequest(BaseModel):
    question: str
    skills: list[str] = []
    target_role: str = ''
    region: str = ''

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: int

feedback_log = []

@app.post('/ask')
async def ask(req: AskRequest):
    deps = Deps(skills=req.skills, target_role=req.target_role, region=req.region)
    result = await agent.run(req.question, deps=deps)
    return {'answer': result.output, 'status': 'ok'}

@app.post('/feedback')
async def feedback(req: FeedbackRequest):
    feedback_log.append({'question': req.question, 'rating': req.rating})
    return {'status': 'ok', 'total_feedback': len(feedback_log)}

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/stats')
def stats():
    pos = sum(1 for f in feedback_log if f['rating'] == 1)
    neg = sum(1 for f in feedback_log if f['rating'] == -1)
    return {'total_queries': len(feedback_log), 'positive': pos, 'negative': neg}