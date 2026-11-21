# Trower's Personal Accounting Handler
# Sólo funciona con años que tengan 4 dígitos...
import os, re, json, argparse
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
                        if int(year) < int(last[-4:]) or (int(year) == int(last[-4:]) and meses.index(month) < meses.index(last[:-4])):
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
        his.append(last)
        last = getLastFileName(user, files)
    return his

def parseAccounts(line):
    words = line.strip().split(' ')
    accs = []
    while words:
        acc = int(words.pop(0)[0])-1
        money = words.pop(0)
        # Dará error si alguna de las cuentas no tiene un número representando la cantidad de dinero disponible
        money = float(re.search(r"-*\d+(\.\d{,2})?", money).group()) # type: ignore
        accs.insert(acc, money)
    return accs

def printCurrentAccounts(accs):
    for i, acc in enumerate(accs):
        print("{0}: {1:.2f}€".format(i+1, acc), end=" ")
    week, month = getDateString()
    print(f"- {month}, Semana {week}")

# Sustituir la última línea por el saldo actual de las cuentas
def updateAccounts(accs, lines):
    newline = ""
    for i, acc in enumerate(accs):
        newline += "{0}: {1:.2f}€ ".format(i+1, acc)
    lines[-1] = newline + "\n"
    return lines

def printOptions():
    print(""" ¡Bienvenido a TPAH!
    Selecciona una opción:
    1 - Añadir saldo
    2 - Quitar saldo
    3 - Transferir saldo de una cuenta a otra
    4 - Mostrar transacciones de la semana
    5 - Mostrar transacciones de un mes
    6 - Mostrar transacciones totales por mes según año
    7 - Mostrar suma de saldo actual en cuentas
    9 - Salir
    0 - Menú configuración""")

def printConfig():
    print("""Menú configuración
    1 - Agregar cuenta
    2 - Modificar cuenta
    3 - Combinar cuentas
    4 - Borrar cuenta (sólo si el balance es 0)
    5 - Mostrar información de las cuentas
    6 - Guardar cambios realizados (guardado automático a la vuelta del menú principal)
    7 - Ayuda
    9 - Menú principal
    91 - Volver al menú principal sin guardar configuración (no se guardarán cambios realizados en la configuración)""")

def printHelp():
    print("""Este menú sólo te enseñará a usar la aplicación, sin alterar tus cuentas actuales.
    ¿Qué información necesitas?
    1 - Añadir, quitar o transferir saldo
    2 - Mostrar transacciones y sumas totales
    3 - Configurar cuentas
    0 - Volver""")

