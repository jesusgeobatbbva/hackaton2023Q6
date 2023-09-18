
import sqlite3
from datetime import datetime
# Conectar a la base de datos
conn = sqlite3.connect('BBVA.db')

#La conexion de la base de datos se almacena en 'conn'
cursor = conn.cursor()

#Se define una función llamada consultar_saldo que recibe un numero_cuenta como argumento. 
#Dentro de la función, se ejecuta una consulta SQL que busca el saldo de una cuenta en la tabla CuentasBancarias 
#basándose en el número de cuenta proporcionado. Luego, se recupera el saldo de la cuenta utilizando 
#cursor.fetchone(). Si se encuentra un saldo, se devuelve; de lo contrario, se devuelve None.
id_cliente = 'ID'
saldo_cliente = 'Saldo'
nombre_cliente ='NombreCliente'


    
def consultar_saldo(numero_cuenta):
    cursor.execute('SELECT '+ saldo_cliente +' FROM Cuentas WHERE '+id_cliente+' = ?', (numero_cuenta,))
   #cursor.fetchone() es un método utilizado en Python para recuperar la siguiente fila (registro) de un conjunto de resultados obtenido después de ejecutar una consulta SQL en una base de datos utilizando un cursor. El nombre del método "fetchone" se utiliza porque su función principal es recuperar una sola fila de los resultados cada vez que se llama.
    saldo = cursor.fetchone()
    if saldo:
        return saldo[0]
    else:
        return None

#Se define la funcion que nos va a ayudar a realizar el deposito, y tiene numero_cuenta y monto como argumentos
def hacer_deposito(numero_cuenta, monto):
    #Si el monto es menor a cero
    if monto <= 0:
        return "El monto del depósito debe ser mayor que cero."
    #y consulta el saldo actual 
    saldo_actual = consultar_saldo(numero_cuenta)
    #verificar si existe un saldo actual 
    if saldo_actual is not None:
        nuevo_saldo = saldo_actual + monto
        #actualizamos la tabla 
        cursor.execute('UPDATE Cuentas SET '+saldo_cliente+' = ? WHERE '+id_cliente+' = ?', (nuevo_saldo, numero_cuenta))
        
        # Registrar la transacción
        cursor.execute('INSERT INTO Transacciones ('+id_cliente,+'CuentaID, Tipo_Transaccion, Monto_transaccion, FechaHora_transaccion, Descripcion_transaccion) VALUES (?, ?, ?, ?, ?)',
                       (numero_cuenta, 'Depósito', monto, datetime.now(), 'Depósito realizado'))
        conn.commit()

        return f"Depósito exitoso. Nuevo saldo: {nuevo_saldo}"
    else:
        return "La cuenta especificada no existe."

#Definimos la funcion que hace el retiro y le damos los argumentos numero_cuenta y monto 
def hacer_retiro(numero_cuenta, monto):
    if monto <= 0:
        return "El monto del retiro debe ser mayor que cero."
    #Muestra el saldo 
    saldo_actual = consultar_saldo(numero_cuenta)
    #Si el saldo existe 
    if saldo_actual is not None:
        #Si el monto es menor o igual a saldo actual 
        if monto <= saldo_actual:
            #Se crea un nuevo saldo que será el saldo actual menor el monto a retirar
            nuevo_saldo = saldo_actual - monto
            #actualizamos la tabla
            cursor.execute('UPDATE CuentasBancarias SET Saldo_cuenta = ? WHERE Numero_Cuenta = ?', (nuevo_saldo, numero_cuenta))
            
            # Registrar la transacción
            cursor.execute('INSERT INTO Transacciones (CuentaID, Tipo_Transaccion, Monto_transaccion, FechaHora_transaccion, Descripcion_transaccion) VALUES (?, ?, ?, ?, ?)',
                           (numero_cuenta, 'Retiro', monto, datetime.now(), 'Retiro realizado'))
            #se guardan las actualizaciones
            conn.commit()
            return f"Retiro exitoso. Nuevo saldo: {nuevo_saldo}"
        else:
            return "Fondos insuficientes para realizar el retiro."
    else:
        return "La cuenta especificada no existe."
