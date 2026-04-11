def resolve_dynamic_interval(probability: float):
    

    if probability >= 0.8:
        return 30   

    elif probability >= 0.6:
        return 60   

    elif probability >= 0.4:
        return 120 

    else:
        return 300  
