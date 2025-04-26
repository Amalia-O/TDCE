import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sys

def main(argumentos):
    archivoPath = argumentos[1]
    frecuencias = pd.read_csv(
        archivoPath, names = [ "RL", "Total", "N1", "N2", "N3", "N4", "N5" ], header = 0,
        index_col = 0, dtype = np.float32 
    )

    paleta = sns.color_palette("viridis", as_cmap = False, n_colors = 6)
    paleta = sns.color_palette("husl", 6)

    datos = [ 
        { "nombre": "N1", "label": "Nodo 1" },
        { "nombre": "N2", "label": "Nodo 2" },
        { "nombre": "N3", "label": "Nodo 3" },
        { "nombre": "N4", "label": "Nodo 4" },
        { "nombre": "N5", "label": "Nodo 5" },
        { "nombre": "Total", "label": "$f_h$" },
    ]

    for indice, dato in enumerate(datos):
        stem = plt.stem(frecuencias.RL, frecuencias[dato["nombre"]], label = dato["label"], linefmt = "--")
        plt.setp(stem.baseline, color = (0, 0, 0, 0))
        plt.setp(stem.stemlines, color = (paleta[indice][0], paleta[indice][1], paleta[indice][2], 0.5))
        plt.setp(stem.markerline, color = paleta[indice])

    plt.xlabel("$R_L ~ [\Omega]$")
    plt.ylabel("$Hz$")
    plt.yscale("log")
    plt.legend()
    # plt.grid(visible = True, axis = "y", which = "both")
    plt.show()

if __name__ == "__main__":
    main(sys.argv)