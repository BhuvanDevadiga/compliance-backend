from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.mitigation_memory import MitigationMemory

def update_reinforcement(
    db: Session,
    tenant_id: str,
    mitigation_type: str,
    previous_probability: float,
    current_probability: float,
):
    delta = previous_probability - current_probability
    DECAY_FACTOR = 0.9  

    memory = (
        db.query(MitigationMemory)
        .filter(
            MitigationMemory.mitigation_type == mitigation_type,
            MitigationMemory.tenant_id == tenant_id,
        )
        .first()
    )

    # Backward compatibility for legacy SQLite schemas where mitigation_type
    # is globally unique (single-column primary key).
    if not memory:
        memory = (
            db.query(MitigationMemory)
            .filter(MitigationMemory.mitigation_type == mitigation_type)
            .first()
        )
    reinforcement_score = memory.reinforcement_score if memory else 1.0
    if not memory:
        memory = MitigationMemory(mitigation_type=mitigation_type,
                                  tenant_id=tenant_id,
                                  times_used=0, success_count=0, avg_probability_delta=0.0, reinforcement_score=1.0,
                                  )
        db.add(memory)
        db.flush()

    memory.success_count *= DECAY_FACTOR
    memory.avg_probability_delta *=DECAY_FACTOR
    memory.reinforcement_score *=DECAY_FACTOR    

    if memory.times_used is None:
        memory.times_used = 0
    if memory.success_count is None:
        memory.success_count = 0
    if memory.avg_probability_delta is None:
        memory.avg_probability_delta = 0.0
    if memory.reinforcement_score is None:
        memory.reinforcement_score = 1.0

    memory.times_used += 1

    if delta > 0:
        memory.success_count += 1

    # Running average update
    memory.avg_probability_delta = (
        (memory.avg_probability_delta * (memory.times_used - 1)) + delta
    ) / memory.times_used

    # Reinforcement score formula
    memory.reinforcement_score = max(0.01,
        round((memory.success_count / memory.times_used) * memory.avg_probability_delta,
        4,)
    )

    try:
        with db.begin_nested():
            db.flush()
    except IntegrityError:
        # Another transaction inserted the row; reload and update without breaking the outer txn.
        memory = (
            db.query(MitigationMemory)
            .filter(MitigationMemory.mitigation_type == mitigation_type)
            .first()
        )
        if not memory:
            raise
        if memory.times_used is None:
            memory.times_used = 0
        if memory.success_count is None:
            memory.success_count = 0
        if memory.avg_probability_delta is None:
            memory.avg_probability_delta = 0.0
        memory.times_used += 1
        if delta > 0:
            memory.success_count += 1
        memory.avg_probability_delta = (
            (memory.avg_probability_delta * (memory.times_used - 1)) + delta
        ) / memory.times_used
        memory.reinforcement_score = max(
            0.01,
            round((memory.success_count / memory.times_used) * memory.avg_probability_delta, 4),
        )
        db.flush()
        
