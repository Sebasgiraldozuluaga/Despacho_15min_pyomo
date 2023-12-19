
# Modelo de despacho de energía eléctrica en períodos  de 15 minutos- PYOMO-OPTIMIZATION


El objetivo principal del despacho de 
energía eléctrica es determinar la operación de un 
sistema eléctrico mediante la asignación óptima de la 
demanda total del sistema entre las diferentes 
unidades de generación. Este despacho de energía 
eléctrica se podrá realizar en diferentes periodos de 
tiempo según el marco regulatorio del país y los 
requerimientos energéticos del mismo. Para este caso 
en particular, se desarrolló un modelo de despacho con 
su respectiva formulación matemática, función 
objetivo y restricciones que permitan el despacho de 
energía eléctrica de una unidad de generación en un 
periodo de tiempo equivalente a 15 minutos.




## OBJETIVOS

### Objetivo General
Elaborar un modelo matemático de despacho de energía 
eléctrica para una unidad de generación en periodos de 
tiempo de 15 minutos.
### Objetivo Específico
Evaluar sobre condiciones y parámetros reales, la 
viabilidad teórica de la modificación del despacho a 
periodos de tiempo de 15 minutos.

Ampliar de 24 a 96 los períodos de demanda y verificar 
que en el despacho esta se satisface en todo periodo de 
tiempo.

Verificar el impacto que tiene la modificación que 
tienen los parámetros UR y DR en las centrales térmicas, 
si la regulación se modifica a periodos de 15 minutos.
## PLANTEAMIENTO MATEMÁTICO

$$\min \sum_{j=1}^{t=1} \sum_{j=1}^{t=1} P_{1jt} \cdot g_{1jt} + \sum_{j=1}^{t=1} \sum_{j=1}^{t=1} PAP_{1jt} \cdot a_{1jt} + \sum_{i=t} CR_{it}$$

Con las siguientes restricciones:

$$g_{1jt} - max_{1jt} \cdot u_{1jt} \leq 0 \forall i, \forall t$$

$$g_{1jt} - min_{1jt} \cdot u_{1jt} \geq 0 \forall i, \forall t$$

$$\sum_{j=1}^{t} g_{1jt} + r_i = Demanda \forall t$$

$$a_{1it} - p_{i2t} \geq u_{it} - u_{i(t-1)} \forall i, t$$

$$a_{2it} + p_{2it} \leq 1 \forall i, t$$


## CONCLUSIONES 

Encontrar los nuevos parámetros de UR y DR, para el 
redespacho de recursos energéticos en periodos de 15min, 
ayuda a la optimización de recursos a un menor precio.
 Plantear un despacho para un mayor número de 
periodos viabiliza la buena optimización de recursos 
energéticos a un menor costo y un redespacho más 
pertinente para centrales de generación donde su recurso 
para la generación de energía es variable como lo es en 
centrales eólicas y fotovoltaicas donde el suministro de 
viento o radiación puede ser variable en varias ocasiones 
en diferentes momentos en una hora.
 Implementar más periodos de tiempo optimiza el costo 
de generación para toda la demanda energética del país.