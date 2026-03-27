import cv2
import face_recognition
import requests
import numpy as np
import threading
import time
import base64
import os
from datetime import datetime

# CONFIGURACIÓN
API_URL = "http://127.0.0.1:8000/api/face-recognition"
ALERT_URL = "http://127.0.0.1:8000/api/alerts"
EAR_THRESHOLD = 0.23
BLINK_LIMIT = 2

class SensorBiometrico:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.blink_counter = 0
        self.liveness_confirmed = False
        self.last_request_time = 0.0
        self.request_cooldown = 5
        self.frame_buffer = [] # Buffer circular para pre-grabación
        self.buffer_size = 30 # ~1 segundo a 30fps

    def calcular_ear(self, ojo):
        A = np.linalg.norm(ojo[1] - ojo[5])
        B = np.linalg.norm(ojo[2] - ojo[4])
        C = np.linalg.norm(ojo[0] - ojo[3])
        return (A + B) / (2.0 * C)

    def detectar_parpadeo(self, landmarks):
        left_eye = np.array(landmarks['left_eye'])
        right_eye = np.array(landmarks['right_eye'])
        avg_ear = (self.calcular_ear(left_eye) + self.calcular_ear(right_eye)) / 2.0
        return avg_ear < EAR_THRESHOLD

    def enviar_a_api(self, encoding, current_frame, confidence, video_buffer=None):
        """
        Envía el encoding al backend con metadata y evidencia multimedia.
        """
        try:
            payload = {
                "encoding": encoding.tolist(),
                "confidence": float(confidence),
                "sensor_id": "camara_entrada_1"
            }
            response = requests.post(API_URL, json=payload, timeout=5)
            data = response.json()
            
            if data.get("status") == "success":
                print(f"[ACCESO] Permitido: {data.get('user')} (Confianza: {confidence:.2f})")
            elif data.get("status") == "denied":
                # Calcular nivel de riesgo basado en distancia (1 - confianza)
                distancia = 1.0 - confidence
                nivel = "Bajo"
                if distancia > 0.6: nivel = "Alto"
                elif distancia > 0.45: nivel = "Medio"
                
                print(f"[ALERTA] Intruso detectado (Riesgo: {nivel}). Procesando evidencia...")
                self.enviar_alerta(current_frame, confidence, video_buffer, nivel)
        except Exception as e:
            print(f"[ERROR] No se pudo conectar con el servidor: {e}")

    def enviar_alerta(self, frame, confidence, video_buffer, nivel):
        """
        Envía alerta detallada con imagen, video y nivel de riesgo.
        """
        try:
            # 1. Imagen base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # 2. Video base64 (Procesar buffer si existe)
            video_b64 = None
            if video_buffer and len(video_buffer) > 0:
                temp_filename = f"temp_alert_{int(time.time())}.mp4"
                h, w, _ = video_buffer[0].shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_filename, fourcc, 15.0, (w, h))
                for f in video_buffer:
                    out.write(f)
                out.release()
                
                with open(temp_filename, "rb") as v_file:
                    video_b64 = base64.b64encode(v_file.read()).decode('utf-8')
                os.remove(temp_filename)

            payload = {
                "imagen": img_b64,
                "video": video_b64,
                "descripcion": f"Intruso detectado con nivel de riesgo {nivel}",
                "tipo": "intruso_desconocido",
                "nivel_riesgo": nivel,
                "metadata": {
                    "confidence": float(confidence),
                    "sensor": "camara_entrada_1",
                    "timestamp_local": datetime.now().isoformat()
                }
            }
            requests.post(ALERT_URL, json=payload, timeout=5)
            print(f"[ALERTA] Evidencia multimedia (Riesgo {nivel}) enviada al dashboard.")
        except Exception as e:
            print(f"[ERROR] Fallo al enviar alerta multimedia: {e}")

    def run(self):
        print("🚀 Sensor Biométrico PRO Iniciado")
        print("Presiona ESC para salir.")
        while True:
            ret, frame = self.cam.read()
            if not ret: break

            # Actualizar buffer
            self.frame_buffer.append(frame.copy())
            if len(self.frame_buffer) > self.buffer_size:
                self.frame_buffer.pop(0)

            # Procesamiento optimizado
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_small)
            
            if face_locations:
                face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
                landmarks_list = face_recognition.face_landmarks(rgb_small, face_locations)
                
                for (top, right, bottom, left), face_encoding, landmarks in zip(face_locations, face_encodings, landmarks_list):
                    # Volver a escala original (x4 porque usamos 0.25)
                    top, right, bottom, left = top*4, right*4, bottom*4, left*4
                    
                    # Detección de vida (Liveness Simple)
                    is_blinking = self.detectar_parpadeo(landmarks)
                    if is_blinking:
                        self.blink_counter += 1
                    
                    color = (0, 255, 255) # Amarillo - Verificando
                    status_text = "VERIFICANDO... PARPADEA"

                    if self.blink_counter >= BLINK_LIMIT:
                        self.liveness_confirmed = True
                        color = (0, 255, 0)
                        status_text = "LIVENESS OK - PROCESANDO"

                        current_time = time.time()
                        if current_time - self.last_request_time > self.request_cooldown:
                            # Capturar buffer actual para la alerta si es denegado
                            evidence_buffer = list(self.frame_buffer)
                            
                            threading.Thread(
                                target=self.enviar_a_api, 
                                args=(face_encoding, frame.copy(), 0.85, evidence_buffer)
                            ).start()
                            self.last_request_time = current_time
                            self.blink_counter = 0
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.putText(frame, status_text, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            cv2.imshow("Monitor de Acceso Biometrico", frame)
            if cv2.waitKey(1) == 27: break # ESC

        self.cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    sensor = SensorBiometrico()
    sensor.run()
