import requests
import os

# Configuración básica
BASE_URL = "http://192.168.68.22/OTCS/cs.exe/api/v1" 
USER = "otadmin@otds.admin"
PASS = "inicio1234."

# Directorio de salida (relativo al script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Crear carpeta si no existe

def get_ot_token():
    """Obtiene el ticket de autenticación necesario para cualquier operación."""
    auth_url = f"{BASE_URL}/auth"
    payload = {'username': USER, 'password': PASS}
    
    try:
        response = requests.post(auth_url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()['ticket']
    except Exception as e:
        print(f"❌ Error de autenticación: {e}")
        return None

def get_filename_from_response(response, default_name):
    """Extrae el nombre del archivo desde el header Content-Disposition."""
    content_disposition = response.headers.get('Content-Disposition', '')
    
    if 'filename=' in content_disposition:
        # Buscar filename="archivo.pdf" o filename=archivo.pdf
        import re
        match = re.search(r'filename[*]?=["\']?([^"\';\n]+)["\']?', content_disposition)
        if match:
            return match.group(1).strip()
    
    return default_name


def download_document(data_id, output_dir=OUTPUT_DIR):
    """Descarga el contenido físico del documento usando su DataID con su nombre original."""
    token = get_ot_token()
    if not token: return None

    # Endpoint para contenido de nodos
    download_url = f"{BASE_URL}/nodes/{data_id}/content"
    headers = {'OTCSTICKET': token}

    try:
        print(f"Descargando documento {data_id}...")
        with requests.get(download_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            
            # Obtener nombre original del archivo
            filename = get_filename_from_response(r, f"{data_id}.dat")
            output_path = os.path.join(output_dir, filename)
            
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ Archivo guardado en: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error al descargar: {e}")
        return None

# --- PRUEBA LOCAL ---
if __name__ == "__main__":
    test_id = 104282 
    download_document(test_id)  # Se guardará con su nombre original