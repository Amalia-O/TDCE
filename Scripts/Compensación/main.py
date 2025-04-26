import sys
import numpy as np
import pandas as pd

RC = 220
RD1 = 1*10**3
RD2 = 1*10**3
RP1 = 1*10**3
RP2 = 1.8*10**3
RS = 2.2

CL = 1*10**(-6)

Vth = 25.9*10**(-3)

BETA = "beta"
GM = "gm"
RPI = "Rpi"
RO = "Ro"
CMU = "Cmu"
CPI = "Cpi"

TIPO_NPN = "N"
TIPO_PNP = "P"

class TransistorPNP:
    def __init__(self, nombre, beta, fTMh, va, cmupF):
        self.nombre = nombre
        self.beta = beta
        self.fT = fTMh * 10**6
        self.va = va
        self.cmu = cmupF * 10**(-12)

    def parametros(self, Ic):
        gm = -Ic / Vth
        return {
            BETA: self.beta,
            GM: gm,
            RPI: self.beta / gm,
            RO: -self.va / Ic,
            CMU: self.cmu,
            CPI: gm / (2 * np.pi * self.fT ),
        }
    
    def __str__(self):
        fTMHz = self.fT * 10**(-6)
        cmu = self.cmu * 10**12

        return f"{self.nombre}-PNP: [b:{self.beta} VA:{self.va:.2f} fTMhz:{fTMHz:.2f} CmupF:{cmu:.2f}]"

class TransistorNPN:
    def __init__(self, nombre, beta, fTMh, va, cmupF):
        self.nombre = nombre
        self.beta = beta
        self.fT = fTMh * 10**6
        self.va = va
        self.cmu = cmupF * 10**(-12)

    def parametros(self, Ic):
        gm = Ic / Vth
        return {
            BETA: self.beta,
            GM: gm,
            RPI: self.beta / gm,
            RO: self.va / Ic,
            CMU: self.cmu,
            CPI: gm / (2 * np.pi * self.fT ),
        }
    
    def __str__(self):
        fTMHz = self.fT * 10**(-6)
        cmu = self.cmu * 10**12

        return f"{self.nombre}-NPN: [b:{self.beta} VA:{self.va:.2f} fTMhz:{fTMHz:.2f} CmupF:{cmu:.2f}]"

def paral(R1, R2):
    return 1 / ( (1 / R1) + (1 / R2) )

def calculoDeNodos(RL, pQ1, pQ2, pQ3, pQ4, pQ5, pQ6):
    # Resistencias importante
    roeq = pQ5[RO] 
    rpieq = pQ6[RPI] + (pQ6[BETA] + 1) * pQ5[RPI]
    gmeq = pQ5[GM] * (1 + pQ6[BETA])
    beq = pQ5[BETA] * (1 + pQ6[BETA])

    Rprima = RS + paral(RP1 + RP2, paral(roeq, (1 / gmeq) + (pQ2[RO] / beq)))
    Reeq = paral(RP1 + RP2, RS + paral(RL, RD1 + paral(RD2, pQ2[RPI])))

    # Ganancia
    Avcb2 = -pQ2[GM] * paral(pQ2[RO], rpieq + (Reeq * beq * roeq) / (Reeq + roeq))
    Avcb6 = -pQ6[GM] * pQ5[RPI] / (1 + pQ6[GM] * paral(pQ5[RO], Reeq))
    Aveb6 = pQ6[GM] * paral(pQ5[RO], Reeq) / (1 + pQ6[GM] * paral(pQ5[RO], Reeq))

    Avcb4 = -pQ4[GM] * paral(pQ2[RO], rpieq + (Reeq * beq * roeq) / (Reeq + roeq)) / 1 + (pQ4[GM] * RC)
    Aveb4 = pQ4[GM] * RC / (1 + pQ4[GM] * RC)
    Aveb3 = ( pQ3[BETA] * pQ1[RO] ) / ( paral(pQ3[RPI], pQ3[RO]) + pQ3[BETA] * pQ1[RO] )

    # Calculo de nodos en si
    datosN1 = {
        "nodo": "Nodo 1", 
        "R": paral(pQ2[RPI], paral(RD2, RD1 + paral(RL, Rprima))),
        "C": pQ2[CPI] + pQ2[CMU] * (1 - Avcb2),
    }

    datosN2 = {
        "nodo": "Nodo 2", 
        "R": paral(pQ2[RO], rpieq + (Reeq * beq * roeq) / (Reeq + roeq)),
        "C": pQ2[CMU] + pQ4[CMU] + pQ6[CMU] * (1 - Avcb6) + pQ6[CPI] * (1 - Aveb6),
    }

    datosN3 = {
        "nodo": "Nodo 3", 
        "R": paral(pQ5[RPI], pQ6[RO] + paral(pQ6[RPI], paral(pQ5[RO], Reeq)) * (pQ6[GM] * pQ6[RO] + 1)),
        "C": pQ5[CPI] + pQ6[CMU] + pQ5[CMU] * (1 - Avcb6),
    }

    datosN4 = {
        "nodo": "Nodo 4",
        "R": paral(pQ4[RPI] + RC, RC + (1 / pQ3[GM])),
        "C": pQ3[CPI] * (1 - Aveb3) + pQ4[CPI] * (1 - Aveb4) + pQ4[CMU] * (1 - Avcb4),
    }

    datosSalida = {
        "nodo": "Nodo 5",
        "R": paral(RL, paral(Rprima, RD1 + paral(RD2, pQ2[RPI]))),
        "C": CL,
    }

    return datosN1, datosN2, datosN3, datosN4, datosSalida

