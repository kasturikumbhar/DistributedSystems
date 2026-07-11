import time
from redis_client import r
from models import Job
from db import SessionLocal
from datetime import datetime

first=True

while True:
    job_id=r.rpop("job_queue")

    if not job_id:
        time.sleep(2)
        continue
    db=SessionLocal()
    try:
        job_id=job_id.decode()
        job=db.query(Job).filter(Job.job_id==job_id).first()
        print(job.payload)
        if job.status=="SUCCESS":
            continue
        job.status="PROCESSING"
        job.updated_at=datetime.utcnow()
        db.commit()
        print("Updated to PROCESSING")
        time.sleep(5)
        # if first:
        #     first= False
        #     print("Failing")
        #     raise Exception("Failing Purposely")
        # if job.status=="PROCESSING":    
        #     job.status="SUCCESS"
        #     job.updated_at=datetime.utcnow()
        #     db.commit()
        # print("Updated to SUCCESS")
        # print(f"job completed for job id: {job.job_id} at {job.updated_at}")
    except Exception as e:
        job.status="FAILED"
        job.retry_count+=1
        job.error_message=str(e)
        if job.retry_count > job.max_retries:
            job.status ="DEAD"
        else:
            r.lpush("job_queue",str(job.job_id))
        
        db.commit()


    finally:
        db.close()


