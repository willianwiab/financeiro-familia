#!/usr/bin/env python3
# Gera a cópia do app para a instância da irmã (financeiro-manfrin),
# a partir do index.html principal, trocando apenas o firebaseConfig.
# Rode sempre que atualizar o index.html principal:  python3 gerar-manfrin.py
import re, os, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(RAIZ, 'index.html')
DEST_DIR = os.path.join(RAIZ, '_deploy-manfrin')
DEST = os.path.join(DEST_DIR, 'index.html')

CONFIG_MANFRIN = '''const firebaseConfig = {
  apiKey: "AIzaSyBDFr8t0sWmN60zj68g7PU6yoZ6XNw9Amo",
  authDomain: "financeiro-manfrin.firebaseapp.com",
  projectId: "financeiro-manfrin",
  storageBucket: "financeiro-manfrin.firebasestorage.app",
  messagingSenderId: "580878883457",
  appId: "1:580878883457:web:8f4e1bfa204b0ab52f0b80"
};'''

s = open(SRC, encoding='utf-8').read()

# Substitui o bloco const firebaseConfig = { ... }; inteiro
novo, n = re.subn(r'const firebaseConfig = \{.*?\};', CONFIG_MANFRIN, s, count=1, flags=re.S)
if n != 1:
    print('ERRO: não encontrei o bloco firebaseConfig'); sys.exit(1)
if 'financeiro-pessoal-bda5d' in novo:
    print('ERRO: ainda restou referência ao projeto original'); sys.exit(1)

os.makedirs(DEST_DIR, exist_ok=True)
open(DEST, 'w', encoding='utf-8').write(novo)
print('OK ->', DEST, '(', len(novo), 'bytes )')
print('projeto:', 'financeiro-manfrin')
