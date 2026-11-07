import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import agent
CONFIG=json.loads((agent.ROOT/'config.json').read_text())
class Tests(unittest.TestCase):
    def job(self): return agent.normalize(dict(title='AI Engineer',company='Test',location='Singapore',url='https://example.com/jobs/1',description='Python SQL Docker, 2+ years of experience'))
    def test_experience(self):
        j=self.job();self.assertEqual(agent.evaluate(j,CONFIG)['decision'],'shortlist')
        j['description']='6 years of experience';self.assertEqual(agent.evaluate(j,CONFIG)['decision'],'reject')
        j['description']='3–5 years of experience';self.assertEqual(agent.evaluate(j,CONFIG)['decision'],'shortlist')
    def test_title_location_company(self):
        j=self.job();j['title']='Principal AI Engineer';self.assertEqual(agent.evaluate(j,CONFIG)['decision'],'reject')
        j=self.job();j['location']='New York';self.assertEqual(agent.evaluate(j,CONFIG)['decision'],'reject')
        c=json.loads(json.dumps(CONFIG));c['filters']['excluded_companies']=['Test'];self.assertEqual(agent.evaluate(self.job(),c)['decision'],'reject')
    def test_duplicates_distinct_reqs(self):
        a=self.job();b=self.job();b['url']='https://example.com/jobs/2';self.assertEqual(len(agent.deduplicate([a,a,b])),2)
        a['requisition_id']=b['requisition_id']='123';self.assertEqual(len(agent.deduplicate([a,b])),1)
    def test_evidence_gate(self):
        r={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'jobs':[self.job()]}),'annotations':[]}]}]}
        with patch('agent.request_json',return_value=r): self.assertEqual(agent.discover(CONFIG,'careers','Singapore','fake')[0],[])
        r['output'][0]['content'][0]['annotations']=[{'type':'url_citation','url':'https://example.com/jobs/1'}]
        with patch('agent.request_json',return_value=r): self.assertEqual(len(agent.discover(CONFIG,'careers','Singapore','fake')[0]),1)
        with patch('agent.request_json',return_value=r): self.assertEqual(agent.discover(CONFIG,'linkedin','Singapore','fake')[0],[])
    def test_status_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);agent.save([agent.evaluate(self.job(),CONFIG)],out,{'started_at':agent.now()})
            db=agent.sqlite3.connect(out/'tracker.sqlite3');db.execute("UPDATE jobs SET status='applied'");db.commit();db.close()
            agent.save([agent.evaluate(self.job(),CONFIG)],out,{'started_at':agent.now()})
            j=json.loads((out/'audit.json').read_text())['jobs'][0];self.assertFalse(j['new']);self.assertEqual(j['application_status'],'applied')
    def test_csv_url_safety(self):
        self.assertTrue(agent.safe_cell('=SUM(1,2)').startswith("'"))
        for u in ['javascript:alert(1)','https://127.0.0.1/a','https://localhost/a']:
            with self.assertRaises(ValueError):agent.canon(u)
        self.assertEqual(agent.canon('https://example.com/job?utm_source=foo'),'https://example.com/job')
    def test_ats(self):
        data={'jobs':[{'id':7,'title':'AI Engineer','absolute_url':'https://example.com/jobs/7','location':{'name':'Singapore'},'content':'<p>Python</p>'}]}
        with patch('agent.request_json',return_value=data):
            j=agent.ats_jobs({'provider':'greenhouse','slug':'test','company':'Test'})[0];self.assertEqual(j['verification'],'live_ats_feed');self.assertEqual(j['description'],'Python')
if __name__=='__main__': unittest.main()
