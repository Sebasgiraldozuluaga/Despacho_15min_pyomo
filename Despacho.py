from pyomo.environ import *
import pandas as pd
from openpyxl import load_workbook
from os import getcwd
import xlwings as xw
from pandasql import sqldf

#Definir objeto con archivo de excel
xlFile = getcwd() + r"\despacho.xlsx"            

# # Definir objeto con información de excel
xl_datos = pd.ExcelFile(xlFile)

#Definir modelo de optimizacion
modelo = ConcreteModel("despacho")

#LECTURA DE DATOS;
df_DEMANDA = xl_datos.parse('DEMANDA_15MIN').set_index(['periodo']) 
df_GENERADORES = xl_datos.parse('GENERADORES').set_index(['nombre','periodo']) 
iGenerador  = sqldf("SELECT distinct(nombre) FROM df_GENERADORES;", locals())
df_RAMPAS = xl_datos.parse('RAMPAS').set_index(['recurso'])
CR = 2000000 

ESTADOINICIAL={}
GENERADORINICIAL={}

#Indices del modelo
modelo.GENERADOR = Set(initialize=iGenerador.nombre)
modelo.PERIODO = Set(initialize=df_DEMANDA.index)
modelo.RAMPAS = Set(initialize=df_RAMPAS.index)

for i in modelo.RAMPAS:
    ESTADOINICIAL[i]=0
    GENERADORINICIAL[i]=0

#Definir variables de decision
modelo.despacho = Var( modelo.GENERADOR, modelo.PERIODO,domain=PositiveReals )
modelo.binaria = Var( modelo.GENERADOR, modelo.PERIODO, domain=Binary )
modelo.arranque = Var( modelo.RAMPAS, modelo.PERIODO, domain=Binary )
modelo.parada = Var( modelo.RAMPAS, modelo.PERIODO, domain=Binary )
modelo.racionamiento = Var (modelo.PERIODO, domain=PositiveReals )

#Definir funcion objetivo
def obj_rule(modelo):
    expr1 = sum ( df_GENERADORES.precio[i,t] * modelo.despacho[i,t]
                for i in modelo.GENERADOR
                 for t in modelo.PERIODO
                )

    expr2 = sum ( df_RAMPAS.costoarranque[i] * modelo.arranque[i,t]
                for i in modelo.RAMPAS
                for t in modelo.PERIODO
                )
    
    expr3 = sum ( CR * modelo.racionamiento[t]
                for i in modelo.GENERADOR
                for t in modelo.PERIODO
                )
    expr = expr1 + expr2 + expr3
    return expr 

modelo.FO = Objective(rule=obj_rule, sense=minimize)

#Definir restricciones
#restriccion Balance demanda
def r1_rule(modelo,t):
    ecuacion1 = sum(modelo.despacho[i,t]+modelo.racionamiento[t]
                    for i in modelo.GENERADOR
    )
    return ecuacion1 >= df_DEMANDA.demanda[t]

modelo.r1 = Constraint(modelo.PERIODO,rule=r1_rule)

#restriccion Maximo
def r2_rule(modelo,i,t):
    ecuacion2 = modelo.despacho[i,t] - df_GENERADORES.maximo[i,t]*modelo.binaria[i,t]
    return ecuacion2 <= 0

modelo.r2 = Constraint(modelo.GENERADOR,modelo.PERIODO,rule=r2_rule)  

#restriccion Mínimo
def r3_rule(modelo,i,t):
    ecuacion3 = modelo.despacho[i,t] - df_GENERADORES.minimo[i,t]*modelo.binaria[i,t]
    return ecuacion3 >= 0

modelo.r3 = Constraint(modelo.GENERADOR,modelo.PERIODO,rule=r3_rule)

#Restriccion 4
def r4_rule(modelo,i,t):
    if t==1:
        ecuacion4 = modelo.arranque[i,t]-modelo.parada[i,t]     
        return ecuacion4 >= modelo.binaria[i,t]-ESTADOINICIAL[i]
    else:
        return modelo.arranque[i,t]-modelo.parada[i,t]>=modelo.binaria[i,t]-modelo.binaria[i,t-1]
