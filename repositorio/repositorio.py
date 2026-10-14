from typing import  Any
from psycopg2.extensions import connection

class RepositorioBot:
    def __init__(self, db_connection : connection):
        self.conn = db_connection

    def buscar_clientes_por_placas(self, placas: list[str]) -> list[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                c.placa, 
                c.nome, 
                c.numero_contato, 
                c.cpf_cnpj, 
                c.id_modelo_carro
            FROM 
                clientes c
            WHERE 
                c.placa = ANY(%s);
        """, placas)
        resultados = cursor.fetchall()
        return resultados
            
    
   