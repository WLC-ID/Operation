def count_to_amount(n):
    if (n <= 0):
        return 1
    else:
        return 2*n
    
def format_material(material, n):
    return "nimbus{" + f"currency_id=\"{material}\",amount={count_to_amount(n)}" + "}"

def format_rpg(type, id, n):
    return "mmoitem{" + f"type={type},id={id}_{format(n, '02')},amount=1" + "}"

def construct_output(type, id, n):
    return {
        "type": type,
        "id": id + "_" + str(format(n, '02')),
        "amount": 1
    }