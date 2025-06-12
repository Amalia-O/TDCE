import argparse
import numpy as np
import pandas as pd

PATH_NUCLEOS = "nucleos.csv"
PATH_AWG = "AWG.csv"

Ku = 0.33
DENSIDAD_COBRE = 1.724 * 10**(-6)
MU_0 = 4 * np.pi * 10**(-7)

CORE_TYPE = "coreType"
GEOMETRIC_CONSTANTE = "geometricConstant"
CROSS_SECTIONAL_AREA = "crossSectional"
BOBBIN_AREA = "bobbinArea"
MLT = "MLT"
MAGNETIC_PATH_LENGTH = "magneticPathLength"

AWG = "AWG"
BARE_AREA = "bareArea"
DIAMETER = "diameter"

def obtenerParametros():
    parser = argparse.ArgumentParser(
        prog="Metodo Erickson",
        description="Forma para la cual se puede definir los parametros del inductor usando el metodo de Erickson",
    )

    parser.add_argument(
        "-l", "--inductor",
        type=float,
        dest="inductancia",
        help="Valor en micro Henry de la inductancia",
        required=True
    )

    parser.add_argument(
        "-bmax", "--campoMagneticoMaximo",
        type=float,
        default=300,
        dest="campoMagneticoMaximo",
        help="Valor del campo magnetico en mili Teslas"
    )

    parser.add_argument(
        "-bsat", "--campoMagneticoSaturacion",
        type=float,
        default=400,
        dest="campoMagneticoSaturacion",
        help="Valor del campo magnetico en el cual satura en mili Teslas"
    )

    parser.add_argument(
        "-idc", "--corrienteDC",
        type=float,
        dest="corrienteDC",
        help="Corriente en Amperes que tiene que circular constantemente",
        required=True
    )

    parser.add_argument(
        "-f", "--frecuencia",
        type=float,
        dest="frecuencia",
        help="Frecuencia en kilo hertzs",
        required=True
    )

    parser.add_argument(
        "-ilmax", "--corrienteInductorMaxima",
        type=float,
        dest="corrienteInductorMaxima",
        help="Corriente máxima en Amperes que pasa por el inductor",
        required=True
    )

    parser.add_argument(
        "-pmax", "--potenciaMaxima",
        type=float,
        dest="potenciaMaximaCobre",
        help="La potencia máxima en Watts que soporta el cobre",
        required=True
    )

    parser.add_argument(
        "-mKg", "--margenKg",
        type=float,
        default=0.0,
        dest="margenKg",
        help="Margen en 1x10^-3 cm^5 extra para la elección del núcleo",
    )

    parser.add_argument(
        "-mAw", "--margenAw",
        type=float,
        default=0.0,
        dest="margenAw",
        help="Margen en 1x10^-3 cm^2 extra para la elección de AWG",
    )

    parser.add_argument(
        "-mRcu", "--margenRcu",
        type=float,
        default=0.0,
        dest="margenRcu",
        help="Margen en Ohm's extra para la validación de la resistencia del bobinado",
    )

    parser.add_argument(
        "-mSIL", "--margenDensidadCorriente",
        type=float,
        default=0.0,
        dest="margenDensidadCorriente",
        help="Margen en Amperes/mm^2 extra para la validación de la densidad de corriente en el cobre",
    )

    return parser.parse_args()

VERI_CONSTANTE_GEOMETRICA = 1
VERI_SECCION_ALAMBRE = 2
VERI_RESISTENCIA_COBRE = 3
VERI_DENSIDAD_COBRE = 4
VERI_CAMPO_MAG = 8

