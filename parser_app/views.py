import os
import tempfile
import shutil
from django.http import FileResponse
from django.shortcuts import render
from .services import funcionalidad_1_separar_y_renombrar, funcionalidad_2_hacer_match_y_unir

def index(request):
    """Muestra la página principal con las dos opciones"""
    return render(request, 'parser_app/index.html')

def ejecutar_funcionalidad_1(request):
    """Funcionalidad 1: Separar y Renombrar"""
    if request.method == 'POST' and request.FILES.get('documento_principal'):
        pdf_file = request.FILES['documento_principal']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_pdf_path = os.path.join(temp_dir, 'input.pdf')
            output_dir = os.path.join(temp_dir, 'resultados_f1')
            
            with open(input_pdf_path, 'wb+') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)
                    
            # Ejecutar SOLO Funcionalidad 1
            funcionalidad_1_separar_y_renombrar(input_pdf_path, output_dir)
            
            zip_path_base = os.path.join(temp_dir, 'Archivos_Separados')
            shutil.make_archive(zip_path_base, 'zip', output_dir)
            
            return FileResponse(open(f"{zip_path_base}.zip", 'rb'), as_attachment=True, filename='Archivos_Separados.zip')
            
    return render(request, 'parser_app/index.html')

def ejecutar_funcionalidad_2(request):
    """Funcionalidad 2: Hacer Match y Unir"""
    if request.method == 'POST' and request.FILES.getlist('documentos_separados'):
        archivos_subidos = request.FILES.getlist('documentos_separados')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, 'resultados_f2')
            os.makedirs(output_dir)
            
            # Guardar los archivos que el usuario subió (que ya traen los nombres correctos)
            for archivo in archivos_subidos:
                ruta_archivo = os.path.join(output_dir, archivo.name)
                with open(ruta_archivo, 'wb+') as f:
                    for chunk in archivo.chunks():
                        f.write(chunk)
                        
            # Ejecutar SOLO Funcionalidad 2 (lee nombres, une y borra los originales en esa carpeta)
            funcionalidad_2_hacer_match_y_unir(output_dir)
            
            zip_path_base = os.path.join(temp_dir, 'Archivos_Unidos_Reformas')
            shutil.make_archive(zip_path_base, 'zip', output_dir)
            
            return FileResponse(open(f"{zip_path_base}.zip", 'rb'), as_attachment=True, filename='Archivos_Unidos_Reformas.zip')
            
    return render(request, 'parser_app/index.html')
