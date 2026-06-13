from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

# ---------------------------------------------------
# Core Data Model: The Audit Log Entry (F1)
# 모든 로그 기록의 기본 형태입니다. 위변조 불가능성을 위해 필수 필드가 포함됩니다.
class AuditLogEntry(BaseModel):
    """실제 저장될 단일 감사 기록 엔트리."""
    log_id: str = Field(..., description="UUID 기반 고유 식별자")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC 시간 (기록 시점)")
    user_identifier: str = Field(..., description="접근을 시도한 사용자 계정 또는 기기 ID")
    action_type: Literal["READ", "WRITE", "DELETE", "ACCESS"] = Field(..., description="수행된 동작 타입")
    resource_path: str = Field(..., description="영향받은 자원 (예: /data/user/profile.docx)")
    success: bool = Field(..., description="작업 성공 여부")
    details: dict[str, any] = Field({}, description="추가적인 상세 정보 (IP 주소, 세션 ID 등)")
    # 무결성 검증을 위한 핵심 필드. 이 값이 변하면 로그를 조작했다는 의미입니다.
    record_hash: str = Field(..., description="이 기록의 SHA256 해시 값")

# ---------------------------------------------------
# API Request Model: 외부에서 전송되는 원본 이벤트 (Gateway Agent -> API)
class RawAuditEventRequest(BaseModel):
    """로컬 게이트웨이 에이전트가 서버에 보고하는 원본 데이터 구조."""
    user_identifier: str = Field(..., description="사용자 ID")
    action_type: Literal["READ", "WRITE", "DELETE", "ACCESS"] = Field(...)
    resource_path: str = Field(..., description="접근된 자원 경로")
    success: bool = Field(..., description="로컬에서 감지한 작업 성공 여부")
    details: dict[str, any] = Field({}, description="추가적인 상세 정보 (예: 파일 크기, 시도 시간)")

# ---------------------------------------------------
# API Response Model
class AuditStatusResponse(BaseModel):
    """로그 기록 요청에 대한 응답 상태."""
    message: str
    log_id: str
    is_accepted: bool = True