def generate_filename(app_id, timestamp):
    return f'logs/{app_id}/{app_id}_{timestamp.strftime("%Y-%m-%d_%H")}.txt'
