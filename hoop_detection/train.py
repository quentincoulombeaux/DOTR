from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch

# Use the model
results = model.train( 
    data="C:\ESEO\E5e\projet_industriel\pi\Repositery_GitHub\hoop_detection\config.yaml", 
    epochs=50
    ) # train the model
