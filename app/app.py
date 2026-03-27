import cv2
import face_recognition
import json
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import numpy as np

# -------------------------
# Configuración
# -------------------------
USUARIOS_FILE = "usuarios.json"
CARPETA_ROSTROS = "rostros"
TOLERANCIA_STRICT = 0.4 # Más bajo es más estricto
EAR_THRESHOLD = 0.23    # Umbral de parpadeo (Eye Aspect Ratio)

if not os.path.exists(CARPETA_ROSTROS):
    os.mkdir(CARPETA_ROSTROS)

if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "w") as f:
        json.dump({}, f)

# -------------------------
# Utilidades JSON y Datos
# -------------------------
def cargar_usuarios():
    try:
        with open(USUARIOS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

def guardar_usuario(datos):
    usuarios = cargar_usuarios()
    usuarios[datos["usuario"]] = datos
    guardar_usuarios(usuarios)

# -------------------------
# Imagen segura
# -------------------------
def preparar_imagen(img):
    if img is None: return None
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return np.ascontiguousarray(img, dtype=np.uint8)

# -------------------------
# Liveness (Anti-Spoofing)
# -------------------------
def calcular_ear(ojo):
    # Ecuación EAR: (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
    A = np.linalg.norm(ojo[1] - ojo[5])
    B = np.linalg.norm(ojo[2] - ojo[4])
    C = np.linalg.norm(ojo[0] - ojo[3])
    ear = (A + B) / (2.0 * C)
    return ear

def detectar_parpadeo(landmarks):
    # Indices para modelo 68 puntos (face_recognition usa dlib 68 por defecto)
    left_eye = np.array(landmarks['left_eye'])
    right_eye = np.array(landmarks['right_eye'])
    
    ear_left = calcular_ear(left_eye)
    ear_right = calcular_ear(right_eye)
    
    avg_ear = (ear_left + ear_right) / 2.0
    return avg_ear < EAR_THRESHOLD

# -------------------------
# Sincronización
# -------------------------
def sincronizar_usuarios():
    print("Iniciando sincronización...")
    usuarios = cargar_usuarios()
    
    if not os.path.exists(CARPETA_ROSTROS):
        print("Error: Carpeta rostros no existe")
        return

    archivos = os.listdir(CARPETA_ROSTROS)
    cambios = False

    for archivo in archivos:
        if not archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        usuario_id = os.path.splitext(archivo)[0]
        ruta = os.path.join(CARPETA_ROSTROS, archivo)

        if usuario_id not in usuarios:
            print(f"Procesando archivo: {archivo}")
            try:
                img = cv2.imread(ruta)
                if img is None: continue
                rgb = preparar_imagen(img)
                encodings = face_recognition.face_encodings(rgb)
                
                if len(encodings) > 0:
                    encoding_list = encodings[0].tolist()
                    usuarios[usuario_id] = {
                        "nombre": usuario_id,
                        "usuario": usuario_id,
                        "correo": "Sin correo",
                        "rostro": ruta,
                        "encoding": encoding_list
                    }
                    cambios = True
                    print(f"Usuario {usuario_id} recuperado.")
            except Exception as e:
                print(f"Error procesando {archivo}: {e}")

    for id_user, datos in usuarios.items():
        if "encoding" not in datos:
            ruta = datos["rostro"]
            if os.path.exists(ruta):
                try:
                    img = cv2.imread(ruta)
                    rgb = preparar_imagen(img)
                    encodings = face_recognition.face_encodings(rgb)
                    if len(encodings) > 0:
                        usuarios[id_user]["encoding"] = encodings[0].tolist()
                        cambios = True
                except:
                    pass

    if cambios:
        guardar_usuarios(usuarios)

# -------------------------
# UI Helper
# -------------------------
def dibujar_marco(frame, texto=""):
    h, w, _ = frame.shape
    size = 240
    x1 = w // 2 - size // 2
    y1 = h // 2 - size // 2
    x2 = x1 + size
    y2 = y1 + size

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
    if texto:
        cv2.putText(frame, texto, (x1 - 20, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    return frame, (x1, y1, x2, y2)

def mejorar_luz(img):
    return cv2.convertScaleAbs(img, alpha=1.3, beta=40)

# -------------------------
# Ventana Bienvenida
# -------------------------
def mostrar_bienvenida_ui(user_data):
    ventana.withdraw() # Ocultar ventana principal
    
    top = tk.Toplevel()
    top.title("Acceso Permitido")
    top.geometry("400x350")
    top.configure(bg="#E8F5E9")
    
    tk.Label(top, text="¡BIENVENIDO!", 
             font=("Arial", 20, "bold"), 
             bg="#E8F5E9", fg="#2E7D32").pack(pady=20)
    
    frame_datos = tk.Frame(top, bg="white", padx=20, pady=20, relief=tk.RAISED)
    frame_datos.pack(pady=10)
    
    hora = datetime.now().strftime("%H:%M:%S")
    
    tk.Label(frame_datos, text=f"Nombre: {user_data['nombre']}", 
             font=("Arial", 12), bg="white").pack(anchor="w", pady=2)
    tk.Label(frame_datos, text=f"Usuario: {user_data['usuario']}", 
             font=("Arial", 12), bg="white").pack(anchor="w", pady=2)
    tk.Label(frame_datos, text=f"Correo: {user_data['correo']}", 
             font=("Arial", 12), bg="white").pack(anchor="w", pady=2)
    tk.Label(frame_datos, text=f"Hora: {hora}", 
             font=("Arial", 12, "bold"), bg="white", fg="#1976D2").pack(anchor="w", pady=10)
             
    def cerrar():
        top.destroy()
        ventana.deiconify() # Mostrar ventana principal de nuevo
        
    tk.Button(top, text="Cerrar Sessión", 
              bg="#d32f2f", fg="white", font=("Arial", 10, "bold"),
              command=cerrar).pack(pady=20)

# -------------------------
# UI Principal y lógica de botones
# -------------------------
def mostrar_principal():
    for widget in ventana.winfo_children():
        widget.destroy()

    tk.Label(ventana,
             text="Sistema Biométrico Seguro",
             font=("Arial", 16, "bold"), fg="#333").pack(pady=30)

    btn_reg = tk.Button(ventana, text="Registrar Nuevo Usuario",
              font=("Arial", 11),
              width=25, height=2,
              bg="#2196F3", fg="white",
              activebackground="#1976D2",
              command=mostrar_registro)
    btn_reg.pack(pady=10)

    btn_log = tk.Button(ventana, text="Ingreso Seguro (Cámara)",
              font=("Arial", 11),
              width=25, height=2,
              bg="#4CAF50", fg="white",
              activebackground="#388E3C",
              command=login_facial_seguro)
    btn_log.pack(pady=10)
              
    tk.Label(ventana, text="Tecnología de Liveness Detection", 
             font=("Arial", 8), fg="gray").pack(side=tk.BOTTOM, pady=10)

def mostrar_registro():
    for widget in ventana.winfo_children():
        widget.destroy()

    tk.Label(ventana, text="Registro de Usuario", font=("Arial", 14, "bold")).pack(pady=10)

    frame_form = tk.Frame(ventana)
    frame_form.pack(pady=5)

    tk.Label(frame_form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5)
    entry_nombre = tk.Entry(frame_form)
    entry_nombre.grid(row=0, column=1, padx=5)

    tk.Label(frame_form, text="Usuario:").grid(row=1, column=0, sticky="e", padx=5)
    entry_usuario = tk.Entry(frame_form)
    entry_usuario.grid(row=1, column=1, padx=5)

    tk.Label(frame_form, text="Correo:").grid(row=2, column=0, sticky="e", padx=5)
    entry_correo = tk.Entry(frame_form)
    entry_correo.grid(row=2, column=1, padx=5)

    def procesar():
        nombre = entry_nombre.get().strip()
        usuario = entry_usuario.get().strip()
        correo = entry_correo.get().strip()
        
        if not nombre or not usuario:
            messagebox.showerror("Error", "Campos obligatorios vacíos")
            return
            
        cam = cv2.VideoCapture(0)
        ruta = f"{CARPETA_ROSTROS}/{usuario}.jpg"
        
        while True:
            ret, frame = cam.read()
            if not ret: break
            frame, _ = dibujar_marco(frame, "Presiona S para guardar")
            cv2.imshow("Registro", frame)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.imwrite(ruta, frame)
                break
        
        cam.release()
        cv2.destroyAllWindows()
        
        if os.path.exists(ruta):
            img = cv2.imread(ruta)
            rgb = preparar_imagen(img)
            encs = face_recognition.face_encodings(rgb)
            if encs:
                datos = {
                    "nombre": nombre, "usuario": usuario, 
                    "correo": correo, "rostro": ruta,
                    "encoding": encs[0].tolist()
                }
                guardar_usuario(datos)
                messagebox.showinfo("Éxito", "Usuario Guardado")
                mostrar_principal()
            else:
                os.remove(ruta)
                messagebox.showerror("Error", "No se detectó rostro")
    
    tk.Button(ventana, text="Capturar", command=procesar, bg="#2196F3", fg="white").pack(pady=20)
    tk.Button(ventana, text="Volver", command=mostrar_principal).pack()

# -------------------------
# Login Seguro con Liveness
# -------------------------
def login_facial_seguro():
    usuarios = cargar_usuarios()
    if not usuarios:
        messagebox.showerror("Error", "Base de datos vacía")
        return

    encodings_conocidos = []
    lista_usuarios = []
    for user in usuarios.values():
        if "encoding" in user:
            encodings_conocidos.append(np.array(user["encoding"]))
            lista_usuarios.append(user)
            
    cam = cv2.VideoCapture(0)
    
    usuario_detectado = None
    blink_counter = 0
    liveness_confirmed = False
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    while True:
        ret, frame = cam.read()
        if not ret: break

        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = preparar_imagen(small_frame)
        
        face_locations = face_recognition.face_locations(rgb_small)
        
        # Si hay rostros encontrados
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
            
            # Obtener landmarks para liveness (del frame original o escalado)
            # Usamos el frame pequeño para velocidad, pero landmarks necesitan coords imagen
            landmarks_list = face_recognition.face_landmarks(rgb_small, face_locations)
            
            for (top, right, bottom, left), face_encoding, landmarks in zip(face_locations, face_encodings, landmarks_list):
                # Escalar coords
                top *= 2
                right *= 2
                bottom *= 2
                left *= 2
                
                # 1. Identificación (STRICT MODE)
                matches = face_recognition.compare_faces(encodings_conocidos, face_encoding, tolerance=TOLERANCIA_STRICT)
                distance = face_recognition.face_distance(encodings_conocidos, face_encoding)
                
                name = "Desconocido"
                color = (0, 0, 255)
                
                best_match_index = np.argmin(distance)
                if matches[best_match_index]:
                    name = lista_usuarios[best_match_index]["nombre"]
                    usuario_detectado = lista_usuarios[best_match_index]
                    color = (0, 255, 255) # Amarillo (Esperando liveness)
                else:
                    usuario_detectado = None

                # 2. Liveness Check (Parpadeo)
                # Checkear parpadeo solo si es alguien conocido
                if usuario_detectado:
                    is_blinking = detectar_parpadeo(landmarks)
                    
                    if is_blinking:
                        blink_counter += 1
                        cv2.putText(frame, "PARPADEO DETECTADO", (left, top - 40), font, 0.7, (0, 255, 0), 2)
                    
                    # Si parpadea por 2-3 frames consecutivos o acumula
                    if blink_counter >= 3:
                        liveness_confirmed = True
                        color = (0, 255, 0) # Verde (Acceso)
                        cv2.putText(frame, "VERIFICADO", (left, top - 60), font, 0.7, (0, 255, 0), 2)
                
                # Dibujar
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                if not liveness_confirmed and usuario_detectado:
                   cv2.putText(frame, "POR FAVOR PARPADEA", (left, bottom + 30), font, 0.6, (0, 255, 255), 2)
                
                cv2.putText(frame, name, (left, bottom + 60), font, 0.8, color, 2)

        if liveness_confirmed and usuario_detectado:
            # Pausa breve para mostrar el éxito verde
            cv2.imshow("Acceso Seguro", frame)
            cv2.waitKey(1000)
            break # Salir del loop para mostrar bienvenida
            
        cv2.imshow("Acceso Seguro", frame)
        if cv2.waitKey(1) == 27: # ESC
            usuario_detectado = None # Cancelar login
            break
            
    cam.release()
    cv2.destroyAllWindows()
    
    if liveness_confirmed and usuario_detectado:
        mostrar_bienvenida_ui(usuario_detectado)

# -------------------------
# INICIO
# -------------------------
if __name__ == "__main__":
    sincronizar_usuarios()
    ventana = tk.Tk()
    ventana.title("Sistema de Acceso Biométrico")
    ventana.geometry("400x500")
    mostrar_principal()
    ventana.mainloop()
