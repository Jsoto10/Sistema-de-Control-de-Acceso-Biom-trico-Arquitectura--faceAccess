import numpy as np
import cv2
import face_recognition
from typing import List, Optional

class FaceService:
    @staticmethod
    def compare_faces(known_encodings: List[List[float]], face_encoding: List[float], tolerance: float = 0.4) -> bool:
        """
        Compara un encoding enviado por el sensor con una lista de encodings conocidos de la DB.
        """
        if not known_encodings:
            return False
            
        # Convertir a numpy para usar funciones de distancia de forma vectorizada
        known_matrix = np.array(known_encodings)
        face_norm = np.array(face_encoding)
        
        # Calcular distancias euclidianas
        distances = np.linalg.norm(known_matrix - face_norm, axis=1)
        
        # Retornar True si alguna distancia es menor a la tolerancia
        return any(distances <= tolerance)

    @staticmethod
    def extract_and_analyze(image_bytes: bytes):
        """
        Calcula encodings y extrae rasgos faciales (landmarks) desde bytes de imagen.
        """
        # Convertir bytes a imagen de opencv/numpy
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None, None
            
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 1. Encodings (Vectores de 128 d)
        face_locations = face_recognition.face_locations(rgb_img)
        if not face_locations:
            return None, None
            
        encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        # 2. Análisis de rasgos (puntos faciales)
        landmarks = face_recognition.face_landmarks(rgb_img, face_locations)
        
        # Formatear rasgos para guardarlos de forma segura en JSON
        rasgos = {
            "num_caras": len(face_locations),
            "puntos_faciales": landmarks[0] if landmarks else {},
            "face_size": {
                "top": face_locations[0][0],
                "right": face_locations[0][1],
                "bottom": face_locations[0][2],
                "left": face_locations[0][3]
            }
        }
        
        return [e.tolist() for e in encodings], rasgos

    @staticmethod
    def get_best_match(users: List[dict], face_encoding: List[float], tolerance: float = 0.4):
        """
        Busca el mejor match entre una lista de usuarios.
        Soporta formato nuevo (dict de ángulos) y antiguo (lista simple).
        """
        best_user = None
        min_distance = float("inf")
        face_norm = np.array(face_encoding)
        
        for user in users:
            enc_data = user.get("encodings", []) # Nombre correcto en el modelo
            
            # Normalizar: Si es dict, extraer todos los vectores de todos los ángulos
            all_vectors = []
            if isinstance(enc_data, dict):
                for angle_vecs in enc_data.values():
                    if isinstance(angle_vecs, list):
                        all_vectors.extend(angle_vecs)
            elif isinstance(enc_data, list):
                all_vectors = enc_data
            
            if not all_vectors:
                continue
                
            user_matrix = np.array(all_vectors)
            distances = np.linalg.norm(user_matrix - face_norm, axis=1)
            local_min = np.min(distances)
            
            if local_min < min_distance and local_min <= tolerance:
                min_distance = local_min
                best_user = user
                
        return best_user, min_distance
