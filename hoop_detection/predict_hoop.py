import os
from ultralytics import YOLO
import cv2

# Fonction pour calculer l'aire d'une boîte englobante (bounding box)
def calculate_area(x1, y1, x2, y2):
    return abs((x2 - x1) * (y2 - y1))

# Fonction pour calculer l'intersection sur l'union (IoU)
def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = calculate_area(*boxA)
    boxBArea = calculate_area(*boxB)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

# Chemin de la vidéo d'entrée
input_video_path = r'videos\hexagon\video_test2.mp4'

# Chemin de la vidéo de sortie
output_video_path = r'videos\hexagon\video_test2_final_out.mp4'

# Ouvrir la vidéo en entrée
cap = cv2.VideoCapture(input_video_path)

# Vérifier si la vidéo a été ouverte avec succès
if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la vidéo.")
    exit()

# Obtenir les informations de la vidéo (largeur, hauteur, FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Initialiser l'écriture vidéo pour créer une nouvelle vidéo avec les détections
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Utiliser le codec 'mp4v' pour l'enregistrement
out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

# Chargement des modèles YOLO pour les cercles et les hexagones
model_hoop_path = r'runs\detect\train9\weights\last.pt'
model_hexagon_path = r'runs\detect\train5\weights\last.pt'

model_hoop = YOLO(model_hoop_path)
model_hexagon = YOLO(model_hexagon_path)

# Définition du seuil de confiance pour les détections
threshold = 0.83

# Boucle principale pour traiter chaque image de la vidéo
while True:
    ret, frame = cap.read()
    if not ret:
        print("Fin de la vidéo ou erreur de lecture.")
        break
    
    H, W, _ = frame.shape

    # Application des modèles YOLO pour les cercles et les hexagones
    results_hoop = model_hoop(frame)[0]
    results_hexagon = model_hexagon(frame)[0]

    # Stockage des hoops et hexagones pour comparaison
    hoops = []
    hexagons = []

    # Traitement des détections de cercles
    for result in results_hoop.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        if score > threshold:
            hoops.append([x1, y1, x2, y2, score])

    # Traitement des détections d'hexagones
    for result in results_hexagon.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        if score > threshold:
            hexagons.append([x1, y1, x2, y2, score])

    # Filtrer les hoops superposés avec les hexagones
    for hoop in hoops:
        hoop_area = calculate_area(hoop[0], hoop[1], hoop[2], hoop[3])
        keep_hoop = True
        for hexagon in hexagons:
            hexagon_area = calculate_area(hexagon[0], hexagon[1], hexagon[2], hexagon[3])
            iou = calculate_iou([hoop[0], hoop[1], hoop[2], hoop[3]], [hexagon[0], hexagon[1], hexagon[2], hexagon[3]])
            
            # Si l'aire est similaire à 90% et la superposition (IoU) à 90%
            if abs(hoop_area - hexagon_area) / hoop_area < 0.3 and iou >= 0.7:
                keep_hoop = False
                break
        
        if keep_hoop:
            # Dessine un rectangle bleu pour les cercles
            cv2.rectangle(frame, (int(hoop[0]), int(hoop[1])), (int(hoop[2]), int(hoop[3])), (255, 0, 0), 4)  # Bleu
            # Affichage du type et du score
            cv2.putText(frame, f"HOOP {hoop[4]:.2f}",
                        (int(hoop[0]), int(hoop[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.3,
                        (255, 0, 0),
                        3,
                        cv2.LINE_AA)

    # Afficher toujours les hexagones
    for hexagon in hexagons:
        # Dessine un rectangle rouge pour les hexagones
        cv2.rectangle(frame, (int(hexagon[0]), int(hexagon[1])), (int(hexagon[2]), int(hexagon[3])), (0, 0, 255), 4)  # Rouge
        # Affichage du type et du score
        cv2.putText(frame, f"HEXAGON {hexagon[4]:.2f}",
                    (int(hexagon[0]), int(hexagon[1] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    (0, 0, 255),
                    3,
                    cv2.LINE_AA)

    # Écrire le frame annoté dans la vidéo de sortie
    out.write(frame)

# Libérer les ressources
cap.release()
out.release()
cv2.destroyAllWindows()
