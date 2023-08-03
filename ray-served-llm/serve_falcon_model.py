from models_ray_served import ModelServer

SERVE_FALCON_MODEL = "tiiuae/falcon-7b"

serve_falcon_model_app = ModelServer.bind(SERVE_FALCON_MODEL)
