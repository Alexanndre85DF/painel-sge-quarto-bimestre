"""
Utilitários para obter informações de IP e navegador do usuário
"""
import streamlit as st
import requests
import unicodedata
import re

def get_client_ip() -> str:
    """Obtém o IP do cliente através do Streamlit"""
    try:
        # Streamlit não expõe diretamente o IP, então usamos serviços externos
        # como fallback para desenvolvimento
        try:
            # Tenta obter IP local primeiro (para desenvolvimento)
            response = requests.get('https://httpbin.org/ip', timeout=5)
            if response.status_code == 200:
                return response.json().get('origin', '127.0.0.1')
        except:
            pass
        
        # Fallback para IP local
        return '127.0.0.1'
    except Exception:
        return 'Unknown'

def get_user_agent() -> str:
    """Obtém informações do navegador do usuário"""
    try:
        # Streamlit não expõe user-agent diretamente
        # Para uma implementação mais robusta, seria necessário
        # usar headers HTTP customizados
        return st.get_option("browser.gatherUsageStats") and "Streamlit App" or "Unknown Browser"
    except Exception:
        return "Unknown Browser"

def get_client_info() -> dict:
    """Obtém informações completas do cliente"""
    return {
        'ip': get_client_ip(),
        'user_agent': get_user_agent(),
        'session_id': st.session_state.get('session_id', 'unknown')
    }

def normalize_city_name(city_name: str) -> str:
    """Normaliza o nome da cidade para comparação (remove acentos, converte para minúsculas)"""
    if not city_name:
        return ""
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', str(city_name))
    city_normalized = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    # Converte para minúsculas, remove espaços extras e remove sufixos comuns
    city_clean = city_normalized.lower().strip()
    city_clean = re.sub(r'\s*-\s*[A-Z]{2}\s*$', '', city_clean)  # Remove "- TO", "-TO", etc
    city_clean = re.sub(r'\s*,\s*.*$', '', city_clean)  # Remove tudo após vírgula
    return city_clean

def get_city_from_ip(ip: str = None) -> dict:
    """
    Obtém a cidade do IP usando API de geolocalização
    Se IP não for fornecido, usa API que detecta automaticamente o IP do cliente
    """
    try:
        if ip and ip not in ['127.0.0.1', 'localhost', 'Unknown']:
            # Se tem IP específico, usar ele
            url = f'http://ip-api.com/json/{ip}?fields=status,message,city,regionName,country'
        else:
            # Se não tem IP ou é local, usar API que detecta automaticamente
            # Esta API detecta o IP de quem faz a requisição
            url = 'http://ip-api.com/json/?fields=status,message,city,regionName,country,query'
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'city': data.get('city', '').strip(),
                    'region': data.get('regionName', '').strip(),
                    'country': data.get('country', '').strip(),
                    'ip': data.get('query', ''),
                    'success': True
                }
            else:
                return {
                    'city': None,
                    'region': None,
                    'country': None,
                    'ip': None,
                    'success': False,
                    'error': data.get('message', 'Erro na API')
                }
        else:
            return {
                'city': None,
                'region': None,
                'country': None,
                'ip': None,
                'success': False,
                'error': f'Erro HTTP {response.status_code}'
            }
    except requests.exceptions.Timeout:
        return {
            'city': None,
            'region': None,
            'country': None,
            'ip': None,
            'success': False,
            'error': 'Timeout na requisição'
        }
    except Exception as e:
        return {
            'city': None,
            'region': None,
            'country': None,
            'ip': None,
            'success': False,
            'error': str(e)
        }

def is_city_allowed(city_name: str, allowed_cities: list) -> bool:
    """Verifica se a cidade está na lista de cidades permitidas"""
    if not city_name:
        return False
    
    city_normalized = normalize_city_name(city_name)
    
    for allowed_city in allowed_cities:
        allowed_normalized = normalize_city_name(allowed_city)
        if city_normalized == allowed_normalized:
            return True
    
    return False
