from ultralytics import YOLO

# Load a COCO-pretrained YOLO11n model
model = YOLO("yolo11n.yaml")

# Train the model 
results = model.train(data="C:\ESEO\E5e\projet_industriel\pi\Repositery_GitHub\hoop_detection\config.yaml", 
                      epochs=50)
