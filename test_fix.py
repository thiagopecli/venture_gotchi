#!/usr/bin/env python
"""Script para testar o conteúdo de messages"""

messages = ['Partida encerrada. Não é possível realizar novas ações.']

# Teste 1: substring em string
result = any('encerrada' in str(m) for m in messages)
print(f"Test 1 - 'encerrada' in messages: {result}")

# Teste 2: verificar cada uma
for msg in messages:
    print(f"Message: '{msg}'")
    print(f"  Type: {type(msg)}")
    print(f"  Str: '{str(msg)}'")
    print(f"  'encerrada' in str: {'encerrada' in str(msg)}")
