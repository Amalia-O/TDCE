import argparse
import numpy as np
import pandas as pd

PATH_NUCLEOS = "nucleos.csv"
PATH_AWG = "AWG.csv"

Ku = 0.33
DENSIDAD_COBRE = 1.724 * 10**(-6)
MU_0 = 4 * np.pi * 10**(-7)

CORE_TYPE = "coreType"
IDX_CORE_TYPE = 0
GEOMETRIC_CONSTANTE = "geometricConstant"
IDX_GEOMETRIC_CONSTANTE = 1
CROSS_SECTIONAL_AREA = "crossSectional"
IDX_CROSS_SECTIONAL_AREA = 2
BOBBIN_AREA = "bobbinArea"
IDX_BOBBIN_AREA = 3
MLT = "MLT"
IDX_MLT = 4
MAGNETIC_PATH_LENGTH = "magneticPathLength"
IDX_MAGNETIC_PATH_LENGTH = 5

AWG = "AWG"
IDX_AWG = 0
BARE_AREA = "bareArea"
IDX_BARE_AREA = 1

def obtenerParametros():
    parser = argparse.ArgumentParser(
        prog="DiseñoInductor",
        description="Forma para la cual se puede definir los parametros del inductor",
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
        "-idc", "--corrienteDC",
        type=float,
        dest="corrienteDC",
        help="Corriente en Amperes que tiene que circular constantemente",
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

# inductancia, campoMagneticoMaximo,  corrienteDC, corrienteInductorMaxima, potenciaMaximaCobre, margenKg, margenAw, margenRcu, margenDensidadCorriente
def main(param):
    # Datos de los csv
    dataNucleos = pd.read_csv(PATH_NUCLEOS, header = 0, names=[CORE_TYPE, GEOMETRIC_CONSTANTE, CROSS_SECTIONAL_AREA, BOBBIN_AREA, MLT, MAGNETIC_PATH_LENGTH])
    dataAWG = pd.read_csv(PATH_AWG, header = 0, names=[AWG, BARE_AREA])

    # Cambio de unidades
    inductancia = param.inductancia * 10**(-6)
    campoMagneticoMaximo = param.campoMagneticoMaximo * 10**(-3)

    # Resistencia maxima del alambre [Ohm]
    resistenciaCobreMaxima = param.potenciaMaximaCobre / (param.corrienteDC**2)

    # Geometrica del nucleo [cm^5]
    cotaMinimaKg = param.margenKg * 10**(-3) \
        + 10**8 * (DENSIDAD_COBRE * inductancia**2 * param.corrienteInductorMaxima**2) / (campoMagneticoMaximo**2 * resistenciaCobreMaxima * Ku) 


    # Eleccion del nucleo
    nucleosPosibles = dataNucleos.loc[dataNucleos[GEOMETRIC_CONSTANTE] > cotaMinimaKg]

    # Los sorteamos para que siempre el primero sea el mas chico
    indicesDeNucleos = nucleosPosibles.geometricConstant.argsort()

    nucleosPosibles = nucleosPosibles.to_numpy()
    for indiceNucleo in indicesDeNucleos:
        nucleo = nucleosPosibles[indiceNucleo]

        # Entrehierro en m
        entreHierro = 10**4 * (MU_0 * inductancia * param.corrienteInductorMaxima**2) / (campoMagneticoMaximo**2 * nucleo[IDX_CROSS_SECTIONAL_AREA])

        # Cantidad de vueltas
        nVueltas = np.ceil(10**4 * (inductancia * param.corrienteInductorMaxima) / (campoMagneticoMaximo * nucleo[IDX_CROSS_SECTIONAL_AREA]))

        # Seccion de alambre en cm^2 y mm^2
        cotaSuperiorSeccionAlambreCm2 = (Ku * nucleo[IDX_BOBBIN_AREA]) / nVueltas

        # Tendriamos que elegir un AWG
        AWGPosibles = dataAWG.loc[dataAWG[BARE_AREA] * 10**(-3) < cotaSuperiorSeccionAlambreCm2]

        # Los sorteamos para que siempre el primero sea el mas grande
        indicesAWG = AWGPosibles[BARE_AREA].argsort()[::-1]

        fueElegidoInductor = False

        AWGPosibles = AWGPosibles.to_numpy()
        for indiceAWG in indicesAWG:
            AWGelegido = AWGPosibles[indiceAWG]

            # Verificamos la resistencia de bobinado
            resistenciaCobre = (DENSIDAD_COBRE * nVueltas * nucleo[IDX_MLT]) / (AWGelegido[IDX_BARE_AREA] * 10**-3)

            if resistenciaCobre > resistenciaCobreMaxima:
                continue

            # Verificando la densidad de corriente del alambre
            densidadDeCorriente = param.corrienteInductorMaxima / (100 * AWGelegido[IDX_BARE_AREA] * 10**-3)

            if densidadDeCorriente > 5:
                continue

            fueElegidoInductor = True
            break

        if fueElegidoInductor:
            break

    if not fueElegidoInductor:
        print("No se pudo elegir ningún inductor, considerar cambiar algún parametro de entrada o reducir los margenes")
        return

    print("Elegido:")
    print(f"Nucleo {nucleo[IDX_CORE_TYPE]}, con AWG#{int(AWGelegido[IDX_AWG])}")
    print(f"\tEntrehierro: {(10**3 * entreHierro):.3f} mm")
    print(f"\tCantidad de vueltas: {int(nVueltas)}")
    print(f"\tResistencia de bobina: {resistenciaCobre:.3f}")
    print(f"\tDensidad de corriente: {densidadDeCorriente:.3f} A/mm^2")


if __name__ == "__main__":
    main(obtenerParametros())