def checkWeeksInFile(file, lines, week):
    weekcount = 1
    #lastline = len(lines) - 1
    accline = lines[-1] #Las cuentas actualizadas siempre son la última línea
    while weekcount <= week: #Semanas sin movimientos
        if f"Semana {weekcount}\n" not in lines:
            lines.append(f"Semana {weekcount}\n")
            lines.append(".\n")
            lines.append(accline) #El último caracter de accline no es un salto de línea
            with open(file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        weekcount += 1

"""def addToAccount(accs, lines, week):
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
    return lines"""

def addToAccounts(accs, lines, week):
    try:
        accind = input("¿A qué cuentas quieres añadir saldo? (Indica con números separados por un espacio) ").strip().split(" ")
        accind = [int(i) for i in accind]
        accsnum = len(accs)
        accindsnum = len(accind)
        while accindsnum > accsnum or any(i > accsnum for i in accind):
            accind = input(f"Detectada cuenta no válida ó demasiadas cuentas indicadas. Sólo hay {len(accs)} cuentas. ¿A qué cuentas quieres añadir saldo? ").strip().split(" ")
            accind = [int(i) for i in accind]
        money = float(input("¿Cuánto saldo quieres añadir? (Indica el número de euros sin ningún carácter especial, usando un punto para céntimos como decimales) "))
        # Implementar forma rápida de operar si sólo se indica una cuenta
        if accindsnum < 2:
            percents = [1]
        else:
            total = 1 # Ir decrementándolo para obtener automáticamente el resto de porcentaje
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
                if total < 0: # En caso de que el total no encaje entre tanta resta
                    total = 1
                    print()
                else:
                    res = input("¿Porcentajes aceptables? (s/n) ")
                    if res != 's':
                        return lines
    except:
        print("No es un número. Abortando operación...")
        return None
    if accindsnum < 2:
        accind = accind[0]
        subj = input("Introduce el asunto del movimiento: ")
        weekind = lines.index(f"Semana {week}\n")
        dotind = lines[weekind:].index(".\n") + weekind
        lines.insert(dotind, "{0} {1:+.2f} {2}\n".format(accind, money, subj))
        accs[accind-1] += money
    else:
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
            newline += f"{round(percents[i]*100, 2)}% = {results[i]}, "
            accs[accind[i]-1] += res
        newline = newline[:-2] + "\n"
        weekind = lines.index(f"Semana {week}\n")
        dotind = lines[weekind:].index(".\n") + weekind
        lines.insert(dotind, newline)
    lines = updateAccounts(accs, lines)
    return lines

"""def withdrawFromAccount(accs, lines, week):
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
    return lines"""

def withdrawFromAccounts(accs, lines, week):
    try:
        accind = input("¿De qué cuentas quieres retirar saldo? (Indica con números separados por un espacio) ").strip().split(" ")
        accind = [int(i) for i in accind]
        accsnum = len(accs)
        accindsnum = len(accind)
        while accindsnum > accsnum or any(i > accsnum for i in accind):
            accind = input(f"Demasiadas cuentas indicadas o cuenta no válida indicada. Sólo hay {len(accs)} cuentas. ¿De qué cuentas quieres retirar saldo? ").strip().split(" ")
            accind = [int(i) for i in accind]
        money = float(input("¿Cuánto saldo quieres retirar? (Indica el número de euros sin ningún carácter especial, usando un punto para céntimos como decimales) "))
        if accindsnum < 2:
            percents = [1]
        else:        
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
    if accindsnum < 2:
        accind = accind[0]
        subj = input("Introduce el asunto del movimiento: ")
        weekind = lines.index(f"Semana {week}\n")
        dotind = lines[weekind:].index(".\n") + weekind
        lines.insert(dotind, "{0} {1:+.2f} {2}\n".format(accind, -money, subj))
        accs[accind-1] -= money
    else:
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
            newline += f"{round(percents[i]*100, 2)}% = {-res}, "
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
    elif files[-1] != files[0]:
        print(f"Se han encontrado varios ficheros buscando por mes \"{regex}\". Por favor, sé más específico")
    else:
        for file in files:
            print(f"Movimientos en {[m for m in meses if re.search(regex, m)][0]} de {year}:")
            with open(file, "r", encoding='utf-8') as f:
                cont = f.read()
            print(cont)
    return lines

def showYear(rfol, currentfile, lines):
    year = input("¿Qué año quieres consultar? ")
    user = currentfile[:currentfile.index(meses[int(datetime.now().strftime("%m"))-1])] # Sacar usuario del nombre del fichero actual
    files = os.listdir(rfol)
    # Sólo ficheros de texto que sean de este usuario, del año indicado, y cumplan con el formato
    files = [file for file in files if re.search(f"^{user}", file) and file[-8:] == f"{year}.txt"]
    if not files:
        print(f"No se han encontrado ficheros de {user} para el año {year}.")
    else:
        totaltotal = 0
        for m in meses:
            f = [file for file in files if re.search(m, file[len(user):-8])]
            if f:
                f = f[0]
            else:
                continue
            with open(f, "r", encoding='utf-8') as f:
                cont = f.readlines()
            indot = False # Alterna True y False para ver si estoy entre "Semana X" y "." o no
            total = 0 # Total de transacciones
            # Procesado lineal de líneas
            for li in cont:
                if li.startswith("Semana "):
                    indot = True
                    continue
                elif li == ".\n":
                    indot = False
                if indot: total += 1
            print(f"{m} -> {total} transacciones")
            totaltotal += total
        print(f"En {year} se han realizado {totaltotal} transacciones en total")
    return lines

# Actualizar líneas correspondientes en el fichero según se modifique la configuración
# Cuidado, el control de errores es mínimo; 
# newacc tiene que ser el número de cuenta inmediatamente superior,
# oldacc tiene que encajar con el número de cuentas, etc
def configAccounts(accs, lines, oldacc=0, newacc=0):
    # Añadir cuenta con saldo a 0
    if newacc > 0 and oldacc == 0:
        accs += [0]
    # Eliminar cuenta con saldo 0 (comprobar error, en este caso sí)
    elif newacc == 0 and oldacc > 0:
        if accs[oldacc-1] != 0:
            return lines
        accs = accs[:oldacc-1] + accs[oldacc:]
    # Combinar cuentas (newacc es la cuenta destino, no pueden ser la misma cuenta)
    elif newacc > 0 and oldacc > 0:
        if newacc == oldacc:
            return lines
        accs[newacc-1] += accs[oldacc-1]
        accs = accs[:oldacc-1] + accs[oldacc:]
    # No hacer nada
    else:
        return lines
    lines = updateAccounts(accs, lines)
    return lines

# Transferencias automáticas según límites mínimos y máximos de las cuentas
# No se se sacará dinero de la cuenta de reserva si no tiene saldo o saldo negativo
def checkLimitAccount(conf, accs, week, lines):
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    for ind, c in enumerate(conf["accounts"]):
        bkpind = c["Cuenta reserva"]
        if c["Mínimo"] and bkpind > 0 and accs[bkpind-1] > 0 and c["Mínimo"] > accs[ind]:
            diff = c["Mínimo"] - accs[ind]
            if accs[bkpind-1] < diff: diff = accs[bkpind-1]
            accs[bkpind-1] -= round(diff, 2)
            accs[ind] += round(diff, 2)
            lines.insert(dotind, "{0}->{1} {2:.2f} {3}\n".format(bkpind, ind+1, diff, "Mínimo establecido"))
        elif c["Máximo"] and bkpind > 0 and c["Máximo"] < accs[ind]:
            diff = accs[ind] - c["Máximo"]
            accs[ind] -= round(diff, 2)
            accs[bkpind-1] += round(diff, 2)
            lines.insert(dotind, "{0}->{1} {2:.2f} {3}\n".format(bkpind, ind+1, diff, "Máximo permitido"))
    lines = updateAccounts(accs, lines)
    return lines

# Crear configuración de cuenta
def createAccount(conf, accs, week, lines = None):
    accind = len(accs)+1
    if accind > 9:
        print(f"No es posible tener más de 9 cuentas simultáneas.")
        return lines, conf
    skip = input(f"Configurando cuenta {accind}. ¿Asignar nombre y descripción? (S/N) ")
    accobj = {
        "Nombre": f"Cuenta {accind}",
        "Saldo": 0,
        "Descripción": f"Configuración por defecto para cuenta {accind}",
        "Creada el": datetime.now().strftime("%Y/%m/%d %H:%M"),
        "Modificada el": datetime.now().strftime("%Y/%m/%d %H:%M"),
        "Mínimo": None,
        "Máximo": None,
        "Cuenta reserva": 0
    }
    if skip == 'N' and not lines: return accobj
    if skip != 'N':
        print(f"Los siguientes campos son opcionales y pueden quedarse en blanco.")
        name = input("Escribe el nombre de la cuenta: ")
        desc = input("Incluye una descripción de la cuenta: ")
        accobj["Nombre"] = name
        accobj["Descripción"] = desc
    """
    money, mini, maxi = None, None, None
    while money in ['', None]:
        money = input("¿ inicial? (Opcional) ")
        if money == '': 
            money = 0
        else:
            money = re.search('^[-+]?\\d+(\\.\\d{,2})', money)
            if money:
                money = money.group(0)
            else:
                print(f"Numero no válido. Inténtalo de nuevo.")
    """
    # Ejecución de función en proceso de creación de usuario
    if not lines:
        return accobj
    conf["accounts"].append(accobj)
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines.insert(dotind, "{0} => Cuenta creada.\n".format(accind))
    lines = configAccounts(accs, lines, newacc=accind)
    return lines, conf

# Modificar cuenta
def modifyAccount(conf, accs, week, lines):
    accind = input(f"¿Número de la cuenta a modificar? (Del 1 al {len(conf['accounts'])}) ")
    if not accind.isdigit() or accind == "0":
        print("No es un número válido, abortando...")
        return lines, conf
    ind = int(accind) - 1
    if not ind < len(conf["accounts"]):
        print("Cuenta no existente, abortando...")
        return lines, conf
    name = input(f"Nombre de cuenta: {conf['accounts'][ind]["Nombre"]}\nNombre nuevo: ")
    if not name:
        print("El nombre no puede quedarse en blanco. Vuelve a intentarlo")
        return lines, conf
    desc = input(f"Descripción: {conf['accounts'][ind]["Descripción"]}\nDescripción nueva: ")
    minmax = input(f"""A cada cuenta se le puede asignar una cuenta de reserva ya creada para configurar un límite máximo de saldo y un límite mínimo.
Si el saldo de la cuenta no llega al mínimo, se saca dinero de la cuenta de reserva para alcanzarlo si es posible.
Si el saldo de la cuenta sobrepasa el máximo, el saldo sobrante se manda a la cuenta de reserva. Estas operaciones se hacen automáticamente.
Para evitar bucles con las transacciones automáticas, la cuenta de reserva asociada no puede tener, a su vez, una cuenta de reserva propia.
También puedes cambiar los límites anteriormente configurados, configurar una cuenta de reserva diferente ó borrar la existente para la cuenta {accind}.
¿Configurar mínimo, máximo y cuenta de reserva? (S/N) """)
    bkpacc = 0
    if minmax == 'S':
        while bkpacc != -1 and (bkpacc == 0 or bkpacc > len(conf["accounts"])):
            bkpacc = input("¿Qué cuenta se va a usar de reserva? (Dejar en blanco para no tener cuenta de reserva configurada) ")
            if bkpacc == "": bkpacc = -1
            elif bkpacc and not bkpacc.isdigit(): 
                print("No es un número válido.")
                bkpacc = 0
            elif bkpacc:
                bkpacc = int(bkpacc)
                if bkpacc > len(conf["accounts"]):
                    print("Cuenta inexistente")
                elif bkpacc == int(accind):
                    print("Esta cuenta es la actual, no es posible asignar la propia cuenta como cuenta de reserva")
                elif conf["accounts"][bkpacc-1]["Cuenta reserva"] != 0:
                    print(f"""No se puede asignar la cuenta número {bkpacc} como cuenta de reserva porque la cuenta {bkpacc} tiene configurada la cuenta {conf["accounts"][bkpacc-1]["Cuenta reserva"]} como cuenta de reserva.
Borra la cuenta de reserva de la cuenta {bkpacc} si quieres usarla como reserva de la cuenta {accind}.""")
                    bkpacc = 0
            else: bkpacc = 0
    if bkpacc > 0:
        mini = input(f"¿Límite mínimo de saldo a mantener en la cuenta número {accind}? (Indicar hasta 2 decimales, dejar en blanco para no usar) ")
        while mini and not re.search(r"^[+-]?\d+(\.\d{,2})?", mini):
            print("Mínimo no válido. Por favor, indica el saldo con un número con, como máximo, dos decimales.")
            mini = input(f"¿Límite mínimo de saldo a mantener en la cuenta número {accind}? ")
        maxi = input(f"¿Límite máximo de saldo a respetar en la cuenta número {accind}? (Indicar hasta 2 decimales, dejar en blanco para no usar) ")
        while maxi and not re.search(r"^[+-]?\d+(\.\d{,2})?", maxi):
            print("Máximo no válido. Por favor, indica el saldo con un número con, como máximo, dos decimales.")
            maxi = input(f"¿Límite máximo de saldo a respetar en la cuenta número {accind}? ")
        if mini:
            mini = round(float(mini), 2)
            print("Mínimo de {0:.2f}.".format(mini), end=" ")
        elif mini == '': mini = None
        if maxi:
            maxi = round(float(maxi), 2)
            print("Máximo de {0:.2f}.".format(maxi), end=" ")
        elif maxi == '': maxi = None
        minmax = input(f"La cuenta de reserva será la cuenta número {bkpacc}. ¿Correcto? (S/N) ")
        if minmax != 'S':
            print("No se ha configurado nueva cuenta de reserva, límite mínimo ó límite máximo.")
            bkpacc = conf["accounts"][ind]["Cuenta reserva"]
            mini = conf['accounts'][ind]["Mínimo"]
            maxi = conf['accounts'][ind]["Máximo"]
    elif bkpacc == -1:
        mini = None
        maxi = None
        bkpacc = 0
    conf['accounts'][ind]["Nombre"] = name
    conf['accounts'][ind]["Descripción"] = desc
    conf['accounts'][ind]["Mínimo"] = mini
    conf["accounts"][ind]["Máximo"] = maxi
    conf["accounts"][ind]["Cuenta reserva"] = bkpacc
    conf['accounts'][ind]["Modificada el"] = datetime.now().strftime("%Y/%m/%d %H:%M")
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    if minmax == 'S':
        lines.insert(dotind, "{0} => Config modificada. {1}, {2}.\n".format(accind, (f"Nuevo mínimo {mini}" if mini is not None else "Mínimo no definido"), (f"Nuevo máximo {maxi}" if maxi is not None else "máximo no definido")))
    lines = checkLimitAccount(conf, accs, week, lines)
    print(f"Cuenta {accind} ({conf['accounts'][ind]["Nombre"]}) modificada con éxito.")
    return lines, conf

#Combinar cuentas (tener en cuenta las cuentas de reserva configuradas)
def mergeAccounts(conf, accs, week, lines):
    dest = input("Primera cuenta a combinar con otra: ")
    if not dest.isdigit() or dest == "0":
        print("No es un número válido, abortando...")
        return lines, conf
    dest = int(dest) - 1
    if not dest < len(conf["accounts"]):
        print("Cuenta no existente, abortando...")
        return lines, conf
    ori = input("Segunda cuenta a combinar con la primera (Atención, ¡esta cuenta y su configuración serán eliminadas!): ")
    if not ori.isdigit() or ori == "0":
        print("No es un número válido, abortando...")
        return lines, conf
    ori = int(ori) - 1
    if not ori < len(conf["accounts"]):
        print("Cuenta no existente, abortando...")
        return lines, conf
    if ori == dest:
        print("No se puede combinar una cuenta consigo misma. Inténtalo de nuevo")
        return lines, conf
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines = configAccounts(accs, lines, oldacc=ori+1, newacc=dest+1) # La función no acepta índices, sino números de cuenta
    accs = parseAccounts(lines[-1]) # Actualizar cuentas y trabajar con una menos tras la combinación
    conf["accounts"] = conf["accounts"][:ori] + conf["accounts"][ori+1:] # Eliminar configuración de cuenta borrada
    lines.insert(dotind, "{0}->{1} => Cuentas combinadas (resultado en cuenta número {2}).\n".format(ori+1, dest+1, dest+1))
    lines = checkLimitAccount(conf, accs, week, lines)
    print(f"Cuentas combinadas con éxito. Saldo de la cuenta resultante: {accs[dest-1]}")
    return lines, conf

# Borrar cuenta únicamente si no tiene (tener en cuenta las cuentas de reserva configuradas)
def deleteAccount(conf, accs, week, lines):
    accind = input(f"""Sólo se puede borrar una cuenta si su saldo es de cero (0€).
Si se quiere borrar una cuenta con saldo ó deuda, usar la opción "Combinar cuentas",
indicando la cuenta donde recibir el saldo ó deuda como primera y la cuenta a borrar como segunda.
¿Qué cuenta quieres borrar? (Indica con un número del 1 al {len(accs)}) """)
    if not accind.isdigit() or accind == "0":
        print("No es un número válido, abortando...")
        return lines, conf
    ind = int(accind) - 1
    if not ind < len(conf["accounts"]):
        print("Cuenta no existente, abortando...")
        return lines, conf
    if accs[ind] != 0:
        print(f"El saldo de la cuenta {accind} no es cero. Por favor, usa la opción \"Combinar cuentas\" para borrarla.")
        return lines, conf
    weekind = lines.index(f"Semana {week}\n")
    dotind = lines[weekind:].index(".\n") + weekind
    lines = configAccounts(accs, lines, oldacc=int(accind))
    print(f"Cuenta número {accind} ({conf['accounts'][ind]['Nombre']}) borrada con éxito.")
    conf["accounts"] = conf["accounts"][:ind] + conf["accounts"][ind+1:] # Eliminar configuración de cuenta borrada
    lines.insert(dotind, "{0} => Cuenta sin saldo borrada.\n".format(accind))
    return lines, conf

def showAccounts(conf):
    accind = input("¿Qué cuentas quieres comprobar? (Indica con números separados por un espacio) ").strip().split(" ")
    inds = [int(i)-1 for i in accind]
    for i, c in enumerate(conf["accounts"]):
        if i in inds:
            print(f"""Cuenta número {i+1}:
    - Nombre: {c["Nombre"]}
    - Descripción: {c["Descripción"]}
    - Cuenta de reserva: {c["Cuenta reserva"] if c["Cuenta reserva"] != 0 else "Ninguna"}
    - Límite de saldo mínimo: {"{0:.2f}".format(c["Mínimo"]) if c["Mínimo"] is not None else "Ninguno"}
    - Límite de saldo máximo: {"{0:.2f}".format(c["Máximo"]) if c["Máximo"] is not None else "Ninguno"}
    - Último saldo guardado: {"{0:.2f}".format(c["Saldo"])}
    - Fecha de creación: {c["Creada el"]}
    - Fecha de última modificación: {c["Modificada el"]}
            """)
    return

# Guardar en configuración 
def updateConfigFile(rfol, user, conf, accs, verbose=False):
    conffile = os.path.join(rfol, user) + '.tpah'
    for i, acc in enumerate(accs): conf["accounts"][i]["Saldo"] = accs[i]
    with open(conffile, 'w', encoding='utf-8') as f:
        json.dump(conf, f, indent=4, ensure_ascii=False)
    if verbose: print(f"Configuración actualizada.")
    return conf

# Menú de ayuda para mostrar el uso de la aplicación
def helpCommandInterface():
    print("¡Todavía por implementar! Si necesitas ayuda, abre un caso en https://github.com/NotTrower/private-home-tools/issues")
    return

# Hay que pasar "lines" porque se van a utilizar a medida que se configuran las cuentas
def configCommandInterface(rfol, user, week, accs, lines):
    with open(os.path.join(rfol, user) + '.tpah', 'r', encoding='utf-8') as f:
        conf = json.load(f)
    prevconf = conf.copy()
    prevlines = lines[:]
    res = True
    while lines and res != '9':
        printCurrentAccounts(accs)
        printConfig()
        res = input()
        if res == '1':
            lines, conf = createAccount(conf, accs, week, lines)
        elif res == '2':
            lines, conf = modifyAccount(conf, accs, week, lines)
        elif res == '3':
            lines, conf = mergeAccounts(conf, accs, week, lines)
        elif res == '4':
            lines, conf = deleteAccount(conf, accs, week, lines)
        elif res == '5':
            showAccounts(conf)
        elif res == '6':
            conf = updateConfigFile(rfol, user, conf, accs, verbose=True)
        elif res == '7':
            helpCommandInterface()
        # Mantener configuración anterior
        elif res == '91':
            print("Cambios en la configuración revertidos.")
            return prevlines, prevconf
        else:
            res = '9'
        accs = parseAccounts(lines[-1]) # La última línea siempre serán las cuentas actualizadas
    conf = updateConfigFile(rfol, user, conf, accs, verbose=True)
    return lines, conf

def checkCorrectConfig(conf, accs):
    keys = ["Nombre", "Saldo", "Descripción", "Creada el", "Modificada el", "Mínimo", "Máximo", "Cuenta reserva"]
    if len(conf["accounts"]) != len(accs):
        print("Error 1. Número de cuentas en configuración incongruente con el último fichero de transacciones. Contacte con el administrador.")
        return 1
    elif any([not all([ k in keys for k in c.keys() ]) for c in conf["accounts"]]):
        print("Error 2. Falta información en la configuración de alguna cuenta. Contacte con el administrador.")
        return 2
    return 0

def initAccountFile(rfol, name, accs):
    with open(os.path.join(rfol, name), 'w', encoding='utf-8') as f:
        for i, money in enumerate(accs):
            f.write("{0}: {1:.2f}€ ".format(i+1, money)) #Deja un espacio al final
        f.write('\n')

# La configuración será un array de objetos JSON con una cuenta por objeto
def initConfigFile(rfol, name, accs):
    conffile = os.path.join(rfol, name) + '.tpah'
    conf = { "accounts": [] }
    for i, acc in enumerate(accs): conf["accounts"].append(createAccount(conf, accs, 0, lines=None))
    with open(conffile, 'w', encoding='utf-8') as f:
        json.dump(conf, f, indent=4, ensure_ascii=False)
    print(f"Usuario {name} configurado con éxito.")
    return

def userCommandInterface(rfol, currentfile, user, week, history):
    file = os.path.join(rfol, currentfile)
    conffile = os.path.join(rfol, user) + '.tpah'
    if not os.path.isfile(file):
        with open(os.path.join(rfol, history[-1]), 'r', encoding='utf-8') as prevf:
            accounts = parseAccounts(prevf.readlines()[-1])
        initAccountFile(rfol, currentfile, accounts)
    if not os.path.isfile(conffile):
        print(f"Fichero de configuración '{conffile}' no encontrado. Creando configuración por defecto...", end=" ")
        initConfigFile(rfol, user, accounts)
        print(f"hecho.")
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    accounts = parseAccounts(lines[-1]) # La última línea siempre serán las cuentas actualizadas
    checkWeeksInFile(file, lines, week)
    with open(conffile, 'r',  encoding='utf-8') as f:
        conf = json.load(f)
    chk = checkCorrectConfig(conf, accounts) # Comprobar que hay el mismo número de cuentas entre la configuración y el fichero actual de operaciones
    if chk != 0: return chk*10
    conf = updateConfigFile(rfol, user, conf, accounts)
    res = True
    while lines and res != '9':
        printCurrentAccounts(accounts)
        printOptions()
        res = input()
        if res == '1':
            lines = addToAccounts(accounts, lines, week)
            lines = checkLimitAccount(conf, accounts, week, lines)
        elif res == '2':
            lines = withdrawFromAccounts(accounts, lines, week)
            lines = checkLimitAccount(conf, accounts, week, lines)
        elif res == '3':
            lines = transferToAccount(accounts, lines, week)
            lines = checkLimitAccount(conf, accounts, week, lines)
        elif res == '4':
            lines = showWeek(lines, week)
        elif res == '5':
            lines = showMonth(rfol, currentfile, lines) #Mejorar para que aproveche la variable "history"
        elif res == '6':
            lines = showYear(rfol, currentfile, lines)
        elif res == '7':
            accind = input("¿Qué cuentas sumar? (Indica con números separados por un espacio ó 0 para sumar todas las cuentas) ").strip().split(" ")
            accind = [int(i) for i in accind]
            if not accind[0]:
                print(f"La suma de todas las cuentas es {round(sum(accounts), 2)}€")
            elif any([(i < 1 or i > len(accounts)) for i in accind]):
                print(f"Alguna cuenta indicada no existe. Por favor, indicar números del 1 al {len(accounts)}.")
            else:
                total = 0
                for i in accind: total += accounts[i-1]
                print(f"La suma de las cuentas {', '.join([str(i) for i in accind])} es {round(total, 2)}€")
        elif res == '0':
            lines, conf = configCommandInterface(rfol, user, week, accounts, lines)
            accounts = parseAccounts(lines[-1]) # La última línea siempre serán las cuentas actualizadas
        else:
            res = '9'
        if lines:
            with open(file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        elif not lines:
            return 2
    conf = updateConfigFile(rfol, user, conf, accounts, verbose=True)
    return 0

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
        initConfigFile(rfol, user, accounts)
    else:
        print(f"Encontrado fichero/s de cuenta para usuario {user}.")
    if currentdatestr not in files:
        print(f"Creado nuevo fichero de cuenta {currentdatestr}.")
    try:
        rescode = userCommandInterface(rfol, currentdatestr, user, week, files) # Mejora: hacer una interfaz gráfica
    except Exception as e:
        print("Ha ocurrido un error. Contacte con el desarrollador del código en: https://github.com/NotTrower")
        print(e)
        sleep(4)
        rescode = 1
    if rescode not in [0, 1, 2]: print("Administrador: https://github.com/NotTrower")
    sleep(2)
    exit(rescode)

if __name__ == '__main__':
    main(argInit())