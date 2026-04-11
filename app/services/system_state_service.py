from app.models.system_state import GlobalSystemState

def get_global_state(db):
    state = db.query(GlobalSystemState).first()

    if not state:
        state = GlobalSystemState(id="GLOBAL")
        db.add(state)
        db.commit()
        db.refresh(state)

    return state