import sqlfluff
import sys
import os

def validate_sql_file(file_path, dialect='ansi', templater='jinja', exclude_rules=None, only_syntax=False):
    """
    Valida la sintaxis de un archivo SQL usando sqlfluff.
    
    Args:
        file_path (str): Ruta al archivo SQL.
        dialect (str): Dialecto SQL (ansi, mysql, postgres, etc.).
        templater (str): Motor de plantillas ('jinja', 'raw', 'placeholder').
        exclude_rules (list): Lista de códigos de reglas a excluir.
        only_syntax (bool): Si es True, solo muestra errores de parsing (PRS).
        
    Returns:
        list: Lista de diccionarios con los errores encontrados.
    """
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return None

    print(f"Validando '{file_path}' con dialecto '{dialect}' y templater '{templater}'...")
    
    # Realizar el linting
    try:
        # Configuración para ignorar variables estilo Python {var} si usamos 'placeholder'
        if templater == 'placeholder':
            pass

        lint_result = sqlfluff.lint(
            sql_content, 
            dialect=dialect, 
            templater=templater,
            exclude_rules=exclude_rules
        )
        
        # Filtrar si solo se piden errores de sintaxis
        if only_syntax:
            lint_result = [v for v in lint_result if v['code'].startswith('PRS')]
            
    except Exception as e:
        print(f"Error durante la validación: {e}")
        return None

    if not lint_result:
        print("✅ No se encontraron errores de sintaxis.")
        return []
    
    print(f"⚠️ Se encontraron {len(lint_result)} problemas:")
    
    formatted_errors = []
    for violation in lint_result:
        # Estructura del violation: 
        # {'start_line_no': 1, 'start_line_pos': 1, 'code': 'L001', 'description': '...', ...}
        line_no = violation.get('start_line_no', violation.get('line_no', '?'))
        line_pos = violation.get('start_line_pos', violation.get('line_pos', '?'))
        
        error_msg = (
            f"Línea {line_no}, Pos {line_pos}: "
            f"[{violation['code']}] {violation['description']}"
        )
        print(error_msg)
        formatted_errors.append(violation)
        
    return formatted_errors

def fix_sql_file(file_path, dialect='ansi'):
    """
    Intenta corregir automáticamente los errores de formato en el archivo SQL.
    """
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        fixed_content = sqlfluff.fix(sql_content, dialect=dialect)
        
        if fixed_content == sql_content:
            print("No se realizaron cambios (el archivo ya estaba correcto o no se pudieron arreglar los errores).")
            return

        # Guardar copia de seguridad
        backup_path = file_path + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        print(f"Copia de seguridad guardada en '{backup_path}'")
        
        # Guardar archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Archivo corregido y guardado: '{file_path}'")
        
    except Exception as e:
        print(f"Error al corregir el archivo: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validador de archivos SQL usando sqlfluff")
    parser.add_argument("file", help="Ruta al archivo SQL")
    parser.add_argument("--dialect", default="ansi", help="Dialecto SQL (mysql, postgres, ansi, etc.)")
    parser.add_argument("--templater", default="jinja", choices=["jinja", "raw", "placeholder"], 
                        help="Motor de plantillas. Usa 'raw' si tienes variables {var} que dan error.")
    parser.add_argument("--fix", action="store_true", help="Intentar corregir errores automáticamente")

    args = parser.parse_args()
    
    if args.fix:
        fix_sql_file(args.file, args.dialect)
    else:
        validate_sql_file(args.file, args.dialect, args.templater)