modelo.r4 = Constraint(modelo.RAMPAS,modelo.PERIODO,rule=r4_rule)

#Restriccion 5
def r5_rule(modelo,i,t):
    ecuacion = modelo.arranque[i,t]+modelo.parada[i,t]
    return ecuacion <= 1

modelo.r5 = Constraint(modelo.RAMPAS,modelo.PERIODO,rule=r5_rule)

#Restriccion 6 de UR
def r6_rule(modelo,i,t):
    if t==1:
        ecuacion5 = modelo.despacho[i,t] - GENERADORINICIAL[i]
        return ecuacion5 <= df_RAMPAS.ur[i]
    else:
        return modelo.despacho[i,t]-modelo.despacho[i,t-1] <= df_RAMPAS.ur[i]
modelo.r6 = Constraint(modelo.RAMPAS,modelo.PERIODO,rule=r6_rule)

#Restriccion 7 de DR
def r7_rule(modelo,i,t):
    if t==1:
        ecuacion7 = GENERADORINICIAL[i] - modelo.despacho[i,t]
        return ecuacion7 <= df_RAMPAS.dr[i]
    else:
        return modelo.despacho[i,t-1] - modelo.despacho[i,t] <=df_RAMPAS.dr[i]
modelo.r7 = Constraint(modelo.RAMPAS,modelo.PERIODO,rule=r7_rule)

#Restriccion 8 tiempo en linea
def r8_rule(modelo,i,t):
    if t < df_RAMPAS.tml[i]:
        return Constraint.Skip
    ecuacion8 = sum(modelo.arranque[i,k]
                    for k in range(t-df_RAMPAS.tml[i]+1,t)
            
                    
    )
    return ecuacion8 <= modelo.binaria[i,t]
modelo.r8 = Constraint(modelo.RAMPAS,modelo.PERIODO,rule=r8_rule)

#Restriccion 9 tiempo fuera de linea
def r9_rule(modelo,i,t):
    if t < df_RAMPAS.tmfl[i]:
        return Constraint.Skip
    ecuacion9 = sum(modelo.parada[i,k]
                    for k in range(t-df_RAMPAS.tmfl[i]+1,t)                 
    )
    return ecuacion9 <= 1-modelo.binaria[i,t]
modelo.r9 = Constraint(modelo.RAMPAS,modelo.PERIODO,rule=r9_rule)

#Restriccion 10
def r10_rule(modelo,i,t):
    ecuacion = sum(modelo.arranque[i,t]
                for i in modelo.RAMPAS
                for t in modelo.PERIODO
    )
    return ecuacion <=1

modelo.r10 = Constraint(modelo.RAMPAS, modelo.PERIODO,rule=r10_rule)

#Definir Optimizador
opt = SolverFactory('cbc')

#Escribir archivo .lp
modelo.write("archivo.lp",io_options={"symbolic_solver_labels":True})

#Ejecutar el modelo
results = opt.solve(modelo,tee=0,logfile ="archivo.log", keepfiles= 0,symbolic_solver_labels=True)

if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):

    #Imprimir Resultados
    print ()
    print ("funcion objetivo ", value(modelo.FO))

    #Escribir los resultados
    wb = xw.Book(xlFile)
    hoja_out = wb.sheets['despacho']

    columnas = ["GENERADOR"]
    for t in modelo.PERIODO:
        columnas.append(t)

    out_ = pd.DataFrame(columns=columnas)

    fila = 0
    for i in modelo.GENERADOR:
        fila += 1
        salida = []
        salida.append(i)
        for t in modelo.PERIODO:
            salida.append(modelo.despacho[i,t].value) 
        out_.loc[fila] = salida
    
    hoja_out.clear_contents()   
    hoja_out.range('A1').value = out_

elif (results.solver.termination_condition == TerminationCondition.infeasible):
	print()
	print("EL PROBLEMA ES INFACTIBLE")

elif(results.solver.termination_condition == TerminationCondition.unbounded):
	print()
	print("EL PROBLEMA ES INFACTIBLE")
else:
    print("TERMINÓ EJECUCIÓN CON ERRORES")