def main(param):
    print("Metodo de Erickson")
    print("Tomando los valores de:")
    print(f"\tL = {param.inductancia} uHy\n\tIdc = {param.corrienteDC} A\n\tILmax = {param.corrienteInductorMaxima} A")
    print(f"\tBmax = {param.campoMagneticoMaximo} mT\n\tf = {param.frecuencia} KHz\n\tPcu max = {param.potenciaMaximaCobre} W\n")


    # Datos de los csv
    dataNucleos = pd.read_csv(PATH_NUCLEOS, header = 0, names=[CORE_TYPE, GEOMETRIC_CONSTANTE, CROSS_SECTIONAL_AREA, BOBBIN_AREA, MLT, MAGNETIC_PATH_LENGTH])
    dataAWG = pd.read_csv(PATH_AWG, header = 0, names=[AWG, BARE_AREA, DIAMETER])

    print(" AWG: ", end = "")
    for AWG_NUM in dataAWG[AWG]:
        extra = "0" if int(AWG_NUM) < 10 else ""
        print(f"{extra}{AWG_NUM}", end = " ")
    print("")

    # Cambio de unidades
    inductancia = param.inductancia * 10**(-6)
    campoMagneticoMaximo = param.campoMagneticoMaximo * 10**(-3)

    # Resistencia maxima del alambre [Ohm]
    resistenciaCobreMaxima = param.potenciaMaximaCobre / (param.corrienteDC**2)

    # Geometrica del nucleo [cm^5]
    cotaMinimaKg = param.margenKg * 10**(-3) \
        + 10**8 * (DENSIDAD_COBRE * inductancia**2 * param.corrienteInductorMaxima**2) / (campoMagneticoMaximo**2 * resistenciaCobreMaxima * Ku) 

    # Verificando la profundidad de penetracion
    profundidadPenetracion = 7.5 / np.sqrt(10**3 * param.frecuencia)

    # Los sorteamos para que siempre el primero sea el mas chico
    indicesDeNucleos = dataNucleos[GEOMETRIC_CONSTANTE].argsort()

    for indiceNucleo in indicesDeNucleos:
        nucleo = dataNucleos.loc[indiceNucleo]
        print(f"{nucleo.at[CORE_TYPE]}:", end=" ")

        if nucleo.at[GEOMETRIC_CONSTANTE] < cotaMinimaKg:
            print(f"0{VERI_CONSTANTE_GEOMETRICA} " * len(dataAWG))
            continue

        # Entrehierro en m
        entreHierro = 10**4 * (MU_0 * inductancia * param.corrienteInductorMaxima**2) / (campoMagneticoMaximo**2 * nucleo.at[CROSS_SECTIONAL_AREA])

        # Cantidad de vueltas
        # nVueltas = np.ceil(10**4 * (inductancia * param.corrienteInductorMaxima) / (campoMagneticoMaximo * nucleo.at[CROSS_SECTIONAL_AREA]))
        nVueltas = np.ceil(np.sqrt(( inductancia * entreHierro ) / ( MU_0 * nucleo.at[CROSS_SECTIONAL_AREA] * 10**(-4) )))

        # Seccion de alambre en cm^2
        cotaSuperiorSeccionAlambre = (Ku * nucleo.at[BOBBIN_AREA]) / nVueltas

        indicesAWG = list(range(len(dataAWG)))

        for indiceAWG in indicesAWG:
            AWGElegido = dataAWG.loc[indiceAWG]

            if AWGElegido.at[BARE_AREA] * 10**(-3) > cotaSuperiorSeccionAlambre:
                print(f"0{VERI_SECCION_ALAMBRE}", end = " ")
                continue

            resultadoAWG = 0

            # Verificamos la resistencia de bobinado
            resistenciaCobre = (DENSIDAD_COBRE * nVueltas * nucleo.at[MLT]) / (AWGElegido.at[BARE_AREA] * 10**-3)
            cumpleResistenciaCobre = resistenciaCobre < resistenciaCobreMaxima

            # Verificando la densidad de corriente del alambre
            densidadDeCorriente = param.corrienteInductorMaxima / (100 * AWGElegido.at[BARE_AREA] * 10**-3)
            cumpleDensidadDeCorriente = densidadDeCorriente < 5

            # Verificando que no sature el nucleo
            campoMagnetico = (MU_0 * nVueltas * param.corrienteInductorMaxima) / (entreHierro)
            cumpleCampoMagnetico = campoMagnetico < param.campoMagneticoSaturacion * 10**(-3)

            if not cumpleResistenciaCobre:
                resultadoAWG += VERI_RESISTENCIA_COBRE

            if not cumpleDensidadDeCorriente:
                resultadoAWG += VERI_DENSIDAD_COBRE

            if not cumpleCampoMagnetico:
                resultadoAWG += VERI_CAMPO_MAG

            print(f"0{resultadoAWG}", end = " ")

        print("")

if __name__ == "__main__":
    main(obtenerParametros())