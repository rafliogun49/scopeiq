"""Debug script to simulate the 2-test ordering issue."""
import os
os.environ['TEST_DATABASE_URL'] = 'postgresql+psycopg://scopeiq:changeme@localhost:5432/scopeiq_test'

from app.workers import tasks as tasks_module
from app.workers import celery_app as celery_module
from app.core import config as config_module
from sqlalchemy import create_engine as sa_create_engine
from sqlmodel import SQLModel, Session
from uuid import uuid4, UUID

test_engine = sa_create_engine(config_module.settings.TEST_DATABASE_URL, echo=False)
SQLModel.metadata.create_all(test_engine)

celery_module.celery_app.conf.task_always_eager = True
celery_module.celery_app.conf.task_eager_propagates = True
tasks_module.engine = test_engine

from app.agents import runner as runner_module
from app.tools import discover_urls as discover_module
from app.tools import http_fetch as http_fetch_module
from app.rag import index as index_module

runner_module.use_stub_runner()

FAKE_HTML = '<html><body><p>Test content here for scraping purposes</p><a href="/pricing">Pricing</a></body></html>'

async def fake_fetch(url, render_js=False):
    return {'status': 200, 'html': FAKE_HTML, 'text': ''}

http_fetch_module.http_fetch = fake_fetch
runner_module.http_fetch = fake_fetch
discover_module.http_fetch = fake_fetch

async def fake_index(run_id, docs):
    return len(docs)

index_module.index_chunks = fake_index
tasks_module.index_chunks = fake_index

# Create a project
from app.models.project import Project
with Session(test_engine) as s:
    proj = Project(name="test", idea="test idea", user_id=uuid4())
    s.add(proj)
    s.commit()
    proj_id = proj.id

print("=== TEST 1: normal run ===")
with Session(test_engine) as s:
    from app.models.run import Run
    run = Run(project_id=proj_id, status='pending')
    s.add(run)
    s.commit()
    run_id = str(run.id)

result = tasks_module.run_research_task(run_id)
print(f"Result: {result}")

with Session(test_engine) as s:
    r = s.get(Run, UUID(run_id))
    print(f"Status: {r.status}, cost: {r.cost_usd}, tokens: {r.token_input}")

print()
print("=== TEST 2: budget exceeded ===")
config_module.settings.BUDGET_INPUT_TOKENS = 1

with Session(test_engine) as s:
    from app.models.run import Run
    run2 = Run(project_id=proj_id, status='pending')
    s.add(run2)
    s.commit()
    run2_id = str(run2.id)

result2 = tasks_module.run_research_task(run2_id)
print(f"Result: {result2}")

with Session(test_engine) as s:
    r2 = s.get(Run, UUID(run2_id))
    print(f"Status: {r2.status}, error: {r2.error}")
