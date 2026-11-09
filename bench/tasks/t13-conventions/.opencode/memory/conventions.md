# Convencoes
1. Codigo em `src/`, testes em `tests/test_<modulo>.py`, framework `unittest`. Rodar: `python3 -m unittest discover -s tests -q`.
2. Erros de dominio sao classes de `src/errors.py` (subclasses de `BankError`). Nunca levante `ValueError`/`Exception` diretamente para regra de negocio.
3. Toda funcao/metodo publico tem type hints em todos os parametros e no retorno.
4. Valores monetarios sao `int` em centavos. Proibido `float` para dinheiro.
5. Proibido `print` em `src/`.
6. Operacoes que alteram duas contas sao atomicas: se falhar, nenhuma conta muda.
