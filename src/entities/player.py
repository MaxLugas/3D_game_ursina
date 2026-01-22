def create_player(**kwargs):
    from ursina.prefabs.first_person_controller import FirstPersonController
    return FirstPersonController(**kwargs)