import os
import psycopg2
from psycopg2.extras import RealDictConnection
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self, link: str = DATABASE_URL):
        self.db_link = link

    def get_connection(self):
        return psycopg2.connect(self.db_link, connection_factory=RealDictConnection)

    def initiate_tables(self):
        queries_criacao = [
            # Tabela de Modelos de Carro
            """
            CREATE TABLE IF NOT EXISTS modelos_carro (
                id SERIAL PRIMARY KEY,
                nome_modelo VARCHAR(100) NOT NULL,
                ano_carro INT NOT NULL,
                UNIQUE (nome_modelo, ano_carro)
            );
            """,
            # Tabela de Clientes
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                placa VARCHAR(10) UNIQUE NOT NULL,
                nome VARCHAR(100) NOT NULL,
                id_modelo_carro INT REFERENCES modelos_carro(id),
                numero_contato INT,
                cpf_cnpj VARCHAR(18) NOT NULL
            );
            """,
            # Tabela de Peças
            """
            CREATE TABLE IF NOT EXISTS pecas (
                id SERIAL PRIMARY KEY,
                nome_peca VARCHAR(100) NOT NULL,
                id_modelo_carro INT REFERENCES modelos_carro(id) NOT NULL,
                valor DECIMAL(10, 2) NOT NULL,
                quantidade_por_carro INT NOT NULL,
                estoque INT DEFAULT 10,
                desconto_par DECIMAL(10, 2) DEFAULT 0.00,
                UNIQUE (nome_peca, id_modelo_carro) 
            );
            """,
            #ÍNDICES DE PERFORMANCE
            "CREATE INDEX IF NOT EXISTS idx_clientes_placa ON clientes(placa);",
            "CREATE INDEX IF NOT EXISTS idx_pecas_modelo ON pecas(id_modelo_carro, nome_peca);"
        ]

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for query in queries_criacao:
                    cursor.execute(query)
            conn.commit()
        finally:
            conn.close()
            
        self._seed_banco()

    def _seed_banco(self):
        """Insere os modelos de carros e depois as peças, vinculando-os pelos IDs."""
 
        modelos_iniciais = [
            ("CHEVROLET ONIX 1.0", 2019),
            ("TOYOTA COROLLA XEI 2.0", 2015),
            ("JEEP COMPASS LONGITUDE 2.0 DIESEL", 2021),
            ("FIAT STRADA FREEDOM 1.3", 2022),
            ("VOLKSWAGEN GOL 1.6 G6", 2014)
        ]

        pecas_iniciais = [
            # CHEVROLET ONIX 1.0 (2019)
            ("PASTILHA DE FREIO DIANTEIRA", "CHEVROLET ONIX 1.0", 2019, 142.00, 1, 5.00),
            ("FILTRO DE ÓLEO", "CHEVROLET ONIX 1.0", 2019, 35.00, 1, 0.00),
            ("AMORTECEDOR DIANTEIRO", "CHEVROLET ONIX 1.0", 2019, 340.00, 2, 8.00),
            ("DISCO DE FREIO DIANTEIRO", "CHEVROLET ONIX 1.0", 2019, 160.00, 2, 10.00),
            
            # TOYOTA COROLLA XEI 2.0 (2015)
            ("PASTILHA DE FREIO DIANTEIRA", "TOYOTA COROLLA XEI 2.0", 2015, 180.00, 1, 1.50),
            ("FILTRO DE ÓLEO", "TOYOTA COROLLA XEI 2.0", 2015, 45.00, 1, 0.00),
            ("AMORTECEDOR DIANTEIRO", "TOYOTA COROLLA XEI 2.0", 2015, 798.00, 2, 7.00),
            ("DISCO DE FREIO DIANTEIRO", "TOYOTA COROLLA XEI 2.0", 2015, 280.00, 2, 10.00),
            
            # JEEP COMPASS LONGITUDE 2.0 DIESEL (2021)
            ("PASTILHA DE FREIO DIANTEIRA", "JEEP COMPASS LONGITUDE 2.0 DIESEL", 2021, 240.00, 1, 6.00),
            ("FILTRO DE ÓLEO DIESEL", "JEEP COMPASS LONGITUDE 2.0 DIESEL", 2021, 55.00, 1, 1.00),
            ("AMORTECEDOR DIANTEIRO", "JEEP COMPASS LONGITUDE 2.0 DIESEL", 2021, 650.00, 2, 8.00),
            ("DISCO DE FREIO DIANTEIRO", "JEEP COMPASS LONGITUDE 2.0 DIESEL", 2021, 320.00, 2, 12.00),
            
            # FIAT STRADA FREEDOM 1.3 (2022)
            ("PASTILHA DE FREIO DIANTEIRA", "FIAT STRADA FREEDOM 1.3", 2022, 130.00, 1, 5.00),
            ("FILTRO DE ÓLEO", "FIAT STRADA FREEDOM 1.3", 2022, 38.00, 1, 8.00),
            ("AMORTECEDOR DIANTEIRO", "FIAT STRADA FREEDOM 1.3", 2022, 390.00, 2, 5.00),
            ("KIT DE EMBREAGEM", "FIAT STRADA FREEDOM 1.3", 2022, 1108.00, 1, 8.00),
            
            # VOLKSWAGEN GOL 1.6 G6 (2014)
            ("PASTILHA DE FREIO DIANTEIRA", "VOLKSWAGEN GOL 1.6 G6", 2014, 95.00, 1, 5.00),
            ("FILTRO DE ÓLEO", "VOLKSWAGEN GOL 1.6 G6", 2014, 30.00, 1, 7.00),
            ("AMORTECEDOR DIANTEIRO", "VOLKSWAGEN GOL 1.6 G6", 2014, 290.00, 2, 8.00),
            ("DISCO DE FREIO DIANTEIRO", "VOLKSWAGEN GOL 1.6 G6", 2014, 140.00, 2, 5.00)
        ]

        query_insert_modelos = """
            INSERT INTO modelos_carro (nome_modelo, ano_carro)
            VALUES (%s, %s)
            ON CONFLICT (nome_modelo, ano_carro) DO NOTHING;
        """

        query_insert_pecas = """
            INSERT INTO pecas (nome_peca, id_modelo_carro, valor, quantidade_por_carro, desconto_par)
            VALUES (
                %s, 
                (SELECT id FROM modelos_carro WHERE nome_modelo = %s AND ano_carro = %s),
                %s, %s, %s
            )
            ON CONFLICT (nome_peca, id_modelo_carro) DO NOTHING;
        """
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
        
                for modelo in modelos_iniciais:
                    cursor.execute(query_insert_modelos, modelo)
                
                for peca in pecas_iniciais:
                    cursor.execute(query_insert_pecas, peca)
                    
            conn.commit()
        finally:
            conn.close()

# Instância global 
db = Database()