#Definimos la función transferencia con los argumentos que creamos como cuenta_origen, cuenta_destino y monto
def hacer_transferencia(cuenta_origen, cuenta_destino, monto):
    #Si la cuenta de origen es igual a la cuenta destino 
    if cuenta_origen == cuenta_destino:
        return "No se puede transferir a la misma cuenta."
    #En resumen, esta parte del código se asegura de que el monto de la transferencia sea válido (mayor que cero) y verifica que las cuentas de origen y destino existan en la base de datos y tengan fondos suficientes antes de proceder con la transferencia. Si alguna de estas condiciones no se cumple, se devuelve un mensaje de error correspondiente.
    if monto <= 0:
        return "El monto de la transferencia debe ser mayor que cero."
    
    saldo_origen = consultar_saldo(cuenta_origen)
    saldo_destino = consultar_saldo(cuenta_destino)

    #Verificar que ambas cuentas de origen y destino existan en la base de datos y tengan saldos disponibles 
    if saldo_origen is not None and saldo_destino is not None:
        #Si el monto es mayor o igual que el saldo origen y verifica que la cuenta de origen tenga suficientes fondos para realizar la transferencia
        if monto <= saldo_origen:

            #Estas líneas calculan los nuevos saldos de la cuenta de origen (nuevo_saldo_origen) y la cuenta de destino (nuevo_saldo_destino) después de realizar la transferencia. Se resta el monto de la cuenta de origen y se suma a la cuenta de destino.
            nuevo_saldo_origen = saldo_origen - monto
            nuevo_saldo_destino = saldo_destino + monto
            #Estas líneas ejecutan dos sentencias SQL para actualizar los saldos en la base de datos. La primera línea actualiza el saldo de la cuenta de origen y la segunda línea actualiza el saldo de la cuenta de destino.
            cursor.execute('UPDATE CuentasBancarias SET Saldo_cuenta = ? WHERE Numero_Cuenta = ?', (nuevo_saldo_origen, cuenta_origen))
            cursor.execute('UPDATE CuentasBancarias SET Saldo_cuenta = ? WHERE Numero_Cuenta = ?', (nuevo_saldo_destino, cuenta_destino))
            
            #Estas líneas registran dos transacciones en la tabla "Transacciones". La primera línea registra la transacción de salida desde la cuenta de origen y la segunda línea registra la transacción de entrada en la cuenta de destino. Ambas transacciones incluyen detalles como el tipo de transacción, el monto, la fecha y hora, y una descripción.
            # Registrar las transacciones
            cursor.execute('INSERT INTO Transacciones (CuentaID, Tipo_Transaccion, Monto_transaccion, FechaHora_transaccion, Descripcion_transaccion) VALUES (?, ?, ?, ?, ?)',
                           (cuenta_origen, 'Transferencia Saliente', monto, datetime.now(), 'Transferencia realizada a ' + cuenta_destino))
            
            cursor.execute('INSERT INTO Transacciones (CuentaID, Tipo_Transaccion, Monto_transaccion, FechaHora_transaccion, Descripcion_transaccion) VALUES (?, ?, ?, ?, ?)',
                           (cuenta_destino, 'Transferencia Entrante', monto, datetime.now(), 'Transferencia recibida de ' + cuenta_origen))
            #guarda los datatos en la base de datos
            conn.commit()
            return f"Transferencia exitosa. Nuevo saldo en cuenta de origen: {nuevo_saldo_origen}"
        else:
            return "Fondos insuficientes para realizar la transferencia."
    else:
        return "Una o ambas cuentas especificadas no existen."
#Definimos la función de historial de transacciones 
def historial_transacciones(numero_cuenta):
    #Se ejecuta la consulta en la base de datos 
    cursor.execute('SELECT Tipo_Transaccion, Monto_transaccion, FechaHora_transaccion, Descripcion_transaccion FROM Transacciones WHERE CuentaID = ? ORDER BY FechaHora_transaccion ASC',
                   (numero_cuenta,))
    #las guardamos aqui
    transacciones = cursor.fetchall()
    return transacciones

def mostrar_menu():

  
 
    while True:
            


        print("\n--- Menú de Operaciones ---")

        print("1. Consultar Saldo")
        print("2. Hacer Depósito")
        print("3. Hacer Retiro")
        print("4. Hacer Transferencia")
        print("5. Ver Historial de Transacciones")
        print("6. Salir")
        
        opcion = input("Seleccione una opción: ")

      
        
        
        if opcion == '1':
            numero_cuenta = input("Ingrese el número de cuenta: ")
            saldo = consultar_saldo(numero_cuenta)
            if saldo is not None:
                print(f"Saldo actual de la cuenta {numero_cuenta}: {saldo}")
            else:
                print("La cuenta especificada no existe.")
        
        elif opcion == '2':
            numero_cuenta = input("Ingrese el número de cuenta: ")
            monto = float(input("Ingrese el monto a depositar: "))
            resultado = hacer_deposito(numero_cuenta, monto)
            print(resultado)
        
        elif opcion == '3':
            numero_cuenta = input("Ingrese el número de cuenta: ")
            monto = float(input("Ingrese el monto a retirar: "))
            resultado = hacer_retiro(numero_cuenta, monto)
            print(resultado)
        
        elif opcion == '4':
            cuenta_origen = input("Ingrese el número de cuenta de origen: ")
            cuenta_destino = input("Ingrese el número de cuenta de destino: ")
            monto = float(input("Ingrese el monto a transferir: "))
            resultado = hacer_transferencia(cuenta_origen, cuenta_destino, monto)
            print(resultado)
        
        elif opcion == '5':
            numero_cuenta = input("Ingrese el número de cuenta: ")
            transacciones = historial_transacciones(numero_cuenta)
            if transacciones:
                print("\n--- Historial de Transacciones ---")
                for transaccion in transacciones:
                    tipo, monto, fecha_hora, descripcion = transaccion
                    print(f"Tipo: {tipo}, Monto: {monto}, Fecha y Hora: {fecha_hora}, Descripción: {descripcion}")
            else:
                print("No se encontraron transacciones para la cuenta especificada.")
        
        elif opcion == '6':
            break
        
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    mostrar_menu()
