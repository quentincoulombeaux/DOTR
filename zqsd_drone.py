from djitellopy import Tello
from pynput import keyboard

tello = Tello()
tello.connect()

# Fonction pour contrôler le drone
def on_press(key):
    try:
        if key.char == 'z':  # Avancer
            tello.move_forward(30)
        elif key.char == 'q':  # Gauche
            tello.move_left(30)
        elif key.char == 's':  # Reculer
            tello.move_back(30)
        elif key.char == 'd':  # Droite
            tello.move_right(30)
        elif key.char == 'a':  # S'élever
            tello.move_up(30)
        elif key.char == 'e':  # Descendre
            tello.move_down(30)
        elif key.char == 'o':  # Décollage ou atterrissage
            if not tello.is_flying:
                tello.takeoff()
            else:
                tello.land()
        elif key.char == 't':  # Afficher la batterie
            battery = tello.get_battery()
            print(f"Batterie: {battery}%")
    except AttributeError:
        pass  # Ignore les autres touches

# Lancement de l'écouteur de clavier
def start_drone_control():
    print("Contrôles du drone activés : ZQSD pour déplacement, A pour s'élever, E pour descendre, O pour décollage/atterrissage.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    start_drone_control()
