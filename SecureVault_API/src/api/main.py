from fastapi import FastAPI, HTTPException
from src.models.schema import RawAuditEventRequest, AuditStatusResponse
from src.services.audit_service import AuditService
from datetime import datetime
import uvicorn

# ---------------------------------------------------
# Initialize Services (Singleton pattern)
try:
    AUDIT_SERVICE = AuditService()
except Exception as e:
    print(f"Fatal Error during service initialization: {e}")
    AUDIT_SERVICE = None


app = FastAPI(title="AJSoft Secure Vault API", description="B2B 규제 준수 감사 로깅 시스템")

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 로그 및 서비스 초기화 검증."""
    if AUDIT_SERVICE:
        print("\n[STATUS] 🚀 Secure Vault API Online. Audit Service Ready.")
    else:
        raise HTTPException(status_code=503, detail="Service Initialization Failed")

@app.post("/api/v1/log", response_model=AuditStatusResponse)
async def record_audit_log(raw_event: RawAuditEventRequest):
    """
    [P1 핵심 엔드포인트] 
    로컬 게이트웨이 에이전트가 전송한 원본 이벤트를 받아, 감사 로그 엔진을 통해 처리하고 저장합니다.
    """
    if not AUDIT_SERVICE:
        raise HTTPException(status_code=503, detail="Audit Service Unavailable")

    try:
        # 1. 서비스 계층 호출 (가장 중요한 비즈니스 로직 실행)
        processed_log = AUDIT_SERVICE.process_raw_event(raw_event)
        
        # 2. 성공 응답 반환
        return AuditStatusResponse(
            message="Audit log successfully accepted and hashed.",
            log_id=processed_log.log_id
        )
    except Exception as e:
        print(f"🚨 Critical Error during logging: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during audit processing.")

@app.get("/api/v1/report", response_model=dict)
async def get_compliance_report(start_date: str = "2026-01-01", end_date: str = "2026-12-31"):
    """
    [P3 핵심 엔드포인트] 
    기간별 규제 준수 보고서의 골격 데이터를 조회합니다. (F2 Skeleton)
    """
    if not AUDIT_SERVICE:
        raise HTTPException(status_code=503, detail="Audit Service Unavailable")

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        # 서비스 레이어를 통해 보고서 데이터 요청
        report = AUDIT_SERVICE.get_compliance_report_skeleton(start, end)
        return report
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")


if __name__ == "__main__":
    # 로컬 테스트 실행 명령어
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)