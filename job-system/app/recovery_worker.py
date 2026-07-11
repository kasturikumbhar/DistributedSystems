from redis_client import r
from models import Job
from db import SessionLocal
from datetime import datetime , timedelta
import time

while True:
    db=SessionLocal()
    try:
        jobs=db.query(Job).filter(Job.status=="PROCESSING",
                                        Job.updated_at < datetime.utcnow()- timedelta(seconds=10)).all()
        for job in jobs:
            if job.retry_count< job.max_retries:
                job.retry_count+=1
                job.status="CREATED"
                r.lpush("job_queue",str(job.job_id))
            else:
                job.status="DEAD"
            db.commit()
    finally:
        db.close()
    time.sleep(360)



    
