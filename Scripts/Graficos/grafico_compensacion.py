import numpy as np
import matplotlib.pyplot as plt


def main():
    tabla = np.genfromtxt("Graficos/datosCompensacion/pulsoAscendiente.csv", dtype = np.float64, delimiter = ",", skip_header = 6).transpose()
    
    cantMuestras = 100
    inicio = 1500
    final = -3000

    vref = tabla[0, inicio:final:cantMuestras] / 1000
    vo = tabla[1, inicio:final:cantMuestras] / 1000

    t = list(map(lambda x: 10 * float(x) - 937, range(len(vo)))) 

    plt.plot(t, vo, label="Tensión de salida $V_0$")
    plt.plot(t, 2 * vref, label="Tensión de referencia $2V_{ref}$")

    plt.title("")
    plt.xlabel("$t$ [ms]")
    plt.ylabel("Tensión [V]");

    # plt.xticks(list(map(lambda x: 1000 * int(x) - 900, range((9 + 17) // 2))))

    plt.legend(loc = 'upper left')
    plt.show();

if __name__ == "__main__":
    main()