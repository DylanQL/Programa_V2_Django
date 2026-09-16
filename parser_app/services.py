import os
import re
import io
from datetime import datetime
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

CLIENT_RUC = "20101363008"

def extraer_texto_ocr(page):
    """Convierte la página del PDF a imagen y extrae el texto."""
    pix = page.get_pixmap(dpi=200)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img)

def funcionalidad_1_separar_y_renombrar(input_pdf_path, output_dir):
    """Separa el PDF, aplica OCR, busca datos y renombra."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(input_pdf_path)
    fecha_actual = datetime.now().strftime('%d-%m-%Y')
    errores = 0

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        texto = extraer_texto_ocr(page)

        # Buscar todos los RUCs válidos (10, 15, 17 o 20 seguido de 9 dígitos)
        rucs_encontrados = list(set(re.findall(r'\b(?:10|15|17|20)\d{9}\b', texto)))
        
        # Buscar formato de factura (Ej: FF01-169 o F001-00000169)
        facturas_encontradas = re.findall(r'\b[FE][0-9A-Z]{3}-\d{1,8}\b', texto)
        
        numero_factura_normalizado = None
        if facturas_encontradas:
            serie, correlativo = facturas_encontradas[0].split('-')
            numero_factura_normalizado = f"{serie}-{correlativo.zfill(8)}"

        tipo_documento = None
        ruc_emisor = None

        # Lógica de clasificación
        if CLIENT_RUC in rucs_encontrados:
            otros_rucs = [r for r in rucs_encontrados if r != CLIENT_RUC]
            if otros_rucs and numero_factura_normalizado:
                tipo_documento = "FACTURA"
                ruc_emisor = otros_rucs[0]
        else:
            # Es ST si no tiene el RUC del cliente, asumiendo que el RUC presente es el del emisor
            if rucs_encontrados and numero_factura_normalizado:
                tipo_documento = "ST"
                ruc_emisor = rucs_encontrados[0]

        # Guardar el documento individual
        nuevo_doc = fitz.open()
        nuevo_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        if tipo_documento and ruc_emisor and numero_factura_normalizado:
            nombre_archivo = f"{ruc_emisor}__{numero_factura_normalizado}__{fecha_actual}__{tipo_documento}.pdf"
        else:
            errores += 1
            nombre_archivo = f"ERROR_AL_LEER_{page_num + 1}.pdf" # +1 para no sobreescribir errores

        ruta_salida = os.path.join(output_dir, nombre_archivo)
        nuevo_doc.save(ruta_salida)
        nuevo_doc.close()

    doc.close()

    # Impresión en consola según resultados
    print("######################################")
    if errores == 0:
        print("*Todos los documentos fueron renombrados exitosamente")
    else:
        print(f"*No se lograron leer ({errores}) documentos")
    print("######################################")


def funcionalidad_2_hacer_match_y_unir(output_dir):
    """Busca parejas FACTURA y ST, las une y limpia las originales."""
    archivos = os.listdir(output_dir)
    
    facturas = {}
    sts = {}
    errores_lectura = 0

    # Clasificar archivos en base al nombre
    for archivo in archivos:
        if archivo.startswith("ERROR_AL_LEER"):
            errores_lectura += 1
            continue
            
        partes = archivo.replace(".pdf", "").split("__")
        if len(partes) == 4:
            llave_base = f"{partes[0]}__{partes[1]}__{partes[2]}"
            tipo = partes[3]
            if tipo == "FACTURA":
                facturas[llave_base] = archivo
            elif tipo == "ST":
                sts[llave_base] = archivo

    # Encontrar las coincidencias y unir
    llaves_match = set(facturas.keys()).intersection(set(sts.keys()))
    
    for llave in llaves_match:
        ruta_factura = os.path.join(output_dir, facturas[llave])
        ruta_st = os.path.join(output_dir, sts[llave])
        
        # Crear documento unido
        doc_unido = fitz.open()
        
        # Abrir ambos PDFs. El orden importa: puedes insertar Factura primero y luego ST
        doc_f = fitz.open(ruta_factura)
        doc_s = fitz.open(ruta_st)
        
        doc_unido.insert_pdf(doc_f)
        doc_unido.insert_pdf(doc_s)
        
        nombre_reformas = f"{llave}__REFORMAS.pdf"
        doc_unido.save(os.path.join(output_dir, nombre_reformas))
        
        # Cerrar y eliminar los individuales
        doc_unido.close()
        doc_f.close()
        doc_s.close()
        
        os.remove(ruta_factura)
        os.remove(ruta_st)

    # Calcular sobrantes
    faltan_st = len(facturas) - len(llaves_match)
    faltan_factura = len(sts) - len(llaves_match)

    # Impresión en consola
    print("######################################")
    if faltan_st == 0 and faltan_factura == 0 and errores_lectura == 0:
        print("*Todos los documentos fueron unidos con Factura + ST exitosamente")
    else:
        if llaves_match and faltan_st == 0 and faltan_factura == 0:
            print("*Todos los documentos fueron unidos con Factura + ST exitosamente")
        if faltan_st > 0:
            print(f"*No se encontro el S.T. de ({faltan_st}) documentos Factura")
        if faltan_factura > 0:
            print(f"*No se encontro la Factura de ({faltan_factura}) documentos S.T.")
        if errores_lectura > 0:
            print(f"*No se lograron leer ({errores_lectura}) documentos")
    print("######################################")