def generarTransistor(nombre, tipo, dispBeta, dispFTMh, va, dispCmuPF):
    transistores = []

    for beta in dispBeta:
        for fTMh in dispFTMh:
            for cmuPF in dispCmuPF:
                if tipo == TIPO_NPN:
                    transistores.append(TransistorNPN(nombre, beta, fTMh, va, cmuPF))
                elif tipo == TIPO_PNP:
                    transistores.append(TransistorPNP(nombre, beta, fTMh, va, cmuPF))

    return transistores

class GenerarConfiguracion:
    def __init__(self, grupoDeTransistores):
        self.grupoDeTransistores = grupoDeTransistores

    def __iter__(self):
        self.contadores = []
        for _ in self.grupoDeTransistores:
            self.contadores.append(0)

        self.salir = len(self.contadores) == 0

        return self

    def __next__(self):
        if self.salir:
            raise StopIteration

        configuracion = []
        for posibleTransistor, contador in zip(self.grupoDeTransistores, self.contadores):
            configuracion.append(posibleTransistor[contador])
        configuracion = tuple(configuracion)

        for i in range(len(self.contadores) - 1):
            self.contadores[i] += 1
            if self.contadores[i] < len(self.grupoDeTransistores[i]):
                return configuracion
            self.contadores[i] = 0

        self.contadores[-1] += 1
        if self.contadores[-1] >= len(self.grupoDeTransistores[-1]):
            self.salir = True

        return configuracion

def main(argumentos):
    if len(argumentos) < 2:
        return

    archivoPath = argumentos[1]
    corrientes = np.genfromtxt(archivoPath, dtype = np.float64, delimiter = "\t", skip_header = 1)

    Q1s, Q2s, Q3s, Q4s, Q5s, Q6s = [
        [ 
            generarTransistor("Q1", TIPO_NPN, [420, 458.7, 800], [300, 339],   52.64, [3.5, 6]),
            generarTransistor("Q2", TIPO_NPN, [420, 458.7, 800], [300, 339],   52.64, [3.5, 6]),
            generarTransistor("Q3", TIPO_PNP, [200, 344.4, 450], [150, 284],   21.11, [6]     ),
            generarTransistor("Q4", TIPO_PNP, [200, 344.4, 450], [150, 284],   21.11, [6]     ),
            generarTransistor("Q5", TIPO_PNP, [55, 70, 160],     [10, 82.8],   100,   [280]   ),
            generarTransistor("Q6", TIPO_NPN, [200, 294.3, 450], [300, 362.5], 63.2,  [3.5, 6]),
        ],
        [ # Modelo tipico
            generarTransistor("Q1", TIPO_NPN, [458.7], [339],   52.64, [3.5]),
            generarTransistor("Q2", TIPO_NPN, [458.7], [339],   52.64, [3.5]),
            generarTransistor("Q3", TIPO_PNP, [344.4], [284],   21.11, [6]     ),
            generarTransistor("Q4", TIPO_PNP, [344.4], [284],   21.11, [6]     ),
            generarTransistor("Q5", TIPO_PNP, [70],     [82.8],   100,   [280]   ),
            generarTransistor("Q6", TIPO_NPN, [294.3], [362.5], 63.2,  [3.5]),
        ],
    ][1]
        
    resultado = {}
    for datos in corrientes:
        RL = datos[0]
        resultado[RL] = {
            "configuracion": "Nada",
            "frecuencias": "Nadie",
            "fTotal": 10**100,
        }

    generador = GenerarConfiguracion([Q1s, Q2s, Q3s, Q4s, Q5s, Q6s])
    contador = 0
    for Q1, Q2, Q3, Q4, Q5, Q6 in iter(generador):
        contador += 1

        for RL, IC1, IC2, IC3, IC4, IC5, IC6 in corrientes:
            listaTransistores = [(Q1, IC1), (Q2, IC2), (Q3, IC3), (Q4, IC4), (Q5, IC5), (Q6, IC6)]

            datos = calculoDeNodos(
                RL, *map(lambda dato: dato[0].parametros(dato[1]), listaTransistores)
            )

            f = 1 / (2 * np.pi * sum(map(lambda dato: dato["R"] * dato["C"], datos)))

            if resultado[RL]["fTotal"] > f:
                resultado[RL] = {
                    "configuracion": f"{Q2}; {Q3}; {Q4}; {Q6}; {Q5}]",
                    "frecuencias": list(map(lambda dato: 1 / (2 * np.pi * dato["R"] * dato["C"]), datos)),
                    "fTotal": f,
                }

    tabla = []
    for RL in resultado:
        valores = resultado[RL]
        tabla.append([RL, valores["fTotal"], *valores["frecuencias"]])

    tabla = pd.DataFrame(tabla, columns = ["RL", "Frecuencia total", "Frecuencia Nodo 1", "Frecuencia Nodo 2", "Frecuencia Nodo 3", "Frecuencia Nodo 4", "Frecuencia Nodo Salida"]) 
    tabla.to_csv(argumentos[2])

if __name__ == "__main__":
    main(sys.argv)
