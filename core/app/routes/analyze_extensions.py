# Additional endpoints for analyze routes - to be appended to analyze.py

# @router.get("/check-existing/{job_id}")
# async def check_existing_analysis(
#     job_id: str,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(database.get_db)
# ):
#     """Check if an analysis job exists and has sentiment results"""
#     job = db.query(models.AnalysisJob).filter(
#         models.AnalysisJob.id == job_id,
#         models.AnalysisJob.user_id == current_user.id
#     ).first()
#     
#     if not job:
#         return {
#             "exists": False,
#             "has_results": False
#         }
#     
#     # Count sentiment results for this job
#     result_count = db.query(models.SentimentResult).filter(
#         models.SentimentResult.job_id == job_id
#     ).count()
#     
#     return {
#         "exists": True,
#         "has_results": result_count > 0,
#         "job_type": job.type,
#         "status": job.status,
#         "created_at": job.created_at,
#         "result_count": result_count,
#         "metadata": job.job_metadata
#     }
