# Trower's Personal Accounting Handler
# Sólo funciona con años que tengan 4 dígitos...
import os, re, argparse
from datetime import datetime

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def getDateString(current:datetime = datetime.now()):
    day = int(datetime.now().strftime("%d"))
    if day > 28:
        week = 4
    else:
        week = day // 7
    return week, meses[int(datetime.now().strftime("%m"))-1]+datetime.now().strftime("%Y")

def getLastFileName(user, files):
    last = ""
    for f in files:
        #Sólo se tratarán ficheros cuyo formato de nombre sea "{user}{nombremes}{año}.txt"
        if f.startswith(user):
            year = re.search(r"\d{4}\.txt$", f)
            if year:
                month = f[len(user):year.span()[0]]
                if month in meses:
                    year = year.group()
                    if last:
                        if int(year) < int(last[-4:]) or meses.index(month) < meses.index(last[:-4]):
                            last = month + year
                    else:
                        last = month + year
    return last

def getFileHistory(user, rfol) -> list:
    files = os.listdir(rfol)
    files = [file for file in files if os.path.isfile(os.path.join(rfol, file) and file[-4:] == ".txt")] # Sólo ficheros que terminen en '.txt'
    his = []
    last = getLastFileName(user, files)
    while last:
        files.remove(last)
        his.insert(0, last)
        last = getLastFileName(user, files)
    return his

def parseAccounts(line):
    words = line.strip().split(' ')
    accs = []
    while words:
        cha = words.pop(0)
        accs.insert(int(cha)-1, words.pop(0))
    return accs

def printAccounts(accounts):
    for i, acc in enumerate(accounts):
        print("{0}: {1:.2f}€ ".format(i, acc), end=" ")
    print()

def printOptions():
    print("""Selecciona una opción:
    1 - Añadir saldo a una cuenta
    2 - Añadir saldo a varias cuentas
    3 - Quitar saldo de una cuenta
    4 - Quitar saldo de varias cuentas
    5 - Transferir saldo de una cuenta a otra
    6 - Mostrar transacciones de la semana
    7 - Mostrar transacciones de un mes
    8 - Salir""")

def userCommandInterface(rfol, currentfile, history):
    file = os.path.join(rfol, currentfile)
    with open(file, 'r') as f:
        lines = f.readlines()
    if not lines:
        with open(os.path.join(rfol, history[-1]), 'r') as prevf:
            accounts = parseAccounts(prevf.readlines()[-1])
        initAccountFile(rfol, currentfile, accounts)
    else:
        accounts = parseAccounts(lines[-1]) # La última línea siempre serán las cuentas actualizadas
    res = True
    while res != '8':
        printAccounts(accounts)
        printOptions()
        res = input()
    
    
def initAccountFile(rfol, name, accounts):
    with open(os.path.join(rfol, name), 'r') as f:
        for i, money in enumerate(accounts):
            f.write("{0}: {1:.2f}€ ".format(i, money))
        f.write("\n")

def argInit():
    parser = argparse.ArgumentParser(description="Script para facilitar el uso de cuentas bancarias lógicas o virtuales.")
    parser.add_argument("-u", "--user", help="Nombre de usuario identificador de sus cuentas virtuales")
    parser.add_argument("-p", "--pass", help="Contraseña para el descifrado de ficheros de cuentas")
    parser.add_argument("-R", "--rootfolder", help="Carpeta contenedora de los ficheros de cuentas")
    return parser.parse_args()

def main(args):
    if not args.user:
        user = input("Nombre de la cuenta a utilizar: ")
    else:
        user = args.user
    if not args.rootfolder:
        if os.name == 'nt':
            rfol = ".\\"
        else:
            rfol = "./"
    else:
        rfol = args.rootfolder
    week, datestr = getDateString()
    currentdatestr = user + datestr + ".txt"
    files = getFileHistory(user, rfol)
    if not files:
        res = input(f"El usuario {user} no tiene ficheros de cuenta previos. ¿Crear uno? (s/n)\n")
        if res != 's':
            exit(0)
        accnum = int(input(f"¿Cuántas cuentas lógicas poseerá el usuario? (Mínimo 1, máximo 9)\n"))
        if accnum < 1 or accnum > 9:
            print("Numero no válido de cuentas. Abortando...")
            exit(1)
        accounts = [0] * accnum
        initAccountFile(rfol, currentdatestr, accounts)
    else:
        print(f"Encontrado fichero/s de cuenta para usuario {user}.")
    if currentdatestr not in files:
        print(f"Creado nuevo fichero de cuenta {currentdatestr}.")
    rescode = userCommandInterface(rfol, currentdatestr, files) # Mejora: hacer una interfaz gráfica
    exit(rescode)

if __name__ == '__main__':
    main(argInit())