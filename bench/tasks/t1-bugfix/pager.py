def paginate(items, size):
    """Divide items em páginas de tamanho `size`."""
    return [items[i * size:(i + 1) * size] for i in range(len(items) // size)]
