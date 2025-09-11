# Trower's Personal Accounting Handler
# Sólo funciona con años que tengan 4 dígitos...
import os, re, argparse
from sys import exit
from time import sleep
from datetime import datetime

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def getDateString(current:datetime = datetime.now()):
    day = int(datetime.now().strftime("%d"))
    if day > 28:
        week = 4
    else:
        week = ((day - 1) // 7) + 1
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
                    year = year.group()[:-4]
                    if last:
                        if int(year) < int(last[-4:]) or meses.index(month) < meses.index(last[:-4]):
                            last = month + year
                    else:
                        last = month + year
    if last:
        return user + last + ".txt"
    else:
        return ""

def getFileHistory(user, rfol) -> list:
    files = os.listdir(rfol)
    files = [file for file in files if os.path.isfile(os.path.join(rfol, file)) and file[-4:] == ".txt"] # Sólo ficheros que terminen en '.txt'
    his = []
    last = getLastFileName(user, files) #Ordenar según Mes y Año el listado de ficheros y filtrar si su nombre no cumple con el formato
    while last:
        files.remove(last)
        his.insert(0, last)
        last = getLastFileName(user, files)
    return his

def parseAccounts(line):
    words = line.strip().split(' ')
    accs = []
    while words:
        acc = int(words.pop(0)[0])-1
        money = words.pop(0)
        # Dará error si alguna de las cuentas no tiene un número representando la cantidad de dinero disponible
        money = float(re.search(r"\d+(\.\d{,2})?", money).group())
        accs.insert(acc, money)
    return accs

def printAccounts(accs):
    for i, acc in enumerate(accs):
        print("{0}: {1:.2f}€".format(i+1, acc), end=" ")
    print()

def updateAccounts(accs, lines):
    newline = ""
    for i, acc in enumerate(accs):
        newline += "{0}: {1:.2f}€ ".format(i+1, acc)
    lines[-1] = newline
    return lines

def printOptions():
    print("""Selecciona una opción:
    1 - Añadir saldo a una cuenta
    2 - Añadir saldo a varias cuentas
    3 - Quitar saldo de una cuenta
    4 - Quitar saldo de varias cuentas
    5 - Transferir saldo de una cuenta a otra
    6 - Mostrar transacciones de la semana
    7 - Mostrar transacciones de un mes
    8 - Mostrar la suma de todas las cuentas
    9 - Salir
    0 - Menú configuración""")

def checkWeeksInFile(file, lines, week):
    weekcount = 1
    while weekcount <= week:
        if f"Semana {weekcount}\n" not in lines: #Semanas sin movimientos
            lines.insert((weekcount - 1)*3 + 1, f"Semana {weekcount}\n")
            lines.insert((weekcount - 1)*3 + 2, ".\n")
            lines.insert((weekcount)*3, lines[0])
            with open(file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        weekcount += 1

def addToAccount(accs, lines, week):
    try:
        accind = int(input("¿A qué cuenta quieres añadir saldo? (Indica con un número) "))
        while accind > len(accs):
            accind = int(input(f"Cuenta no válida. Sólo hay {len(accs)} cuentas. ¿A qué cuenta quieres añadir saldo? "))
        money = round(float(input("¿Cuánto saldo quieres añadir? (Indica el número de euros sin ningún carácter especial, usando un punto para céntimos como decimales) ")), 2)
    except Exception as e:
        print("No es un número. Abortando operación...")
        return None
    subj = input("Introduce el asunto del movimiento: ")
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines.insert(dotind, "{0} {1:+.2f} {2}\n".format(accind, money, subj))
    accs[accind-1] += money
    lines = updateAccounts(accs, lines)
    return lines

def addToAccounts(accs, lines, week):
    try:
        accind = input("¿A qué cuentas quieres añadir saldo? (Indica con números separados por un espacio) ").strip().split(" ")
        accind = [int(i) for i in accind]
        accsnum = len(accs)
        while len(accind) > accsnum or any(i > accsnum for i in accind):
            accind = input(f"Demasiadas cuentas indicadas o cuenta no válida indicada. Sólo hay {len(accs)} cuentas. ¿A qué cuentas quieres añadir saldo? ").strip().split(" ")
            accind = [int(i) for i in accind]
        money = float(input("¿Cuánto saldo quieres añadir? (Indica el número de euros sin ningún carácter especial, usando un punto para céntimos como decimales) "))
        total = 1
        while total == 1:
            percents = []
            for i in accind[:-1]:
                per = input(f"¿Qué porcentaje del ingreso irá a la cuenta número {i}? (Indicar con un número entre 0 y 1, escribe decimales detrás del punto) 0.")
                per = round(float("."+per), 4)
                total -= per
                percents.append(per) # Entrada posiblemente no ordenada por número de cuenta
            total = round(total, 4)
            percents.append(total)
            print(f"Para la cuenta {accind[-1]} irá el {round(total*100, 2)}% ({total} restante).", end=" ")
            if total < 0:
                total = 1
                print()
            else:
                res = input("¿Porcentajes aceptables? (s/n) ")
                if res != 's':
                    return lines
    except:
        print("No es un número. Abortando operación...")
        return None
    newline = ""
    results = []
    for i, per in enumerate(percents):
        newline += f"{accind[i]+per},"
        results.append(round(money * per, 2)) # Mismo orden que percents
    #Para esos centimillos que no se aproximan bien
    if sum(results) > money:
        results[-1] -= (sum(results) - money) # Si hay que quitar céntimos, se quitan de la última cuenta indicada
    elif sum(results) < money:
        results[0] += (money - sum(results)) # Si hay que sumar céntimos, se suman a la primera cuenta indicada
    subj = input("Introduce el asunto del movimiento: ")
    newline = newline[:-1] + " {0:+.2f} {1} # ".format(money, subj)
    for i, res in enumerate(results):
        newline += f"{percents[i]*100}% = {results[i]}, "
        accs[accind[i]-1] += res
    newline = newline[:-2] + "\n"
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines.insert(dotind, newline)
    lines = updateAccounts(accs, lines)
    return lines

def withdrawFromAccount(accs, lines, week):
    try:
        accind = int(input("¿De qué cuenta quieres retirar saldo? (Indica con un número) "))
        while accind > len(accs):
            accind = int(input(f"Cuenta no válida. Sólo hay {len(accs)} cuentas. ¿A qué cuenta quieres añadir saldo? "))
        money = round(float(input("¿Cuánto saldo quieres retirar? (Indica el número de euros sin ningún carácter especial, usando un punto para céntimos como decimales) ")), 2)
    except Exception as e:
        print("No es un número. Abortando operación...")
        return None
    subj = input("Introduce el asunto del movimiento: ")
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines.insert(dotind, "{0} {1:+.2f} {2}\n".format(accind, -money, subj))
    accs[accind-1] -= money
    lines = updateAccounts(accs, lines)
    return lines

def withdrawFromAccounts(accs, lines, week):
    try:
        accind = input("¿De qué cuentas quieres retirar saldo? (Indica con números separados por un espacio) ").strip().split(" ")
        accind = [int(i) for i in accind]
        accsnum = len(accs)
        while len(accind) > accsnum or any(i > accsnum for i in accind):
            accind = input(f"Demasiadas cuentas indicadas o cuenta no válida indicada. Sólo hay {len(accs)} cuentas. ¿De qué cuentas quieres retirar saldo? ").strip().split(" ")
            accind = [int(i) for i in accind]
        money = float(input("¿Cuánto saldo quieres retirar? (Indica el número de euros sin ningún carácter especial, usando un punto para céntimos como decimales) "))
        total = 1
        while total == 1:
            percents = []
            for i in accind[:-1]:
                per = input(f"¿Qué porcentaje saldrá de la cuenta número {i}? (Indicar con un número entre 0 y 1, escribe decimales detrás del punto) 0.")
                per = round(float("."+per), 4)
                total -= per
                percents.append(per) # Entrada posiblemente no ordenada por número de cuenta
            total = round(total, 4)
            percents.append(total)
            print(f"De la cuenta {accind[-1]} saldrá el {round(total*100, 2)}% ({total} restante).", end=" ")
            if total < 0:
                total = 1
                print()
            else:
                res = input("¿Porcentajes aceptables? (s/n) ")
                if res != 's':
                    return lines
    except:
        print("No es un número. Abortando operación...")
        return None
    newline = ""
    results = []
    for i, per in enumerate(percents):
        newline += f"{accind[i]+per},"
        results.append(round(money * per, 2)) # Mismo orden que presenta precents (definido en accind)
    #Para esos centimillos que no se aproximan bien
    if sum(results) > money:
        results[-1] -= (sum(results) - money) # Igual que en addToAccounts
    elif sum(results) < money:
        results[0] += (money - sum(results))
    subj = input("Introduce el asunto del movimiento: ")
    newline = newline[:-1] + " {0:+.2f} {1} # ".format(-money, subj)
    for i, res in enumerate(results):
        newline += f"{percents[i]*100}% = {-res}, "
        accs[accind[i]-1] -= res 
    newline = newline[:-2] + "\n"
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines.insert(dotind, newline)
    lines = updateAccounts(accs, lines)
    return lines

def transferToAccount(accs, lines, week):
    try:
        ori = int(input("Indica el número de la cuenta de la que sacar saldo: "))
        des = int(input("Indica el número de la cuenta a la que meter saldo: "))
        while ori > len(accs) or des > len(accs):
            ori = int(input(f"Cuenta no válida. Sólo hay {len(accs)} cuentas. ¿De qué cuenta quieres sacar saldo? "))
            des = int(input("Indica el número de la cuenta a la que meter saldo: "))
        money = round(float(input("¿Cuánto saldo quieres transferir? (Indica el número de euros sin ningún carácter especial, usando un punto para céntimos como decimales) ")), 2)
    except Exception as e:
        print("No es un número. Abortando operación...")
        return None
    subj = input("Introduce el asunto del movimiento: ")
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines.insert(dotind, "{0}->{1} {2:.2f} {3}\n".format(ori, des, money, subj))
    accs[ori-1] -= money
    accs[des-1] += money
    lines = updateAccounts(accs, lines)
    return lines

def showWeek(lines, week):
    try:
        check = int(input("¿Qué semana quieres consultar? (Indica con un número del 1 al 4) "))
        while check < 1 or check > week:
            if check > week:
                check = int(input("Por mucho que quieras, todavía no podemos ver el futuro. ¿Qué semana quieres consultar? (Indica con un número del 1 al 4) "))
            else:
                check = int(input("Entrada no válida. ¿Qué semana quieres consultar? (Indica con un número del 1 al 4) "))
    except:
        print("No es un número. Abortando operación...")
        return None
    weekind = lines.index(f"Semana {check}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    aux = lines[weekind:dotind]
    if aux:
        for line in aux:
            print(line, end="")
    else:
        print("No hay transacciones en esa semana.")
    return lines

def showMonth(rfol, currentfile, lines):
    regex = input("¿Qué mes quieres consultar? (Indica nombre del mes o expresión regular) ")
    year = input("¿De qué año? ")
    user = currentfile[:currentfile.index(meses[int(datetime.now().strftime("%m"))-1])] # Sacar usuario del nombre del fichero actual
    files = os.listdir(rfol)
    # Sólo ficheros de texto que sean de este usuario, del año indicado, y cumplan con el formato
    files = [file for file in files if re.search(f"^{user}", file) and file[-8:] == f"{year}.txt"]
    files = [file for file in files if re.search(regex, file[len(user):-8])]
    if not files:
        print(f"No se han encontrado ficheros con los criterios especificados para el usuario {user}.")
    else:
        for file in files:
            print(f"Contenidos de {file}")
            with open(file, "r", encoding='utf-8') as f:
                cont = f.read()
            print(cont)
    return lines

def userCommandInterface(rfol, currentfile, week, history):
    file = os.path.join(rfol, currentfile)
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        with open(os.path.join(rfol, history[-1]), 'r', encoding='utf-8') as prevf:
            accounts = parseAccounts(prevf.readlines()[-1])
        initAccountFile(rfol, currentfile, accounts)
    else:
        accounts = parseAccounts(lines[-1]) # La última línea siempre serán las cuentas actualizadas
    checkWeeksInFile(file, lines, week)
    res = True
    while lines and res != '9':
        printAccounts(accounts)
        printOptions()
        res = input()
        if res == '1':
            lines = addToAccount(accounts, lines, week)
        elif res == '2':
            lines = addToAccounts(accounts, lines, week)
        elif res == '3':
            lines = withdrawFromAccount(accounts, lines, week)
        elif res == '4':
            lines = withdrawFromAccounts(accounts, lines, week)
        elif res == '5':
            lines = transferToAccount(accounts, lines, week)
        elif res == '6':
            lines = showWeek(lines, week)
        elif res == '7':
            lines = showMonth(rfol, currentfile, lines) #Mejorar para que aproveche la variable "history"
        elif res == '8':
            print(f"La suma de todas las cuentas es {sum(accounts)}€")
        elif res == '0':
            print("¡Todavía por implementar!")
        else:
            res = '9'
        if res != '9' and res != '0' and lines:
            with open(file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        elif not lines:
            return 2
    return 0
    
    
def initAccountFile(rfol, name, accs):
    with open(os.path.join(rfol, name), 'w', encoding='utf-8') as f:
        for i, money in enumerate(accs):
            f.write("{0}: {1:.2f}€ ".format(i+1, money))
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
            sleep(2)
            exit(1)
        accounts = [0] * accnum
        initAccountFile(rfol, currentdatestr, accounts)
    else:
        print(f"Encontrado fichero/s de cuenta para usuario {user}.")
    if currentdatestr not in files:
        print(f"Creado nuevo fichero de cuenta {currentdatestr}.")
    try:
        rescode = userCommandInterface(rfol, currentdatestr, week, files) # Mejora: hacer una interfaz gráfica
    except:
        sleep(4)
    exit(rescode)

if __name__ == '__main__':
    main(argInit())