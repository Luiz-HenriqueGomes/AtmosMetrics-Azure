import sys; import os; sys.path.insert(0, os.path.abspath(".python_packages/lib/site-packages"))
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.dim_localidade import DimLocalidade

states = [
    {"estado": "AC", "nome": "Acre", "lat": -9.97, "lon": -67.81, "regiao": "Norte", "bioma": "AmazÃ´nia"},
    {"estado": "AL", "nome": "Alagoas", "lat": -9.66, "lon": -35.73, "regiao": "Nordeste", "bioma": "Mata AtlÃ¢ntica"},
    {"estado": "AP", "nome": "AmapÃ¡", "lat": 0.03, "lon": -51.06, "regiao": "Norte", "bioma": "AmazÃ´nia"},
    {"estado": "AM", "nome": "Amazonas", "lat": -3.10, "lon": -60.02, "regiao": "Norte", "bioma": "AmazÃ´nia"},
    {"estado": "BA", "nome": "Bahia", "lat": -12.97, "lon": -38.51, "regiao": "Nordeste", "bioma": "Caatinga"},
    {"estado": "CE", "nome": "CearÃ¡", "lat": -3.71, "lon": -38.54, "regiao": "Nordeste", "bioma": "Caatinga"},
    {"estado": "DF", "nome": "Distrito Federal", "lat": -15.78, "lon": -47.93, "regiao": "Centro-Oeste", "bioma": "Cerrado"},
    {"estado": "ES", "nome": "EspÃ­rito Santo", "lat": -20.31, "lon": -40.31, "regiao": "Sudeste", "bioma": "Mata AtlÃ¢ntica"},
    {"estado": "GO", "nome": "GoiÃ¡s", "lat": -16.68, "lon": -49.25, "regiao": "Centro-Oeste", "bioma": "Cerrado"},
    {"estado": "MA", "nome": "MaranhÃ£o", "lat": -2.53, "lon": -44.30, "regiao": "Nordeste", "bioma": "Cerrado"},
    {"estado": "MT", "nome": "Mato Grosso", "lat": -15.59, "lon": -56.09, "regiao": "Centro-Oeste", "bioma": "Cerrado"},
    {"estado": "MS", "nome": "Mato Grosso do Sul", "lat": -20.44, "lon": -54.64, "regiao": "Centro-Oeste", "bioma": "Pantanal"},
    {"estado": "MG", "nome": "Minas Gerais", "lat": -19.92, "lon": -43.93, "regiao": "Sudeste", "bioma": "Cerrado"},
    {"estado": "PA", "nome": "ParÃ¡", "lat": -1.45, "lon": -48.50, "regiao": "Norte", "bioma": "AmazÃ´nia"},
    {"estado": "PB", "nome": "ParaÃ­ba", "lat": -7.11, "lon": -34.86, "regiao": "Nordeste", "bioma": "Caatinga"},
    {"estado": "PR", "nome": "ParanÃ¡", "lat": -25.42, "lon": -49.27, "regiao": "Sul", "bioma": "Mata AtlÃ¢ntica"},
    {"estado": "PE", "nome": "Pernambuco", "lat": -8.04, "lon": -34.87, "regiao": "Nordeste", "bioma": "Caatinga"},
    {"estado": "PI", "nome": "PiauÃ­", "lat": -5.08, "lon": -42.80, "regiao": "Nordeste", "bioma": "Caatinga"},
    {"estado": "RJ", "nome": "Rio de Janeiro", "lat": -22.90, "lon": -43.20, "regiao": "Sudeste", "bioma": "Mata AtlÃ¢ntica"},
    {"estado": "RN", "nome": "Rio Grande do Norte", "lat": -5.79, "lon": -35.20, "regiao": "Nordeste", "bioma": "Caatinga"},
    {"estado": "RS", "nome": "Rio Grande do Sul", "lat": -30.03, "lon": -51.23, "regiao": "Sul", "bioma": "Pampa"},
    {"estado": "RO", "nome": "RondÃ´nia", "lat": -8.76, "lon": -63.90, "regiao": "Norte", "bioma": "AmazÃ´nia"},
    {"estado": "RR", "nome": "Roraima", "lat": 2.82, "lon": -60.67, "regiao": "Norte", "bioma": "AmazÃ´nia"},
    {"estado": "SC", "nome": "Santa Catarina", "lat": -27.59, "lon": -48.54, "regiao": "Sul", "bioma": "Mata AtlÃ¢ntica"},
    {"estado": "SP", "nome": "SÃ£o Paulo", "lat": -23.55, "lon": -46.63, "regiao": "Sudeste", "bioma": "Mata AtlÃ¢ntica"},
    {"estado": "SE", "nome": "Sergipe", "lat": -10.94, "lon": -37.07, "regiao": "Nordeste", "bioma": "Caatinga"},
    {"estado": "TO", "nome": "Tocantins", "lat": -10.21, "lon": -48.36, "regiao": "Norte", "bioma": "Cerrado"},
]

db = SessionLocal()

try:
    for st in states:
        existing = db.query(DimLocalidade).filter(
            DimLocalidade.municipio == st["nome"],
            DimLocalidade.estado == st["estado"]
        ).first()
        
        if existing:
            existing.latitude_ref = str(st["lat"])
            existing.longitude_ref = str(st["lon"])
            existing.pais = "Brasil"
            existing.continente = "AmÃ©rica do Sul"
            existing.codigo_iso = "BR"
        else:
            loc = DimLocalidade(
                municipio=st["nome"],
                estado=st["estado"],
                uf=st["estado"],
                regiao=st["regiao"],
                bioma=st["bioma"],
                pais="Brasil",
                continente="AmÃ©rica do Sul",
                latitude_ref=str(st["lat"]),
                longitude_ref=str(st["lon"]),
                codigo_iso="BR"
            )
            db.add(loc)
    
    db.commit()
    print("Sucesso! Estados do Brasil adicionados para o mapa meteorologico.")
except Exception as e:
    print("Erro:", e)
    db.rollback()
finally:
    db.close()
